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
        self.sct = mss.mss()  # 初始化屏幕截图器

    def capture_area(self, rect):
        # rect 是 QRect对象，需要转换为 dict
        logging.info(f"start to Capturing area")
        try:
            monitor = {
                "top": rect.top(),
                "left": rect.left(),
                "width": rect.width(),
                "height": rect.height()
            }
            sct_img = self.sct.grab(monitor)
            img = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)
            return img
        except mss.exception.ScreenShotError as e:
            logging.error(f"Screenshot error: {e}")
            return None
        except ValueError as e:
            logging.error(f"Image conversion error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error during screen capture: {e}")
            return None
