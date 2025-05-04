'''
封装 OCR 识别，做文本变化检测
'''

# OcrEngine.py
# OCR模块，提取图片中的文字
import pytesseract
import os
import requests
from tqdm import tqdm


class OcrEngine:
    # 语言代码到训练数据文件的映射
    LANG_MAPPINGS = {
        'eng': 'eng.traineddata',  # English
        'chi_sim': 'chi_sim.traineddata',  # Simplified Chinese
        'chi_tra': 'chi_tra.traineddata',  # Traditional Chinese
        'jpn': 'jpn.traineddata',  # Japanese
        'kor': 'kor.traineddata',  # Korean
        'fra': 'fra.traineddata',  # French
        'deu': 'deu.traineddata',  # German
        'spa': 'spa.traineddata',  # Spanish
    }

    def __init__(self, tessdata_dir='./tessdata'):
        self.tessdata_dir = tessdata_dir
        os.makedirs(self.tessdata_dir, exist_ok=True)

    def _download_language(self, lang_code):
        # url = f"https://github.com/tesseract-ocr/tessdata/{lang_code}.traineddata"
        # dest_path = os.path.join(self.tessdata_dir, f"{lang_code}.traineddata")

        ineddata_file = self.LANG_MAPPINGS.get(lang_code)
        if not ineddata_file:
            raise Exception(f"❌ Unsupported language code: '{lang_code}'")
        url = f"https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/{ineddata_file}"
        dest_path = os.path.join(self.tessdata_dir, ineddata_file)

        print(f"🔄 Downloading language data for '{url}' ...")



        print(f"🔄 Downloading language data for '{lang_code}' ...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            with open(dest_path, 'wb') as f, tqdm(
                    desc=f"Downloading {lang_code}",
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
            ) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    pbar.update(size)
            print(f"✅ Downloaded: {dest_path}")
        else:
            raise Exception(f"❌ Failed to download language data for '{lang_code}'")

    def extract_text(self, img, lang='eng'):
        # print("Language requested:", lang)

        if lang not in self.LANG_MAPPINGS:
            raise Exception(f"❌ Unsupported language code: '{lang}'")
        # print(f"Language requested: {lang} (traineddata: {self.LANG_MAPPINGS[lang]})")

        # 检查语言文件是否存在本地
        traineddata_path = os.path.join(self.tessdata_dir, f"{lang}.traineddata")
        if not os.path.exists(traineddata_path):
            print(f"❗ '{lang}' not available locally. Trying to download...")
            self._download_language(lang)

        # 使用指定的 tessdata 目录
        config = f'--tessdata-dir "{self.tessdata_dir}"'

        # 进行 OCR 识别
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        return text

