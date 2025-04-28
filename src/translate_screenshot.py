import sys
import pytesseract
import mss
import mss.tools
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PIL import Image
from googletrans import Translator

# 配置你的tesseract路径
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

translator = Translator()

class ScreenshotTranslator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('截图翻译小工具')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.btn_screenshot = QPushButton('截图并翻译', self)
        self.btn_screenshot.clicked.connect(self.capture_and_translate)
        layout.addWidget(self.btn_screenshot)

        self.text_original = QTextEdit(self)
        self.text_original.setPlaceholderText("识别出的原文")
        layout.addWidget(self.text_original)

        self.text_translated = QTextEdit(self)
        self.text_translated.setPlaceholderText("翻译后的文本")
        layout.addWidget(self.text_translated)

        self.setLayout(layout)

    def capture_and_translate(self):
        # 截图
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # 默认整个主屏
            screenshot = sct.grab(monitor)

            # 保存为临时图片
            img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
            img.save('temp_screenshot.png')

        # OCR识别
        text = pytesseract.image_to_string(Image.open('temp_screenshot.png'), lang='eng')

        self.text_original.setPlainText(text)

        # 翻译
        if text.strip():
            result = translator.translate(text, src='en', dest='zh-cn')
            self.text_translated.setPlainText(result.text)
        else:
            self.text_translated.setPlainText('没有识别到文字')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScreenshotTranslator()
    ex.show()
    sys.exit(app.exec_())
