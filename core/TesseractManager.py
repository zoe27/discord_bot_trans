import os
import zipfile
import urllib.request
import shutil
import platform

class TesseractManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.tesseract_dir = os.path.join(self.base_dir, "tesseract")
        if not os.path.exists(self.tesseract_dir):
            os.makedirs(self.tesseract_dir)
        self.tesseract_exe = os.path.join(self.tesseract_dir, "tesseract.exe")

        if platform.system() != "Windows":
            raise RuntimeError("Auto download only supported on Windows in this setup")

    def ensure_tesseract(self):
        if not os.path.exists(self.tesseract_exe):
            print("Tesseract not found. Downloading...")
            self.download_and_extract()

    def download_and_extract(self):
        url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-v5.3.3.20231005.zip"
        zip_path = os.path.join(self.base_dir, "tesseract.zip")

        # 下载文件
        urllib.request.urlretrieve(url, zip_path)

        # 解压
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.tesseract_dir)

        os.remove(zip_path)
        print("Tesseract downloaded and extracted.")

    def get_tesseract_cmd(self):
        return self.tesseract_exe
