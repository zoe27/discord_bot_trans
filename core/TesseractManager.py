import logging
import os
import urllib.request
import platform

class TesseractManager:
    def __init__(self):
        self.tesseract_dir = os.path.join(os.getenv('APPDATA'), 'ScreenTranslator', 'tesseract')
        if not os.path.exists(self.tesseract_dir):
            os.makedirs(self.tesseract_dir)
        self.tesseract_exe = os.path.join(self.tesseract_dir, "tesseract.exe")
        logging.info(f"📁 Tesseract path: {self.tesseract_exe}")

        if platform.system() != "Windows":
            logging.info("🔄 Auto download Tesseract only supported on Windows")
            raise RuntimeError("Auto download only supported on Windows in this setup")

    def ensure_tesseract(self):
        if not os.path.exists(self.tesseract_exe):
            print("Tesseract not found. Downloading...")
            self.download_and_extract()

    def download_and_extract(self):
        url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-v5.3.3.20231005.exe"
        exe_path = os.path.join(self.tesseract_dir, "tesseract_setup.exe")

        logging.info(f"🔄 Downloading Tesseract from {url} ... and save to {exe_path}")

        try:
            # Download with progress check
            urllib.request.urlretrieve(url, exe_path)

            logging.info("📦 Installing Tesseract...")

            # Silent installation
            import subprocess
            result = subprocess.run([exe_path, '/S', f'/D={self.tesseract_dir}'],
                                    capture_output=True,
                                    text=True)
            logging.info(result.stdout)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode,
                    result.args,
                    result.stdout,
                    result.stderr
                )

        except urllib.error.URLError as e:
            logging.error(f"Download failed: {e}")
            raise
        except subprocess.CalledProcessError as e:
            logging.error(f"Installation failed: {e}")
            raise
        finally:
            if os.path.exists(exe_path):
                os.remove(exe_path)

        logging.info("Tesseract downloaded and installed.")

    def get_tesseract_cmd(self):
        return self.tesseract_exe