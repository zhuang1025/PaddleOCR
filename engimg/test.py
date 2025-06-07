from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import os

# 定義目標輸出目錄
output_base_dir = r'C:\Users\zhuang\Desktop\Paddle\engimg'

# 確保輸出目錄存在
os.makedirs(output_base_dir, exist_ok=True)

# 初始化 PaddleOCR 物件
# lang='ch' 表示使用中文模型。如果你的圖片主要是英文，可以改成 lang='en'。
# use_gpu=False 表示使用 CPU，如果想用 GPU 且已安裝 CUDA，可將 use_gpu=False 移除
ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)

# 指定要處理的圖片路徑
img_path = r'C:\Users\zhuang\Desktop\Paddle\engimg\id_card_images\image_00000.png'

# 執行 OCR 辨識
result = ocr.ocr(img_path, det=True, rec=True, cls=True)

# 處理辨識結果
recognized_text = []
print("原始 OCR 辨識結果結構：")
print(result) # 打印完整的原始結果，幫助檢查結構

# 檢查 result 是否為空或 None
if result is None or len(result) == 0:
    print("未辨識到任何內容。")
else:
    # PaddleOCR 2.x 版本的 result 結構通常是 [ [box, (text, score)], ... ]
    # 但這裡的 result 是一個列表，可能每個元素本身又是一個列表
    # 根據你的錯誤輸出，可能是 result[0] 才是真正的結果列表
    # 讓我們更健壯地處理它
    processed_results = []
    # 判斷 result 的第一層是否是我們期望的結構，如果不是，就展開一層
    if len(result) > 0 and isinstance(result[0], list) and (len(result[0]) == 2 and isinstance(result[0][0], list) and isinstance(result[0][1], tuple)):
        # 如果 result 已經是直接包含 [box, (text, score)] 的列表
        processed_results = result
    elif len(result) > 0 and isinstance(result[0], list) and len(result[0]) > 0 and isinstance(result[0][0], list) and isinstance(result[0][0][0], list) and isinstance(result[0][0][1], tuple):
        # 如果 result 是 [[[box, (text, score)], ...]] 這樣的結構，例如 result = [[result_list]]
        processed_results = result[0]
    else:
        print("警告：OCR 結果結構不符合預期。請檢查 PaddleOCR 版本或輸入圖片。")
        processed_results = [] # 清空以避免後續錯誤

    for line_info in processed_results:
        # 確保 line_info 有足夠的元素且第二個元素是元組
        if len(line_info) >= 2 and isinstance(line_info[1], tuple):
            text_content = line_info[1][0] # 這裡應該是辨識到的文字
            recognized_text.append(text_content)
            print(f"辨識到: {text_content}")
        else:
            print(f"警告：跳過不符合預期的結果行：{line_info}")


# --- 保存辨識出的文字到 .txt 檔案 ---
# 獲取原始圖片的檔名（不含副檔名）
img_filename_without_ext = os.path.splitext(os.path.basename(img_path))[0]
output_txt_filename = f"{img_filename_without_ext}_ocr_result.txt"
output_txt_path = os.path.join(output_base_dir, output_txt_filename)

if recognized_text: # 只有當有辨識到文字時才寫入檔案
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for text_line in recognized_text:
            f.write(text_line + '\n') # text_line 現在應該是字串
    print(f"\n辨識文字已保存到：{output_txt_path}")
else:
    print("\n沒有辨識到文字，未生成文字檔。")


# --- 保存帶有辨識框的圖片到 .jpg 檔案 (可選) ---
if processed_results: # 只有當有辨識結果時才嘗試繪圖
    # 獲取原始圖片，轉換為 RGB 模式以避免色彩問題
    image = Image.open(img_path).convert('RGB')

    # 提取辨識結果中的框、文字和置信度 (從 processed_results 而不是原始 result)
    boxes = [line_info[0] for line_info in processed_results if len(line_info) >= 2 and isinstance(line_info[1], tuple)]
    txts = [line_info[1][0] for line_info in processed_results if len(line_info) >= 2 and isinstance(line_info[1], tuple)]
    scores = [line_info[1][1] for line_info in processed_results if len(line_info) >= 2 and isinstance(line_info[1], tuple)]

    # 繪製辨識結果到圖片上
    try:
        # 嘗試使用 PaddleOCR 預設字體路徑
        # 如果這段程式碼和 PaddleOCR 安裝在同一個環境且路徑結構沒有被大幅修改，這個路徑通常是正確的。
        paddleocr_install_path = os.path.dirname(os.path.dirname(os.path.abspath(PaddleOCR.__file__)))
        font_path = os.path.join(paddleocr_install_path, 'doc', 'fonts', 'simfang.ttf')
        if not os.path.exists(font_path):
            # 如果預設路徑找不到，嘗試另一個常見路徑
            font_path = os.path.join(paddleocr_install_path, 'paddleocr', 'doc', 'fonts', 'simfang.ttf')
        if not os.path.exists(font_path):
             # 最後，如果 still 找不到，嘗試使用 Windows 系統字體
             print("警告：找不到 PaddleOCR 預設字體 simfang.ttf。嘗試使用系統字體...")
             system_font_path = 'C:/Windows/Fonts/msjh.ttc' # 微軟正黑體
             if os.path.exists(system_font_path):
                 font_path = system_font_path
             else:
                 system_font_path = 'C:/Windows/Fonts/simsun.ttc' # 宋體
                 if os.path.exists(system_font_path):
                     font_path = system_font_path
                 else:
                     font_path = None # 如果系統字體也找不到，就不指定字體
                     print("警告：系統字體也找不到。將不指定字體，可能無法正確顯示中文。")


        if font_path and os.path.exists(font_path):
            im_show = draw_ocr(image, boxes, txts, scores, font_path=font_path)
        else:
            im_show = draw_ocr(image, boxes, txts, scores) # 不指定字體，可能無法正確顯示中文

    except Exception as e:
        print(f"繪製 OCR 結果時發生錯誤：{e}")
        im_show = image # 如果繪圖失敗，就只保存原始圖片

    im_show = Image.fromarray(im_show)

    output_img_filename = f"{img_filename_without_ext}_ocr_result.jpg"
    output_img_path = os.path.join(output_base_dir, output_img_filename)
    im_show.save(output_img_path)
    print(f"辨識結果圖片已保存到：{output_img_path}")
else:
    print("沒有辨識結果，未生成結果圖片。")