import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torchvision.transforms as T
from torchvision import models
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import os
import torch.nn as nn
from collections import defaultdict
import imagehash
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog, simpledialog
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"D:\安装包\Tesseract-OCR\tesseract.exe"
import difflib

# ------------------------------ 模型加载 ------------------------------
try:
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16", local_files_only=True)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16", local_files_only=True)
except Exception as e:
    print("Warning: CLIP 模型加载失败，将尝试在线下载", e)
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")

try:
    resnet_model = models.resnet50(pretrained=True)
except Exception as e:
    print("Warning: ResNet50 模型加载失败，使用无预训练模型", e)
    resnet_model = models.resnet50(pretrained=False)
resnet_model.eval()

# ------------------------------ 特征提取 ------------------------------
def extract_clip_features(image):
    inputs = clip_processor(images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        features = clip_model.get_image_features(**inputs)
    return features.squeeze().cpu().numpy()

def extract_resnet_features(image):
    transform = T.Compose([
        T.Resize(256), T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        features = nn.Sequential(*list(resnet_model.children())[:-1])(image)
    return features.squeeze().cpu().numpy()

# ------------------------------ 哈希过滤 ------------------------------
def hash_check(path1, path2, phash_threshold):
    img1, img2 = Image.open(path1), Image.open(path2)
    h1, h2 = imagehash.phash(img1), imagehash.phash(img2)
    diff = abs(h1 - h2)
    print(f"Hash 距离 {os.path.basename(path1)} vs {os.path.basename(path2)}: {diff}")
    return diff <= phash_threshold

# ------------------------------ OCR 文本相似度 ------------------------------
def text_similarity(img1, img2):
    try:
        text1 = pytesseract.image_to_string(img1, lang='chi_sim')
        text2 = pytesseract.image_to_string(img2, lang='chi_sim')
        ratio = difflib.SequenceMatcher(None, text1, text2).ratio()
        return ratio
    except Exception as e:
        print("OCR 识别失败:", e)
        return 0.0

# ------------------------------ 配对比较函数 ------------------------------
def compare_pair(path1, path2, features_dict, clip_threshold, resnet_threshold, phash_threshold, text_similarity_threshold):
    if not hash_check(path1, path2, phash_threshold): return None
    clip_sim = cosine_similarity(features_dict[path1]["clip"], features_dict[path2]["clip"])[0][0]
    resnet_sim = cosine_similarity(features_dict[path1]["resnet"], features_dict[path2]["resnet"])[0][0]
    if clip_sim > clip_threshold and resnet_sim > resnet_threshold:
        img1 = Image.open(path1).convert("RGB")
        img2 = Image.open(path2).convert("RGB")
        sim_text = text_similarity(img1, img2)
        if sim_text < text_similarity_threshold:
          return None  #  OCR 也必须满足
        print(f"  🔤 OCR 文本相似: {os.path.basename(path1)} vs {os.path.basename(path2)} -> 相似度 {sim_text:.2%}")
        return (path2, clip_sim, resnet_sim, sim_text)
    return None

# ------------------------------ 主函数 ------------------------------
def find_similar_images(image_folder, clip_threshold=0.9, resnet_threshold=0.9, min_group_size=2, phash_threshold=30, text_similarity_threshold=0.8, cluster_threshold=200):
    image_paths = [
        os.path.join(image_folder, f)
        for f in os.listdir(image_folder)
        if f.lower().endswith(('jpg','jpeg','png'))
    ]
    pil_images = [Image.open(p).convert("RGB") for p in image_paths]

    inputs = clip_processor(images=pil_images, return_tensors="pt", padding=True)
    with torch.no_grad():
        clip_feats = clip_model.get_image_features(**inputs).cpu().numpy()
    clip_features = {p: feat for p, feat in zip(image_paths, clip_feats)}

    clip_matrix = np.array([clip_features[p] for p in image_paths])
    if len(image_paths) > cluster_threshold:
        print("进行预聚类...")
        reduced = PCA(n_components=50).fit_transform(clip_matrix)
        labels = KMeans(n_clusters=min(len(image_paths) // 20, 50), random_state=42).fit_predict(reduced)
        image_paths = [p for _, p in sorted(zip(labels, image_paths))]

    transform = T.Compose([
        T.Resize(256), T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    batch_tensor = torch.stack([transform(img) for img in pil_images])
    with torch.no_grad():
        resnet_feats = nn.Sequential(*list(resnet_model.children())[:-1])(batch_tensor)
    resnet_features = {p: feat.squeeze().cpu().numpy() for p, feat in zip(image_paths, resnet_feats)}

    features_dict = {
        p: {
            "clip": clip_features[p].reshape(1, -1),
            "resnet": resnet_features[p].reshape(1, -1)
        } for p in image_paths
    }

    groups, visited, similarity_scores = [], set(), []
    thread_count = simpledialog.askinteger("线程数设置", "请输入线程数（推荐8~16）:", initialvalue=8, minvalue=1, maxvalue=64)

    for i, path1 in enumerate(image_paths):
        if path1 in visited: continue
        group = [path1]
        visited.add(path1)

        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(compare_pair, path1, path2, features_dict, clip_threshold, resnet_threshold, phash_threshold, text_similarity_threshold)
                       for path2 in image_paths[i+1:] if path2 not in visited]
        for future in futures:
            result = future.result()
            if result:
                path2, clip_sim, resnet_sim, sim_text = result
                similarity_scores.append({
                    'img1': os.path.basename(path1),
                    'img2': os.path.basename(path2),
                    'clip': round(clip_sim * 100, 2),
                    'resnet': round(resnet_sim * 100, 2),
                    'text': round(sim_text * 100, 2)  # ✅ 新增
                })
                print(f"  ↳ clip={clip_sim:.2%}, resnet={resnet_sim:.2%}, text={sim_text:.2%}")
                group.append(path2)
                visited.add(path2)

        if len(group) >= min_group_size:
            groups.append(sorted(group))

    return groups, similarity_scores

# ------------------------------ 运行入口 ------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="请选择图片文件夹")
    if not folder:
        print("未选择文件夹，程序退出。")
        exit(1)

    phash_threshold = 30
    clip_threshold = 0.85
    resnet_threshold = 0.85
    text_similarity_threshold = 0.7
    cluster_threshold = 200

    groups, scores = find_similar_images(
        folder,
        clip_threshold=clip_threshold,
        resnet_threshold=resnet_threshold,
        min_group_size=2,
        phash_threshold=phash_threshold,
        text_similarity_threshold=text_similarity_threshold,
        cluster_threshold=cluster_threshold
    )

    print(f"在 '{folder}' 中找到 {len(groups)} 个相似图片组:")
    for item in scores:
        print(f"{item['img1']} vs {item['img2']} -> clip: {item['clip']}%, resnet: {item['resnet']}%, text: {item['text']}%")
    for i, group in enumerate(groups):
        print(f"\n相似组 #{i+1} (共 {len(group)} 张图片):")
        for img_path in group:
            print(f"  - {os.path.basename(img_path)}")
