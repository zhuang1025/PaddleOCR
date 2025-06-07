import os
from PIL import Image
from datasets import load_dataset
import json

# 載入你的資料集
# load_dataset() 會自動處理下載和快取
ds = load_dataset("lansinuote/ocr_id_card")

# 定義要保存的資料夾名稱
output_image_dir = "id_card_images"
output_ocr_dir = "id_card_ocr_texts"

# 創建資料夾，如果它們不存在的話
os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_ocr_dir, exist_ok=True)

print(f"圖片將保存到： {output_image_dir}")
print(f"OCR 文字將保存到： {output_ocr_dir}")

# --- 新增一個輔助函數來安全地提取文字 ---
def get_text_from_item(item):
    """
    從 OCR 資料的單個元素中提取文字內容。
    根據您提供的輸出，文字內容儲存在 'word' 鍵下。
    """
    if isinstance(item, str): # 如果元素本身就是字串
        return item.strip()
    elif isinstance(item, dict):
        # 這裡檢查 'word' 鍵
        if 'word' in item and item['word'] is not None:
            return str(item['word']).strip()
        elif 'text' in item and item['text'] is not None:
            return str(item['text']).strip()
        elif 'transcription' in item and item['transcription'] is not None:
            return str(item['transcription']).strip()
    return "" # 如果無法提取到有效文字，返回空字串

# --- 關鍵修改：限制只處理前 500 個樣本 ---
# 您可以使用 ds['train'].select(range(500)) 來建立一個只包含前 500 個樣本的新 Dataset
# 或者直接在 for 迴圈中加入條件判斷
num_samples_to_process = 500

print(f"將處理前 {num_samples_to_process} 個樣本...")

# 遍歷資料集
# 使用 ds['train'].take(num_samples_to_process) 是一個更優雅且高效的方式
# 它會從訓練集中取出指定數量（500）的樣本
for i, example in enumerate(ds['train'].take(num_samples_to_process)):
# 或者使用更傳統的 for 迴圈和 if 判斷
# for i, example in enumerate(ds['train']):
#     if i >= num_samples_to_process:
#         break

    image = example['image']
    ocr_data = example['ocr']

    # 保存圖片
    image_filename = os.path.join(output_image_dir, f"image_{i:05d}.png")
    image.save(image_filename)

    # 提取並保存 OCR 文字
    ocr_filename = os.path.join(output_ocr_dir, f"ocr_{i:05d}.txt")

    extracted_texts = []
    if isinstance(ocr_data, list):
        for item in ocr_data:
            text = get_text_from_item(item)
            if text: # 只有當提取到的文字不為空時才加入
                extracted_texts.append(text)
    else: # 處理 ocr_data 不是列表的情況 (例如單一字典或字串)
        text = get_text_from_item(ocr_data)
        if text:
            extracted_texts.append(text)

    # 將所有提取到的文字用換行符連接起來
    unified_ocr_text = "\n".join(extracted_texts)

    with open(ocr_filename, 'w', encoding='utf-8') as f:
        f.write(unified_ocr_text)

    # 印出進度
    if (i + 1) % 100 == 0: # 可以調整為每 100 個樣本印一次進度
        print(f"已處理 {i + 1} 個樣本...")

print(f"已完成處理前 {num_samples_to_process} 個樣本。")