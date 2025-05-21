'''
管理多屏截图逻辑
'''
import logging

# ScreenCapture.py
# 区域截图模块

import mss
from PIL import Image

class ScreenCapture:
    def __init__(self):
        self.sct = None

    def _ensure_mss_instance(self):
        if self.sct is None:
            self.sct = mss.mss()

    def capture_area(self, rect):
        # rect 是 QRect对象，需要转换为 dict
        logging.info("Start capturing area")
        try:
            self._ensure_mss_instance()
            monitor = {
                "top": rect.top(),
                "left": rect.left(),
                "width": rect.width(),
                "height": rect.height()
            }
            with self.sct as sct:
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)
                return img
        except mss.exception.ScreenShotError as e:
            logging.error(f"Screenshot error: {e}")
            self.sct = None  # Reset the instance
            return None
        except ValueError as e:
            logging.error(f"Image conversion error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error during screen capture: {e}")
            self.sct = None  # Reset the instance
            return None
