import sys
import pytesseract
import os
import requests
from tqdm import tqdm
import logging


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

    def __init__(self):
        # 判断是否为打包环境
        if getattr(sys, 'frozen', False):  # 如果是 PyInstaller 打包
            app_base = os.path.dirname(sys.executable)
            internal_tessdata = os.path.abspath(os.path.join(app_base, '..', 'Resources', 'tessdata'))
        else:
            internal_tessdata = os.path.join(os.path.dirname(__file__), 'tessdata')

        # 优先使用 .app 内部 Resources 路径（如果可写）
        if os.path.isdir(internal_tessdata) and os.access(internal_tessdata, os.W_OK):
            self.tessdata_dir = internal_tessdata
        else:
            # 回退到用户目录
            self.tessdata_dir = os.path.expanduser('~/Library/Application Support/ScreenTranslator/tessdata')
            os.makedirs(self.tessdata_dir, exist_ok=True)

        # 设置 TESSDATA_PREFIX 环境变量
        os.environ['TESSDATA_PREFIX'] = self.tessdata_dir
        logging.info(f"📁 use tessdata path: {self.tessdata_dir}")

        # 列出已存在的语言文件
        if os.path.exists(self.tessdata_dir):
            logging.info(f"📄 the exist language file: {[f for f in os.listdir(self.tessdata_dir) if f.endswith('.traineddata')]}")

    def _download_language(self, lang_code):
        traineddata_file = self.LANG_MAPPINGS.get(lang_code)
        if not traineddata_file:
            logging.error(f"❌ do not support the language: '{lang_code}'")
            raise Exception(f"❌ do not support the language: '{lang_code}'")

        url = f"https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/{traineddata_file}"
        dest_path = os.path.join(self.tessdata_dir, traineddata_file)

        logging.info(f"🔄 download language file '{lang_code}' from {url} ...")

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
                logging.info(f"✅ download finished: {dest_path}")
            else:
                logging.error(f"❌ download fail，code: {response.status_code}")
                raise Exception(f"❌ download fail，code: {response.status_code}")
        except Exception as e:
            logging.error(f"❌ download fail: {e}")
            raise

    def extract_text(self, img, lang='eng'):
        if lang not in self.LANG_MAPPINGS:
            logging.error(f"❌ do not support language: '{lang}'")
            raise Exception(f"❌ do not support language: '{lang}'")

        traineddata_path = os.path.join(self.tessdata_dir, self.LANG_MAPPINGS[lang])
        if not os.path.exists(traineddata_path):
            logging.warning(f"⚠️ not found the language file '{lang}'，try to download...")
            self._download_language(lang)

        config = f'--tessdata-dir "{self.tessdata_dir}"'

        try:
            text = pytesseract.image_to_string(img, lang=lang, config=config)
            return text
        except pytesseract.TesseractError as e:
            logging.error(f"❌ OCR error: {e}")
            return None