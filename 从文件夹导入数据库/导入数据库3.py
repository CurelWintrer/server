import os
import tkinter as tk
from tkinter import filedialog
import mysql.connector
from mysql.connector import Error
import hashlib

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yjz147',
    'database': 'test'
}

# 支持的图片扩展名
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff', '.webp'}

def ensure_trailing_slash(path):
    """确保路径以分隔符结尾，并转换为斜杠格式"""
    path = path.replace('\\', '/')  # 将反斜杠转换为正斜杠
    if not path.endswith('/'):
        path += '/'
    return path

def normalize_path(path):
    """将路径统一转换为斜杠格式"""
    return path.replace('\\', '/')

def calculate_md5(file_path, chunk_size=8192):
    """计算文件的MD5值"""
    md5_hash = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except Exception as e:
        print(f"计算MD5时出错: {file_path} - {str(e)}")
        return None

def main():
    # 创建Tkinter根窗口（隐藏）
    root = tk.Tk()
    root.withdraw()
    
    # 打开文件夹选择对话框
    print("请选择图片文件夹...")
    folder_path = filedialog.askdirectory(title="选择图片文件夹")
    if not folder_path:
        print("未选择文件夹。退出程序。")
        return
    
    # 确保路径以斜杠结尾并统一格式
    base_folder = ensure_trailing_slash(folder_path)
    
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 准备缓存结构: {(父节点ID, 标题): 节点ID}
        cursor.execute("SELECT imageTitleID, parentID, title FROM image_title")
        node_cache = {}
        for (node_id, parent_id, title) in cursor:
            # 注意: None值用0表示键，避免类型错误
            key = (parent_id if parent_id is not None else 0, title)
            node_cache[key] = node_id
        
        # 计数器
        img_count = 0
        processed_count = 0
        skipped_count = 0
        
        # 遍历文件夹收集图片文件
        for root_dir, _, files in os.walk(folder_path):
            for filename in files:
                full_path = os.path.join(root_dir, filename)
                _, ext = os.path.splitext(filename)
                
                # 只处理图片文件
                if ext.lower() not in IMAGE_EXTENSIONS:
                    continue
                
                img_count += 1
                # 每处理10个文件打印一次进度
                if img_count % 10 == 0:
                    print(f"正在处理第 {img_count} 个图片...")
                
                # 计算MD5值
                md5_val = calculate_md5(full_path)
                if not md5_val:
                    skipped_count += 1
                    continue  # 如果计算失败，跳过此文件
                    
                # 计算相对路径并转换为斜杠格式
                rel_path = os.path.relpath(full_path, folder_path)
                rel_path = normalize_path(rel_path)
                
                # 拆分路径部分
                parts = rel_path.split('/')
                dirs = parts[:-1]  # 目录部分
                img_name = parts[-1]  # 文件名
                
                # 获取最多5个路径层级
                path_parts = dirs[:5]
                while len(path_parts) < 5:
                    path_parts.append(None)
                first, second, third, fourth, fifth = path_parts
                
                # 插入图片路径层级节点
                parent_id = None
                current_level = 1
                for title in dirs:  # 处理所有层级
                    # 特殊处理顶级节点（parent_id为None）
                    cache_key = (parent_id if parent_id is not None else 0, title)
                    
                    if cache_key in node_cache:
                        node_id = node_cache[cache_key]
                    else:
                        # 插入新节点
                        insert_query = """
                        INSERT INTO image_title (title, parentID, level)
                        VALUES (%s, %s, %s)
                        """
                        cursor.execute(insert_query, (title, parent_id, current_level))
                        node_id = cursor.lastrowid
                        # 更新缓存
                        node_cache[cache_key] = node_id
                    
                    # 为下一层准备
                    parent_id = node_id
                    current_level += 1
                
                # 插入图片记录（包含MD5值）
                img_query = """
                INSERT INTO image 
                  (md5, First, Second, Third, Fourth, Fifth, imgName, imgPath)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(img_query, 
                              (md5_val, first, second, third, fourth, fifth, img_name, rel_path))
                
                processed_count += 1
                
        # 提交事务
        conn.commit()
        print(f"\n操作成功完成！")
        print(f"- 共发现 {img_count} 个图片文件")
        print(f"- 成功处理 {processed_count} 个图片")
        if skipped_count:
            print(f"- 跳过 {skipped_count} 个无法计算的图片")
        
    except Error as e:
        print(f"数据库错误: {e}")
        if conn.is_connected():
            conn.rollback()
    except Exception as e:
        print(f"程序错误: {e}")
        if conn.is_connected():
            conn.rollback()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    main()