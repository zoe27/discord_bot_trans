import sys

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
        # 设置 TESSDATA_PREFIX 到程序运行目录下的 tessdata 文件夹
        # current_dir = os.path.dirname(os.path.abspath(__file__))

        # if tessdata_dir is None:
        #     tessdata_dir = os.path.join(current_dir, 'tessdata')

        # Set TESSDATA_PREFIX to the correct path
        if getattr(sys, 'frozen', False):  # If running as a packaged app
            # base_path = sys._MEIPASS
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        os.environ['TESSDATA_PREFIX'] = os.path.join(base_path, 'tessdata')

        # 设置 TESSDATA_PREFIX 环境变量
        # os.environ['TESSDATA_PREFIX'] = tessdata_dir
        print(f"Setting TESSDATA_PREFIX to: {os.environ['TESSDATA_PREFIX']}")

        # 初始化 tessdata 目录
        self.tessdata_dir = os.environ['TESSDATA_PREFIX']
        if not os.path.exists(self.tessdata_dir):
            os.makedirs(self.tessdata_dir, exist_ok=True)

        print(f"Available language files: {[f for f in os.listdir(self.tessdata_dir) if f.endswith('.traineddata')]}")

    def _download_language(self, lang_code):
        # 检查语言代码是否有效
        traineddata_file = self.LANG_MAPPINGS.get(lang_code)
        if not traineddata_file:
            raise Exception(f"❌ Unsupported language code: '{lang_code}'")

        # 构建下载路径
        url = f"https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/{traineddata_file}"
        dest_path = os.path.join(self.tessdata_dir, traineddata_file)

        print(f"🔄 Downloading language data for '{lang_code}' from {url} ...")

        # 请求并保存文件
        try:
            response = requests.get(url, stream=True, timeout=30)
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
                raise Exception(f"❌ Failed to download language data for '{lang_code}', status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error downloading language file: {e}")
            raise

    def extract_text(self, img, lang='eng'):
        if lang not in self.LANG_MAPPINGS:
            raise Exception(f"❌ Unsupported language code: '{lang}'")

        # 检查语言文件是否存在本地
        traineddata_path = os.path.join(self.tessdata_dir, f"{lang}.traineddata")
        if not os.path.exists(traineddata_path):
            print(f"❗ '{lang}' not available locally. Trying to download...")
            self._download_language(lang)

        # 使用指定的 tessdata 目录
        config = f'--tessdata-dir "{self.tessdata_dir}"'

        # 进行 OCR 识别
        try:
            text = pytesseract.image_to_string(img, lang=lang, config=config)
            return text
        except pytesseract.TesseractError as e:
            print(f"❌ Error during OCR: {e}")
            return None
