import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torchvision.transforms as T
from torchvision import models
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import torch.nn as nn
from tqdm import tqdm

# 选择设备（GPU优先）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 加载模型
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
resnet_model = models.resnet50(pretrained=True).to(device)
resnet_model.eval()

# 图像预处理
resnet_transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225])
])

def extract_clip_features(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = clip_processor(images=image, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        features = clip_model.get_image_features(**inputs)
    return features.squeeze().cpu().numpy()

def extract_resnet_features(image_path):
    image = Image.open(image_path).convert("RGB")
    image = resnet_transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        features = nn.Sequential(*list(resnet_model.children())[:-1])(image)
    return features.squeeze().cpu().numpy()

def calculate_similarity(features1, features2):
    return cosine_similarity(features1.reshape(1, -1), features2.reshape(1, -1))[0][0]

def find_similar_images_to_query(query_image_path, folder_path, threshold=0.85):
    # 提取查询图像特征
    print("Extracting features for query image...")
    query_clip = extract_clip_features(query_image_path)
    query_resnet = extract_resnet_features(query_image_path)

    # 搜索文件夹中所有图片
    image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                   if f.lower().endswith(('jpg', 'jpeg', 'png')) and os.path.join(folder_path, f) != query_image_path]

    similar_images = []

    print("Comparing to folder images...")
    for path in tqdm(image_paths, desc="Comparing", unit="image"):
        try:
            clip_feat = extract_clip_features(path)
            resnet_feat = extract_resnet_features(path)
            clip_sim = calculate_similarity(query_clip, clip_feat)
            resnet_sim = calculate_similarity(query_resnet, resnet_feat)
            if clip_sim > threshold and resnet_sim > threshold:
                similar_images.append((path, clip_sim, resnet_sim))
        except Exception as e:
            print(f"Error processing {path}: {e}")

    return similar_images

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python compare_single_image.py <query_image_path> <folder_path>")
        sys.exit(1)

    query_image = sys.argv[1]
    folder = sys.argv[2]

    results = find_similar_images_to_query(query_image, folder)

    print(f"\n=== Images similar to '{query_image}' ===")
    if results:
        for path, clip_sim, resnet_sim in sorted(results, key=lambda x: (clip_sim + resnet_sim) / 2, reverse=True):
            print(f"{path}\n  CLIP similarity: {clip_sim:.3f}  |  ResNet similarity: {resnet_sim:.3f}\n")
    else:
        print("No similar images found.")
