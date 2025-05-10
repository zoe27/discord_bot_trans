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

        # if platform.system() != "Windows":
        #     raise RuntimeError("Auto download only supported on Windows in this setup")

    def ensure_tesseract(self):
        if not os.path.exists(self.tesseract_exe):
            print("Tesseract not found. Downloading...")
            self.download_and_extract()

    def download_and_extract(self):
        url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
        exe_path = os.path.join(self.tesseract_dir, "tesseract_setup.exe")

        # 下载文件
        urllib.request.urlretrieve(url, exe_path)

        # 安装 Tesseract (静默安装)
        import subprocess
        try:
            subprocess.run([exe_path, '/S', f'/D={self.tesseract_dir}'], check=True)
        finally:
            os.remove(exe_path)

        print("Tesseract downloaded and installed.")

    def get_tesseract_cmd(self):
        return self.tesseract_exe