import os
import json
import hashlib
import shutil
from pathlib import Path
import base64
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tkinter import filedialog, Tk

# --- 固定配置区 ---
SHUBIAOBIAO_API_KEY = 'sk-D6lEXIuoNQ1aK6OWf0WD5jwKkhabovIyfxkHYVKPRqveGdj4'  # API Key
API_URL = "https://api.shubiaobiao.com/v1/chat/completions"                 # API 地址
API_MODEL = "gemini-2.5-pro"                                              # 使用模型
TARGET_ROOT_FOLDER = "output_result0724"                                  # 要处理的根文件夹
# --- 配置区结束 ---


def calculate_md5(file_path):
    """计算文件 MD5，用于图片重命名（可选逻辑）"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def encode_image_to_base64(image_path):
    """将图片转 Base64，用于 API 调用"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except IOError as e:
        print(f"  - 错误: 读取图片 {image_path} 失败: {e}")
        return None


def call_shubiaobiao_api(image_base64, image_path, chinese_element_name, folder_categories):
    """调用数标标 API 生成 caption，使用当前提示词"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SHUBIAOBIAO_API_KEY}"
    }

    # 拼接 Prompt（可手动修改的提示词）
    folder_context_line = f"为了提供更精确的上下文，这张图片位于以下文件夹分类中：'{folder_categories}'。\n" if folder_categories else ""
    prompt_text = (
        f"你是一个专业的中国文化元素分析师。你的任务是为一张关于“{chinese_element_name}”的图片撰写一段符合特定结构和风格的详细描述，并以严格的JSON格式返回。\n"
        f"这张图片的上下文主题是：“{chinese_element_name}”。\n"
        f"{folder_context_line}\n"
        "请严格遵循以下步骤和规则：\n"
        "1.  **第一步：撰写详细描述**。描述文本必须严格遵循“开篇点题句 + 分写内容 + 结尾总写句”的结构。\n"
        f"    a. **开篇点题**: 描述的第一个句子必须是‘这是和{chinese_element_name}的同义转写’和‘{chinese_element_name}’尽量差不多的必须直接点明主题‘{chinese_element_name}’的简洁明了的句子。\n"
        "       - **特别规则**:第一句话不使用逗号顿号及“/”斜杠等一句话分开多个内容描写而是简洁明了的一句话。需要‘{chinese_element_name}内容的“/”前面的大类带上。\n" 
        "       - **特别规则**:第一句话‘{chinese_element_name}内容的“/”前面如果是成语、谚语、歇后语需要带上‘{chinese_element_name}’的原内容可以用双引号括起来点题。\n"
        "       - **特别规则**:第一句话‘{chinese_element_name}内容的“/”前面如果是诗词类、古典文学类并且有书名号“《》”需要带上‘{chinese_element_name}’的原内容可以用它原来的书名号括起来点题。\n"
        "       - **特别规则**:第一句话‘{chinese_element_name}内容的“/”前面如果是历史故事、神话故事类需要带上‘{chinese_element_name}’的原内容或者同义内容可以用双引号括起来点题\n"
        "       - **第一句话样例1**：这是xxxx（作品名称）的部分对应作品篆体细分的图片。\n"
        "       - **第一句话样例2**：这是xxxx（画作类别）画作名称的图片。\n"
        "       - **第一句话样例3**：图中展示的是xxxx（实体名）的图片。\n"
        "       - **第一句话样例4**：图中展示的是xxxx（非实体）的场景。\n"  
        "    b. **分写内容 (主体描述)**: 基于图片内容，客观详细地描述元素的外观、形态、颜色、纹理、材质、工艺等视觉细节。严格符合图中可视信息。针对不同类别，从不同维度分写。\n"
        "       - **特别规则**：如果图片内容为**书法类**和**诗词类**这种作品图有几排几列的，如能数清字数，必须用“横排X列，竖排X行，共XX字”这样的格式来描述图片主体。\n"
        "    c. **结尾总写 (背景补充)**: 在描述的末尾也必须是一个句子同样不使用逗号顿号及“/”斜杠等一句话分开多个内容描写的形式。对内容进行概括或延展，补充关于该元素的背景知识，如历史、文化寓意等客观信息。通常以“展现出……的独特韵味与……”或“尽显……的……”等句式，结尾句是为了升华主题‘{chinese_element_name}’到一句简洁到不使用逗号顿号的话语。\n"
        "    d. **其他重要规则**:\n"
        "        - **内容要求**: 总字数不少于30字。无多字、漏字、错别字，语义完整；标点符号使用中文符号，且符合中文习惯及不能有中文语法错误问题。\n"
        "        - **专业语气**: 必须使用客观、中立的百科式语言，无任何主观评价或情感词汇。文本中必须包含中国具体元素的名称，如服饰标明是满族服饰，建筑标明地标名称等。\n"
        "        - **描述焦点**: 精准描述图片核心元素，避免范围扩大化。例如，如果图片是宫门，就只描述宫门，而不是整个宫殿。\n"
        "        - **搜索信息**: 鼓励上网搜索这张图片后，结合搜索得到的结果来完善描述。\n"
        "        - **段落格式**: 必须只有一段文字，不得换行分段。\n\n"
        "2.  **第二步：格式化输出**。你的最终输出必须是一个单一的、不包含任何额外解释文本的JSON对象，格式如下：\n"
        "    ```json\n"
        "    {\n"
        "      \"caption\": \"此处填写你撰写的详细描述\"\n"
        "    }\n"
        "    ```\n\n"
        "--- 优秀描述样例 (请严格模仿其结构和语言风格) ---\n"
        "样例1: \"图中展示的是毛公鼎内部分的大篆铭文。背景为棕褐色，铭文文字呈浅米色，铭文以大篆字体书写，字形大小错落有致，笔画线条或曲或直、古朴浑厚，该图横排五列，竖排七行，共三十五个字。展现出西周时期文字的独特韵味与书法艺术。\"\n"
        "样例2: \"这是泉州提线木偶表演的场景。背景为简洁的深色幕布，男性木偶双臂张开正在表演，身着带有金色配饰和蓝色部件、布满复杂花纹的红色传统戏服，头戴精致帽子，长须垂胸，表情威严。展现出传统木偶戏的独特韵味与表演风采。\"\n"
        "样例3: \"这是宋代传统服饰褙子的图片。褙子整体呈长袍样式，颜色为浅褐色，边缘饰有深色花纹。对襟设计，衣袖宽阔，面料纹理清晰。展现出传统服饰文化的独特韵味与历史底蕴。\"\n"
        "样例4: \"这是戏曲京剧中旦角的图片。背景为绘制着艳丽牡丹与翠绿枝叶的传统布景，人物身着华丽的传统戏服，头戴精致凤冠，面部妆容精致，双手轻握白色水袖于身前。展现出京剧艺术的古典韵味与独特美感。\"\n"
        "样例5: \"这是演练少林功夫的场景。背景为红砖墙与古建筑，人物身着传统练功服，两位僧人跃起施展武术侧踢，后排数位僧人身着灰色僧袍，整齐盘腿静坐。展现出少林武术的独特韵味与实战风采。\"\n"
        "样例6: \"这是人物画《朱佛女画像轴》的图片。画作背景为暖棕色调，画中她头戴华丽凤冠，身着大红服饰，饰有精美龙纹等图案，尽显尊贵，手中拿着白色的笏板，端坐在椅子上。展现出明代贵族女性服饰的独特韵味与礼仪规制。\"\n"
        "样例7: \"这是毛公鼎内部分大篆铭文的图片。背景为棕褐色，铭文文字呈浅米色，铭文以大篆字体书写，字形大小错落有致，笔画线条或曲或直、古朴浑厚，该图横排五列，竖排七行，共三十五个字。展现出西周时期文字的独特韵味与书法艺术。\"\n"
        "样例8: \"图片中展示的是武英殿的宫门。该宫门建筑屋顶为黄色琉璃瓦，殿身红墙彩饰，栏杆白石雕就、造型规整。宫门气势恢宏庄严，尽显中式古建筑的典雅厚重。\"\n\n"
        "现在，请开始分析这张图片并按要求返回JSON结果。"
    )

    # 构造 API 请求体
    image_ext = os.path.splitext(image_path)[1].lower()
    mime_type = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png'}.get(image_ext, 'image/jpeg')
    data_url = f"data:{mime_type};base64,{image_base64}"

    payload = {
        "model": API_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ],
        "response_format": {"type": "json_object"}
    }

    # 重试逻辑
    retries = 3
    for attempt in range(retries):
        try:
            print(f"  - 调用 API 生成 {chinese_element_name} 描述 (第 {attempt+1} 次尝试)...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
            response.raise_for_status()  # 触发 HTTP 错误异常

            # 解析响应
            response_data = response.json()
            content_str = response_data['choices'][0]['message']['content'].strip()
            
            # 清理 JSON 格式（去掉代码块标记）
            if content_str.startswith("```json"):
                content_str = content_str[7:-3].strip()  # 截取中间内容
            elif content_str.startswith("```"):
                content_str = content_str[3:-3].strip()

            # 解析最终 caption
            result_json = json.loads(content_str)
            return result_json.get("caption", "AI 未生成有效描述")

        except requests.exceptions.RequestException as e:
            print(f"  - API 请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"  - 解析 API 响应失败: {e}，响应内容: {content_str}")

        if attempt < retries - 1:
            print("  - 等待 2 秒后重试...")
            time.sleep(2)

    return "错误: 多次调用 API 失败，无法生成描述"


def process_single_image(image_path, json_path, output_dir, folder_categories, missing_files):
    """处理单张图片：读取原 JSON、调用 API 更新 caption、覆盖输出新 JSON"""
    try:
        # 1. 读取原始 JSON 数据
        with open(json_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)

        # 2. 提取关键信息
        # 优先使用 China_element_name，如果不存在则使用 chinese_element_name
        chinese_element_name = original_data.get('China_element_name', original_data.get('chinese_element_name', '未知元素'))
        img_path = original_data.get('Img_path', '')
        img_name = original_data.get('Img_name', '')
        
        # 3. 检查 JSON 中的路径和文件名是否与实际文件一致
        expected_img_name = os.path.basename(image_path)
        expected_img_path = os.path.dirname(os.path.relpath(image_path, TARGET_ROOT_FOLDER))
        
        # 3.1 检查 Img_name 是否匹配
        if img_name and img_name != expected_img_name:
            missing_files['json_img_name_mismatch'].append({
                'json_path': json_path,
                'expected': expected_img_name,
                'actual': img_name
            })
        
        # 3.2 检查 Img_path 是否匹配（相对路径）
        if img_path and img_path != expected_img_path:
            missing_files['json_img_path_mismatch'].append({
                'json_path': json_path,
                'expected': expected_img_path,
                'actual': img_path
            })

        # 4. 调用 API 生成新 caption（使用当前提示词）
        image_base64 = encode_image_to_base64(image_path)
        if not image_base64:
            return None  # 图片编码失败，跳过

        new_caption = call_shubiaobiao_api(image_base64, image_path, chinese_element_name, folder_categories)

        # 5. 构造新 JSON（保留所有字段，只更新 caption）
        new_data = original_data.copy()
        new_data['caption'] = new_caption  # 覆盖 caption 字段

        # 6. 确定输出路径：与源文件夹结构完全一致（覆盖模式）
        relative_path = os.path.relpath(os.path.dirname(json_path), TARGET_ROOT_FOLDER)
        output_folder = os.path.join(output_dir, relative_path)
        os.makedirs(output_folder, exist_ok=True)  # 确保输出目录存在

        # 7. 写入新 JSON（直接覆盖同名文件）
        output_json_path = os.path.join(output_folder, os.path.basename(json_path))
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)

        # 8. 同步复制图片（如果不存在则复制，存在则跳过）
        output_image_path = os.path.join(output_folder, os.path.basename(image_path))
        if not os.path.exists(output_image_path):
            shutil.copy2(image_path, output_image_path)
            print(f"  - 已复制图片: {os.path.basename(image_path)} → {output_folder}")
        # 图片已存在则不重复复制，实现增量覆盖

        print(f"  - 成功处理并覆盖: {json_path} → 输出至 {output_json_path}")
        return new_data

    except Exception as e:
        print(f"  - 处理 {json_path} 失败: {e}")
        missing_files['processing_errors'].append({
            'json_path': json_path,
            'error': str(e)
        })
        return None


def print_missing_files_summary(missing_files):
    """打印缺失文件的汇总信息"""
    if not any(missing_files.values()):
        print("\n✅ 所有图片和 JSON 文件匹配正常，没有发现缺失或不匹配的情况")
        return

    print("\n⚠️ 发现以下文件不匹配情况：")
    
    if missing_files['json_img_name_mismatch']:
        print(f"\n 1. JSON 中的 Img_name 与实际图片名称不匹配（共 {len(missing_files['json_img_name_mismatch'])} 处）：")
        for item in missing_files['json_img_name_mismatch'][:10]:
            print(f"   - {item['json_path']}")
            print(f"     期望图片名: {item['expected']}")
            print(f"     JSON中记录: {item['actual']}")
        if len(missing_files['json_img_name_mismatch']) > 10:
            print(f"   ... 等 {len(missing_files['json_img_name_mismatch'])} 处不匹配")
    
    if missing_files['json_img_path_mismatch']:
        print(f"\n 2. JSON 中的 Img_path 与实际图片路径不匹配（共 {len(missing_files['json_img_path_mismatch'])} 处）：")
        for item in missing_files['json_img_path_mismatch'][:10]:
            print(f"   - {item['json_path']}")
            print(f"     期望相对路径: {item['expected']}")
            print(f"     JSON中记录: {item['actual']}")
        if len(missing_files['json_img_path_mismatch']) > 10:
            print(f"   ... 等 {len(missing_files['json_img_path_mismatch'])} 处不匹配")
    
    if missing_files['image_without_json']:
        print(f"\n 3. 存在没有对应 JSON 文件的图片（共 {len(missing_files['image_without_json'])} 张）：")
        for img_path in missing_files['image_without_json'][:10]:
            print(f"   - {img_path}")
        if len(missing_files['image_without_json']) > 10:
            print(f"   ... 等 {len(missing_files['image_without_json'])} 张图片")
    
    if missing_files['json_without_image']:
        print(f"\n 4. 存在没有对应图片的 JSON 文件（共 {len(missing_files['json_without_image'])} 个）：")
        for json_path in missing_files['json_without_image'][:10]:
            print(f"   - {json_path}")
        if len(missing_files['json_without_image']) > 10:
            print(f"   ... 等 {len(missing_files['json_without_image'])} 个 JSON 文件")
    
    if missing_files['processing_errors']:
        print(f"\n 5. 处理过程中发生错误（共 {len(missing_files['processing_errors'])} 个）：")
        for error in missing_files['processing_errors'][:10]:
            print(f"   - {error['json_path']}: {error['error']}")
        if len(missing_files['processing_errors']) > 10:
            print(f"   ... 等 {len(missing_files['processing_errors'])} 个错误")


def process_json_aggregate(json_path, folder_path, output_dir, folder_categories, max_workers, source_directory, all_failed_images, all_not_found_images):
    failed_images = []
    not_found_images = []

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"  - 跳过非列表结构: {json_path}")
            return

        def process_entry(entry):
            img_name = entry.get('Img_name') or entry.get('img_name')
            if not img_name:
                return entry
            image_path = os.path.join(folder_path, img_name)
            if not os.path.exists(image_path):
                not_found_images.append(image_path)
                return entry
            chinese_element_name = entry.get('China_element_name') or entry.get('chinese_element_name') or "未知元素"
            image_base64 = encode_image_to_base64(image_path)
            if not image_base64:
                failed_images.append(image_path)
                return entry
            new_caption = call_shubiaobiao_api(image_base64, image_path, chinese_element_name, folder_categories)
            if new_caption.startswith("错误:"):
                failed_images.append(image_path)
            entry['caption'] = new_caption
            return entry

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_entry, data))

        rel_path = os.path.relpath(json_path, start=source_directory)
        out_json_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(out_json_path), exist_ok=True)
        with open(out_json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        for entry in data:
            img_name = entry.get('Img_name') or entry.get('img_name')
            if img_name:
                src_img_path = os.path.join(folder_path, img_name)
                dst_img_path = os.path.join(os.path.dirname(out_json_path), img_name)
                if os.path.exists(src_img_path) and not os.path.exists(dst_img_path):
                    shutil.copy2(src_img_path, dst_img_path)

        # 自动重试失败部分
        if failed_images:
            still_failed = []
            for img_path in failed_images:
                entry = next((e for e in data if (e.get('Img_name') or e.get('img_name')) and os.path.join(folder_path, e.get('Img_name') or e.get('img_name')) == img_path), None)
                if entry:
                    chinese_element_name = entry.get('China_element_name') or entry.get('chinese_element_name') or "未知元素"
                    image_base64 = encode_image_to_base64(img_path)
                    if image_base64:
                        new_caption = call_shubiaobiao_api(image_base64, img_path, chinese_element_name, folder_categories)
                        if not new_caption.startswith("错误:"):
                            entry['caption'] = new_caption
                        else:
                            still_failed.append(img_path)
                    else:
                        still_failed.append(img_path)
                else:
                    still_failed.append(img_path)
            with open(out_json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            all_failed_images.extend(still_failed)
        all_failed_images.extend(failed_images)
        all_not_found_images.extend(not_found_images)

    except Exception as e:
        print(f"  - 处理聚合 JSON 失败: {json_path}: {e}")


def process_all_images():
    """新版：批量处理每个文件夹下的聚合 JSON 文件，输出到指定文件夹"""
    print("请在弹出的对话框中选择包含分类图片的[源文件夹]...")
    source_directory = filedialog.askdirectory(title="请选择包含分类图片的源文件夹")
    if not source_directory:
        print("未选择文件夹，程序退出")
        return

    print("请在弹出的对话框中选择输出文件夹...")
    output_dir = filedialog.askdirectory(title="请选择输出文件夹")
    if not output_dir:
        print("未选择输出文件夹，程序退出")
        return

    try:
        max_workers = int(input("请输入并发处理的线程数 (建议 1-5，默认 2): ") or "2")
        max_workers = max(1, min(10, max_workers))
    except ValueError:
        max_workers = 2
        print("输入无效，使用默认并发数 2")

    print("\n正在扫描聚合 JSON 文件...")
    json_files = []
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.lower().endswith('.json'):
                json_files.append(os.path.join(root, file))
    print(f"共找到 {len(json_files)} 个聚合 JSON 文件")

    all_failed_images = []
    all_not_found_images = []
    for json_path in json_files:
        folder_path = os.path.dirname(json_path)
        folder_categories = os.path.relpath(folder_path, source_directory)
        process_json_aggregate(json_path, folder_path, output_dir, folder_categories, max_workers, source_directory, all_failed_images, all_not_found_images)
    print("\n全部处理完成！")

    if all_not_found_images:
        print("\n❌ 找不到图片的路径如下：")
        for img_path in all_not_found_images:
            print(f"  - {img_path}")
    if all_failed_images:
        print("\n❌ caption未成功生成的图片路径如下：")
        for img_path in all_failed_images:
            print(f"  - {img_path}")
    if not all_failed_images and not all_not_found_images:
        print("\n✅ 所有图片均已成功生成 caption 且无缺失图片！")

# filepath: d:\software\中国风采集图片文学与语言\代码\AI生成Caption描述修改.py
if __name__ == "__main__":
    process_all_images()