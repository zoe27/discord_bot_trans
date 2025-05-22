import logging
import os
import urllib.request
import platform

'''
    only for window 
    This module handles the automatic download and installation of 
    Tesseract OCR engine on Windows. It manages the Tesseract
    executable path and ensures it's properly set up for the application.
'''

class TesseractManager:
    def __init__(self):
        self.tesseract_dir = os.path.join(os.getenv('APPDATA'), 'ScreenTranslator', 'tesseract')
        if not os.path.exists(self.tesseract_dir):
            os.makedirs(self.tesseract_dir)
        logging.info(f"📁 Tesseract directory: {self.tesseract_dir}")
        self.tesseract_exe = os.path.join(self.tesseract_dir, "tesseract.exe")
        logging.info(f"📁 Tesseract execution path: {self.tesseract_exe}")

        if platform.system() != "Windows":
            logging.info("🔄 Auto download Tesseract only supported on Windows")
            raise RuntimeError("Auto download only supported on Windows in this setup")

    def ensure_tesseract(self):
        if not os.path.exists(self.tesseract_exe):
            print("Tesseract not found. Downloading...")
            self.download_and_extract()

    def download_and_extract(self):
        url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
        exe_path = os.path.join(self.tesseract_dir, "tesseract_setup.exe")

        logging.info(f"🔄 Downloading Tesseract from {url} to {exe_path}")

        try:
            urllib.request.urlretrieve(url, exe_path)

            logging.info(f"📦 Installing Tesseract into {self.tesseract_dir}")

            import subprocess
            result = subprocess.run(
                [exe_path, '/S', f'/D="{self.tesseract_dir}"'],
                capture_output=True,
                text=True
            )

            logging.info(result.stdout)
            if result.returncode != 0:
                logging.error(f"❌ Installation failed! Return code: {result.returncode}")
                logging.error(f"Stderr: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

            if not os.path.exists(self.tesseract_exe):
                raise FileNotFoundError("Installation finished, but tesseract.exe not found.")

        except urllib.error.URLError as e:
            logging.error(f"❌ Download failed: {e}")
            raise
        except subprocess.CalledProcessError as e:
            logging.error(f"Installation failed with return code {e.returncode}")
            logging.error(f"Stdout: {e.stdout}")
            logging.error(f"Stderr: {e.stderr}")
            raise
        finally:
            if os.path.exists(exe_path):
                os.remove(exe_path)

        logging.info("✅ Tesseract downloaded and installed.")

    def get_tesseract_cmd(self):
        return self.tesseract_exe