import os

# --- 設定資料夾路徑 ---
image_dir = r"C:\Users\User\Desktop\img\id_card_images"
ocr_text_dir = r"C:\Users\User\Desktop\img\id_card_ocr_texts"

print(f"圖片資料夾路徑: {image_dir}")
print(f"OCR 文字資料夾路徑: {ocr_text_dir}")

# --- 步驟 1: 獲取圖片資料夾中所有圖片的檔名 ---
# os.listdir() 獲取所有檔案和資料夾名稱
# os.path.isfile() 判斷是否為檔案 (排除子資料夾)
# 確保只處理圖片檔案 (例如 .png, .jpg 等，這裡假設是 .png)
existing_image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f)) and f.lower().endswith('.png')]

print(f"\n在 '{image_dir}' 中找到 {len(existing_image_files)} 張圖片。")

# --- 步驟 2: 從圖片檔名中提取對應的索引，並構建應保留的 TXT 檔名 ---
# 預期圖片檔名格式為 'image_NNNNN.png'
# 因此我們需要提取 NNNNN 部分
desired_ocr_text_files = set()
for img_filename in existing_image_files:
    # 移除副檔名 .png
    base_name = os.path.splitext(img_filename)[0] # 例如 'image_00000'
    # 檢查是否符合預期格式 (以 'image_' 開頭，後面是數字)
    if base_name.startswith('image_') and base_name[6:].isdigit():
        # 提取數字部分並轉換為 TXT 檔名格式 'ocr_NNNNN.txt'
        # base_name[6:] 會取出 '00000' 部分
        ocr_filename = f"ocr_{base_name[6:]}.txt"
        desired_ocr_text_files.add(ocr_filename)
    else:
        print(f"警告: 圖片檔名 '{img_filename}' 不符合預期格式，將跳過。")

print(f"根據圖片檔案，預計保留 {len(desired_ocr_text_files)} 個 OCR 文字檔案。")

# --- 步驟 3: 遍歷 OCR 文字資料夾，刪除不匹配的檔案 ---
deleted_count = 0
all_ocr_text_files = [f for f in os.listdir(ocr_text_dir) if os.path.isfile(os.path.join(ocr_text_dir, f)) and f.lower().endswith('.txt')]

print(f"\n在 '{ocr_text_dir}' 中找到 {len(all_ocr_text_files)} 個 TXT 檔案，準備開始清理...")

for ocr_filename in all_ocr_text_files:
    if ocr_filename not in desired_ocr_text_files:
        file_to_delete = os.path.join(ocr_text_dir, ocr_filename)
        try:
            os.remove(file_to_delete)
            print(f"已刪除: {ocr_filename}")
            deleted_count += 1
        except OSError as e:
            print(f"錯誤: 無法刪除檔案 {ocr_filename} - {e}")

print(f"\n清理完成！共刪除了 {deleted_count} 個不匹配的 OCR 文字檔案。")
print(f"現在 '{ocr_text_dir}' 中還剩下 {len(os.listdir(ocr_text_dir)) - deleted_count} 個檔案。") # 估計剩餘數量