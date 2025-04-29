'''
封装 OCR 识别，做文本变化检测
'''

# OcrEngine.py
# OCR模块，提取图片中的文字

import pytesseract

class OcrEngine:
    def __init__(self):
        pass

    def extract_text(self, img):
        # 使用pytesseract识别文字，默认英文
        text = pytesseract.image_to_string(img, lang='eng')
        return text
