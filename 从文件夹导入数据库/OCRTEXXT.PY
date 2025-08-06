import os
import pytesseract
from PIL import Image
from tkinter import filedialog, Tk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import shutil


# 选择文件夹
def select_folder():
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    folder_path = filedialog.askdirectory()  # 弹出文件夹选择框
    return folder_path


# 对图片进行OCR识别
def ocr_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


# 计算文字相似度
def group_images_by_text_similarity(image_paths):
    texts = []
    for path in image_paths:
        text = ocr_image(path)
        texts.append(text)

    # 使用TF-IDF进行文本特征提取
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)

    # 计算图片之间的余弦相似度
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 根据相似度阈值分组图片
    groups = []
    visited = [False] * len(image_paths)
    for i in range(len(image_paths)):
        if visited[i]:
            continue
        group = [image_paths[i]]
        visited[i] = True
        for j in range(i + 1, len(image_paths)):
            if not visited[j] and cosine_sim[i][j] > 0.8:  # 假设相似度大于0.8认为是相似的
                group.append(image_paths[j])
                visited[j] = True
        groups.append(group)
    
    return groups


# 将分组结果保存到文件夹中
def save_grouped_images(groups, base_folder):
    for idx, group in enumerate(groups):
        group_folder = os.path.join(base_folder, f"group_{idx + 1}")
        os.makedirs(group_folder, exist_ok=True)
        for img_path in group:
            shutil.copy(img_path, group_folder)
        print(f"Group {idx + 1} saved at {group_folder}")


if __name__ == "__main__":
    folder_path = select_folder()
    
    # 获取文件夹内的所有图片
    image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    # 按文字相似度分组
    groups = group_images_by_text_similarity(image_paths)
    
    # 输出结果并保存分组后的图片
    save_grouped_images(groups, folder_path)
