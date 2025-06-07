import os
from PIL import Image
from datasets import load_dataset
import json

# 載入你的資料集
ds = load_dataset("lansinuote/ocr_id_card")

# --- 定義新的資料夾名稱 ---
output_new_image_dir = "newid_card_images"
output_new_ocr_dir = "newid_card_ocr_texts"

# 創建新的資料夾，如果它們不存在的話
os.makedirs(output_new_image_dir, exist_ok=True)
os.makedirs(output_new_ocr_dir, exist_ok=True)

print(f"新的圖片將保存到： {output_new_image_dir}")
print(f"新的 OCR 文字將保存到： {output_new_ocr_dir}")

# --- 輔助函數：安全地提取文字 (與之前相同) ---
def get_text_from_item(item):
    """
    從 OCR 資料的單個元素中提取文字內容。
    根據您提供的輸出，文字內容儲存在 'word' 鍵下。
    """
    if isinstance(item, str):
        return item.strip()
    elif isinstance(item, dict):
        if 'word' in item and item['word'] is not None:
            return str(item['word']).strip()
        elif 'text' in item and item['text'] is not None:
            return str(item['text']).strip()
        elif 'transcription' in item and item['transcription'] is not None:
            return str(item['transcription']).strip()
    return ""

# --- 關鍵修改：從指定位置開始處理指定數量的樣本 ---
start_index = 500  # 從索引 500 開始
num_samples_to_process_additional = 200 # 接著處理 200 個樣本 (500 ~ 699)

print(f"將從索引 {start_index} 開始，處理額外 {num_samples_to_process_additional} 個樣本...")

# 使用 skip() 跳過前面已處理的樣本，然後使用 take() 取出接下來的樣本
# ds['train'].skip(start_index) 會跳過前 start_index 個樣本
# .take(num_samples_to_process_additional) 會從跳過後的資料集中取 num_samples_to_process_additional 個樣本
subset_ds = ds['train'].skip(start_index).take(num_samples_to_process_additional)

# 遍歷新取出的子集
for i, example in enumerate(subset_ds):
    # 因為 i 是針對子集從 0 開始計數的，我們需要計算原始資料集中的真實索引
    original_index = start_index + i

    image = example['image']
    ocr_data = example['ocr']

    # 保存圖片到新的資料夾
    # 檔案命名仍使用原索引來保持唯一性，例如 image_00500.png
    image_filename = os.path.join(output_new_image_dir, f"image_{original_index:05d}.png")
    image.save(image_filename)

    # 提取並保存 OCR 文字到新的資料夾
    ocr_filename = os.path.join(output_new_ocr_dir, f"ocr_{original_index:05d}.txt")

    extracted_texts = []
    if isinstance(ocr_data, list):
        for item in ocr_data:
            text = get_text_from_item(item)
            if text:
                extracted_texts.append(text)
    else:
        text = get_text_from_item(ocr_data)
        if text:
            extracted_texts.append(text)

    unified_ocr_text = "\n".join(extracted_texts)

    with open(ocr_filename, 'w', encoding='utf-8') as f:
        f.write(unified_ocr_text)

    # 印出進度，這裡的 i 是從 0 開始計數的子集索引
    if (i + 1) % 50 == 0: # 可以調整為每 50 個樣本印一次進度
        print(f"已處理 {i + 1} 個 (總計 {original_index + 1} 個) 樣本...")

print(f"已完成處理額外 {num_samples_to_process_additional} 個樣本。")
print(f"這些樣本的原始索引範圍是從 {start_index} 到 {start_index + num_samples_to_process_additional - 1}。")