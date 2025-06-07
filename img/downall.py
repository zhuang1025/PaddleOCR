import os
from PIL import Image
from datasets import load_dataset
import json

# 載入你的資料集
ds = load_dataset("lansinuote/ocr_id_card")

# 定義要保存的資料夾名稱
output_image_dir = "id_card_images"
output_ocr_dir = "id_card_ocr_texts"

# 創建資料夾，如果它們不存在的話
os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_ocr_dir, exist_ok=True)

print(f"圖片將保存到： {output_image_dir}")
print(f"OCR 文字將保存到： {output_ocr_dir}")

# --- 關鍵修改：更新輔助函數以提取 'word' 鍵的值 ---
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
        # 您也可以保留對 'text' 和 'transcription' 的檢查，以防數據集中有例外
        elif 'text' in item and item['text'] is not None:
            return str(item['text']).strip()
        elif 'transcription' in item and item['transcription'] is not None:
            return str(item['transcription']).strip()
    return "" # 如果無法提取到有效文字，返回空字串

# 遍歷資料集
for i, example in enumerate(ds['train']):
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

    if (i + 1) % 1000 == 0:
        print(f"已處理 {i + 1} 個樣本...")

print("所有圖片和 OCR 文字已成功保存！")