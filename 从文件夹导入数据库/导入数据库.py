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
    
    # 提交事务并关闭连接
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n处理完成!")
    print(f"成功处理 {file_count} 个JSON文件")
    print(f"导入 {entry_count} 条记录到数据库")

if __name__ == "__main__":
    main()