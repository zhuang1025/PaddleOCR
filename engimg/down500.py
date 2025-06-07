import os
from PIL import Image
from datasets import load_dataset

# 載入資料集（會自動處理下載和快取）
ds = load_dataset("Lunzima/ocr_dataset")

# 定義要保存的資料夾名稱
output_image_dir = "id_card_images"
output_answer_dir = "id_card_answers"

# 創建資料夾，如果它們不存在的話
os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_answer_dir, exist_ok=True)

print(f"圖片將保存到： {output_image_dir}")
print(f"答案文字將保存到： {output_answer_dir}")

# 限制只處理前 500 筆資料
num_samples_to_process = 500
print(f"將處理前 {num_samples_to_process} 個樣本...")

# 遍歷前 500 筆資料
for i, example in enumerate(ds['train'].take(num_samples_to_process)):
    image = example['image']
    answer = example.get('answer', '').strip()

    # 保存圖片
    image_filename = os.path.join(output_image_dir, f"image_{i:05d}.png")
    image.save(image_filename)

    # 保存答案文字
    answer_filename = os.path.join(output_answer_dir, f"answer_{i:05d}.txt")
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(answer)

    # 印出進度
    if (i + 1) % 100 == 0:
        print(f"已處理 {i + 1} 個樣本...")

print(f"已完成處理前 {num_samples_to_process} 個樣本。")
