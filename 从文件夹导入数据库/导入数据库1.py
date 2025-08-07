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

# 全局标题缓存 {标题路径元组: imageTitleID}
title_cache = {}

def get_or_insert_title(cursor, title_path, level):
    """
    获取或插入标题记录，返回imageTitleID
    :param cursor: 数据库游标
    :param title_path: 标题路径元组 (First, Second, Third, Fourth, Fifth)
    :param level: 当前层级
    :return: imageTitleID
    """
    # 如果层级无效或标题为空，返回None
    if level < 1 or title_path[level-1] is None:
        return None
    
    # 检查缓存
    cache_key = title_path[:level]
    if cache_key in title_cache:
        return title_cache[cache_key]
    
    # 获取父级ID
    parent_id = None
    if level > 1:
        parent_id = get_or_insert_title(cursor, title_path, level-1)
    
    # 插入当前标题
    title = title_path[level-1]
    sql = """
        INSERT INTO image_title (title, parentID, level)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (title, parent_id, level))
    
    # 获取新标题ID并更新缓存
    new_id = cursor.lastrowid
    title_cache[cache_key] = new_id
    return new_id

def parse_levels(base_dir, file_path):
    """
    从文件路径解析层级结构
    返回包含层级名称的元组
    """
    relative_path = os.path.relpath(file_path, base_dir)
    dir_path = os.path.dirname(relative_path)
    
    levels = dir_path.split(os.sep)
    levels += [None] * (5 - len(levels))  # 填充None使长度为5
    
    return tuple(levels[:5])

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

def process_json_file(cursor, file_path, base_dir):
    """处理单个JSON文件并导入到数据库"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logging.error(f"JSON文件不是数组格式: {file_path}")
            return 0
        
        entry_count = 0
        for entry in data:
            # 检查必填字段
            if 'Img_path' not in entry or 'Img_name' not in entry:
                logging.error(f"JSON条目缺少必要字段: {file_path}")
                continue
            
            img_relative_path = entry['Img_path']
            img_full_path = os.path.join(base_dir, img_relative_path)
            
            # 获取层级名称
            levels = parse_levels(base_dir, img_full_path)
            
            # 为每个层级创建标题记录并获取ID
            level_ids = []
            for i in range(1, 6):
                level_id = get_or_insert_title(cursor, levels, i)
                level_ids.append(level_id)
            
            # 计算图片MD5
            md5_val = calculate_md5(img_full_path)
            if not md5_val:
                continue
            
            # 准备数据库插入数据
            current_time = datetime.now()
            insert_data = {
                'md5': md5_val,
                'First': level_ids[0],
                'Second': level_ids[1],
                'Third': level_ids[2],
                'Fourth': level_ids[3],
                'Fifth': level_ids[4],
                'imgName': entry.get('Img_name'),
                'imgPath': entry['Img_path'],
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
            entry_count += 1
        
        return entry_count
    
    except Exception as e:
        logging.error(f"处理文件时出错: {file_path}")
        logging.error(traceback.format_exc())
        return 0

def main():
    global title_cache
    
    # 选择文件夹
    root = tk.Tk()
    root.withdraw()
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
    
    # 重置标题缓存
    title_cache = {}
    
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
    
    # 提交事务并关闭连接
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n处理完成!")
    print(f"成功处理 {file_count} 个JSON文件")
    print(f"导入 {entry_count} 条记录到image表")
    print(f"创建 {len(title_cache)} 个标题记录")

if __name__ == "__main__":
    main()