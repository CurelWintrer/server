import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torchvision.transforms as T
from torchvision import models
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import torch.nn as nn  # 添

# 加载 CLIP 模型和 ResNet 模型
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
resnet_model = models.resnet50(pretrained=True)
resnet_model.eval()

def extract_clip_features(image_path):
    image = Image.open(image_path)
    inputs = clip_processor(images=image, return_tensors="pt", padding=True)  # 这里没有 text 参数
    with torch.no_grad():
        features = clip_model.get_image_features(**inputs)
    return features.squeeze().numpy()  # 返回一维数组


def extract_resnet_features(image_path):
    image = Image.open(image_path).convert("RGB")
    transform = T.Compose([T.Resize(256), T.CenterCrop(224), T.ToTensor(), T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    image = transform(image).unsqueeze(0)
    
    # 获取ResNet倒数第二层的特征
    # ResNet的倒数第二层是avgpool（池化层）之前的全连接层输出
    with torch.no_grad():
        # 通过去掉最后的全连接层，得到倒数第二层特征
        resnet_features = nn.Sequential(*list(resnet_model.children())[:-1])(image)
    
    return resnet_features.squeeze().numpy()  # 返回一维数组

def calculate_similarity(features1, features2):
    return cosine_similarity(features1.reshape(1, -1), features2.reshape(1, -1))[0][0]

def find_similar_images(image_folder):
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    clip_features = []
    resnet_features = []
    
    for path in image_paths:
        clip_features.append(extract_clip_features(path))
        resnet_features.append(extract_resnet_features(path))

    similarity_groups = []
    for i in range(len(image_paths)):
        group = [image_paths[i]]
        for j in range(i + 1, len(image_paths)):
            clip_similarity = calculate_similarity(clip_features[i], clip_features[j])
            resnet_similarity = calculate_similarity(resnet_features[i], resnet_features[j])
            if clip_similarity > 0.85 and resnet_similarity > 0.85:  # 设定相似度阈值
                group.append(image_paths[j])
        # 去除重复项
        similarity_groups.append(list(set(group)))
    
    return similarity_groups

if __name__ == "__main__":
    import sys
    folder_path = sys.argv[1]  # 从命令行传递文件夹路径
    groups = find_similar_images(folder_path)
    for group in groups:
        print("Group of similar images:", group)
