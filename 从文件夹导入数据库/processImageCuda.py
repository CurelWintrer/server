import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torchvision.transforms as T
from torchvision import models
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import torch.nn as nn
from tqdm import tqdm  # ✅ 导入进度条库

# 选择设备（GPU优先）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 加载 CLIP 模型和 ResNet 模型
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
    return features.squeeze().cpu().numpy()  # 返回一维数组

def extract_resnet_features(image_path):
    image = Image.open(image_path).convert("RGB")
    image = resnet_transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        features = nn.Sequential(*list(resnet_model.children())[:-1])(image)
    return features.squeeze().cpu().numpy()  # 返回一维数组

def calculate_similarity(features1, features2):
    return cosine_similarity(features1.reshape(1, -1), features2.reshape(1, -1))[0][0]

def find_similar_images(image_folder):
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder)
                   if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    
    clip_features = []
    resnet_features = []

    print("Extracting features...")
    for path in tqdm(image_paths, desc="Feature Extraction", unit="image"):
        clip_features.append(extract_clip_features(path))
        resnet_features.append(extract_resnet_features(path))

    similarity_groups = []
    visited = set()

    print("Calculating similarities...")
    for i in tqdm(range(len(image_paths)), desc="Similarity Comparison", unit="image"):
        if i in visited:
            continue
        group = [image_paths[i]]
        visited.add(i)
        for j in range(i + 1, len(image_paths)):
            if j in visited:
                continue
            clip_sim = calculate_similarity(clip_features[i], clip_features[j])
            resnet_sim = calculate_similarity(resnet_features[i], resnet_features[j])
            if clip_sim > 0.85 and resnet_sim > 0.85:
                group.append(image_paths[j])
                visited.add(j)
        similarity_groups.append(group)

    return similarity_groups

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python find_similar_images_gpu.py <image_folder_path>")
        sys.exit(1)
    folder_path = sys.argv[1]
    groups = find_similar_images(folder_path)
    print("\n=== Similar Image Groups ===")
    for idx, group in enumerate(groups):
        if len(group) > 1:
            print(f"\nGroup {idx+1}:")
            for img in group:
                print("  ", img)
