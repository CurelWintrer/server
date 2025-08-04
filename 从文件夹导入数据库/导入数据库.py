import tkinter as tk
from tkinter import filedialog
import os
import json
import mysql.connector
import hashlib
import logging
import traceback
from datetime import datetime

# 配置日志
logging.basicConfig(filename='json_to_mysql.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_md5(file_path):
    """计算文件的MD5哈希值"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating MD5 for {file_path}: {str(e)}")
        return None

def parse_levels(base_dir, file_path):
    """
    从文件路径解析层级结构
    返回 (First, Second, Third, Fourth, Fifth) 元组
    """
    relative_path = os.path.relpath(file_path, base_dir)
    dir_path = os.path.dirname(relative_path)
    
    levels = dir_path.split(os.sep)
    levels += [None] * (5 - len(levels))  # 填充None使长度为5
    
    return tuple(levels[:5])

def process_json_file(cursor, file_path, base_dir):
    """处理单个JSON文件并导入到数据库"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logging.error(f"JSON文件不是数组格式: {file_path}")
            return
        
        for entry in data:
            # 检查必填字段
            if 'Img_path' not in entry or 'Img_name' not in entry:
                logging.error(f"JSON条目缺少必要字段: {file_path}")
                continue
            
            img_relative_path = entry['Img_path']
            img_full_path = os.path.join(base_dir, img_relative_path)
            
            # 从路径获取层级信息
            levels = parse_levels(base_dir, img_full_path)
            
            # 计算图片MD5
            md5_val = calculate_md5(img_full_path)
            if not md5_val:
                continue
            
            # 准备数据库插入数据
            current_time = datetime.now()
            insert_data = {
                'md5': md5_val,
                'First': levels[0],
                'Second': levels[1],
                'Third': levels[2],
                'Fourth': levels[3],
                'Fifth': levels[4],
                'imgName': entry.get('Img_name'),
                'imgPath': entry['Img_path'],  # 直接使用JSON中的Img_path字段
                'chinaElementName': entry.get('China_element_name', None),
                'caption': entry.get('caption', None),
                'state': 0,
                'imageListID': None,
                'created_at': current_time,
                'updated_at': current_time
            }
            
            # 执行SQL插入
            sql = """
            INSERT INTO image (
                md5, First, Second, Third, Fourth, Fifth, 
                imgName, imgPath, chinaElementName, caption, 
                state, imageListID, created_at, updated_at
            ) VALUES (
                %(md5)s, %(First)s, %(Second)s, %(Third)s, %(Fourth)s, %(Fifth)s,
                %(imgName)s, %(imgPath)s, %(chinaElementName)s, %(caption)s,
                %(state)s, %(imageListID)s, %(created_at)s, %(updated_at)s
            )
            """
            cursor.execute(sql, insert_data)
        
        return len(data)
    
    except Exception as e:
        logging.error(f"处理文件时出错: {file_path}")
        logging.error(traceback.format_exc())
        return 0
def analyze_and_insert_titles(cursor):
    """分析image表中的标题层级关系并插入到image_title表"""
    try:
        # 首先清空标题表（如果需要保留已有数据，可以删除这部分）
        cursor.execute("TRUNCATE TABLE image_title")
        
        # 获取所有不重复的标题层级
        cursor.execute("""
            SELECT DISTINCT First, Second, Third, Fourth, Fifth 
            FROM image 
            WHERE First IS NOT NULL
            ORDER BY First, Second, Third, Fourth, Fifth
        """)
        
        title_rows = cursor.fetchall()
        
        # 用于存储已插入的标题及其ID
        title_cache = {}  # 格式: {('First', 'Second',...): id}
        
        for row in title_rows:
            First, Second, Third, Fourth, Fifth = row
            
            # 处理每一级标题
            for level in range(1, 6):
                current_level_titles = row[:level]
                
                # 如果这一级标题不存在，则跳过
                if current_level_titles[-1] is None:
                    continue
                
                # 检查是否已经处理过这个标题
                if current_level_titles in title_cache:
                    continue
                
                # 确定父级ID
                parent_id = None
                if level > 1:
                    parent_titles = current_level_titles[:-1]
                    parent_id = title_cache.get(parent_titles)
                
                # 插入当前标题
                insert_sql = """
                    INSERT INTO image_title (title, parentID, level)
                    VALUES (%s, %s, %s)
                """
                current_title = current_level_titles[-1]
                cursor.execute(insert_sql, (current_title, parent_id, level))
                
                # 获取新插入的ID并缓存
                new_id = cursor.lastrowid
                title_cache[current_level_titles] = new_id
        
        return len(title_cache)
    
    except Exception as e:
        logging.error(f"分析标题层级关系时出错: {str(e)}")
        logging.error(traceback.format_exc())
        return 0

def main():
    # 选择文件夹
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    base_dir = filedialog.askdirectory(title="选择包含JSON文件的文件夹")
    
    if not base_dir:
        print("未选择文件夹，程序退出")
        return
    
    print(f"已选择文件夹: {base_dir}")
    
    # 数据库连接
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="yjz147",
            database="test"
        )
        cursor = conn.cursor()
        print("数据库连接成功")
    except Exception as e:
        logging.error(f"数据库连接失败: {str(e)}")
        print("数据库连接失败，请检查连接参数")
        return
    
    # 遍历文件夹并处理JSON文件
    file_count = 0
    entry_count = 0
    
    for root_dir, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.json'):
                json_path = os.path.join(root_dir, file)
                print(f"处理文件中: {json_path}")
                
                processed = process_json_file(cursor, json_path, base_dir)
                if processed:
                    entry_count += processed
                    file_count += 1
    
    # 分析并插入标题层级关系
    print("\n分析标题层级关系...")
    title_count = analyze_and_insert_titles(cursor)
    print(f"成功插入 {title_count} 条标题记录")
    
    # 提交事务并关闭连接
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n处理完成!")
    print(f"成功处理 {file_count} 个JSON文件")
    print(f"导入 {entry_count} 条记录到image表")
    print(f"导入 {title_count} 条记录到image_title表")

if __name__ == "__main__":
    main()