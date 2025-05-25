import os
import platform
import urllib.request
import zipfile
import shutil
import logging

class TesseractManager:
    def __init__(self):
        if platform.system() != "Windows":
            logging.warning("🔄 Auto-download of Tesseract is only supported on Windows.")
            raise RuntimeError("Auto download only supported on Windows.")

        self.tesseract_base_dir = os.path.join(os.getenv('APPDATA'), 'ScreenTranslator')
        self.tesseract_dir = os.path.join(self.tesseract_base_dir, 'Tesseract-OCR')
        self.tesseract_exe = os.path.join(self.tesseract_dir, 'tesseract.exe')

        os.makedirs(self.tesseract_base_dir, exist_ok=True)
        logging.info(f"📁 Tesseract base dir: {self.tesseract_base_dir}")
        logging.info(f"📁 Tesseract executable: {self.tesseract_exe}")

    def ensure_tesseract(self):
        if not os.path.exists(self.tesseract_exe):
            logging.info("🔍 Tesseract not found. Downloading and extracting...")
            self.download_and_extract()
        if not os.path.exists(self.tesseract_exe):
            raise FileNotFoundError("❌ Tesseract installation failed.")
        logging.info(f"✅ Tesseract is ready at: {self.tesseract_exe}")

    def download_and_extract(self):
        url = "https://github.com/zoe27/tools/raw/refs/heads/master/tool_dir/Tesseract.zip"
        zip_path = os.path.join(self.tesseract_base_dir, "tesseract.zip")

        try:
            urllib.request.urlretrieve(url, zip_path)
            logging.info(f"📦 Downloaded ZIP to: {zip_path}")

            # 清理旧的 Tesseract-OCR 文件夹
            if os.path.exists(self.tesseract_dir):
                shutil.rmtree(self.tesseract_dir)

            # 解压到 base_dir，下一级才是 Tesseract-OCR/
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.tesseract_base_dir)

            if not os.path.exists(self.tesseract_exe):
                raise FileNotFoundError("❌ Extraction completed, but tesseract.exe not found.")

        except urllib.error.URLError as e:
            logging.error(f"❌ Failed to download: {e}")
            raise
        except zipfile.BadZipFile as e:
            logging.error(f"❌ Bad ZIP file: {e}")
            raise
        except Exception as e:
            logging.error(f"❌ Unexpected error during download or extraction: {e}")
            raise
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)
                logging.info(f"🧹 Deleted temporary ZIP file: {zip_path}")

    def get_tesseract_cmd(self):
        return self.tesseract_exe
