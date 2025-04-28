import sys
import pytesseract
import mss
import mss.tools
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import QTimer
from PIL import Image
from googletrans import Translator
import hashlib

# 配置tesseract路径（Mac上可以不需要配置）
# pytesseract.pytesseract.tesseract_cmd = r"/usr/local/bin/tesseract"

translator = Translator()

class ScreenshotTranslator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_region = None
        self.previous_hash = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture_and_compare)

    def initUI(self):
        self.setWindowTitle('实时区域监控翻译')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.btn_screenshot = QPushButton('开始监控区域', self)
        self.btn_screenshot.clicked.connect(self.start_monitoring)
        layout.addWidget(self.btn_screenshot)

        self.text_original = QTextEdit(self)
        self.text_original.setPlaceholderText("识别出的原文")
        layout.addWidget(self.text_original)

        self.text_translated = QTextEdit(self)
        self.text_translated.setPlaceholderText("翻译后的文本")
        layout.addWidget(self.text_translated)

        self.setLayout(layout)

    def start_monitoring(self):
        # 设置要监控的区域（可以自定义某个屏幕区域）
        self.selected_region = {'top': 100, 'left': 100, 'width': 500, 'height': 300}
        self.timer.start(2000)  # 每2秒检查一次

    def capture_and_compare(self):
        if self.selected_region:
            # 使用mss抓取屏幕上的特定区域
            with mss.mss() as sct:
                screenshot = sct.grab(self.selected_region)

                # 转成图片并计算hash
                img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
                img.save('temp_screenshot.png')

                # 计算当前图片的哈希值
                current_hash = self.hash_image('temp_screenshot.png')

                if current_hash != self.previous_hash:
                    # 内容发生了变化，进行OCR识别并翻译
                    self.previous_hash = current_hash
                    text = pytesseract.image_to_string(img, lang='eng')

                    self.text_original.setPlainText(text)

                    # 翻译
                    if text.strip():
                        result = translator.translate(text, src='en', dest='zh-cn')
                        self.text_translated.setPlainText(result.text)
                    else:
                        self.text_translated.setPlainText('没有识别到文字')

    def hash_image(self, img_path):
        """计算图片的哈希值，用来判断图片是否变化"""
        with open(img_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScreenshotTranslator()
    ex.show()
    sys.exit(app.exec_())
