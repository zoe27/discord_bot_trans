import sys
import pytesseract
import mss
import mss.tools
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QTimer
from PIL import Image
from googletrans import Translator
import pyautogui

# 配置tesseract路径（在Mac上可以不配置）
# pytesseract.pytesseract.tesseract_cmd = r"/usr/local/bin/tesseract"

translator = Translator()

class ScreenshotTranslator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_region = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture_and_translate)

    def initUI(self):
        self.setWindowTitle('实时区域截图翻译')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.btn_screenshot = QPushButton('开始截图', self)
        self.btn_screenshot.clicked.connect(self.start_select_region)
        layout.addWidget(self.btn_screenshot)

        self.text_original = QTextEdit(self)
        self.text_original.setPlaceholderText("识别出的原文")
        layout.addWidget(self.text_original)

        self.text_translated = QTextEdit(self)
        self.text_translated.setPlaceholderText("翻译后的文本")
        layout.addWidget(self.text_translated)

        self.setLayout(layout)

    def start_select_region(self):
        # 启动鼠标拖动选择区域的功能
        self.selected_region = pyautogui.locateOnScreen('select_area.png')  # 这里假设屏幕上有截图
        self.timer.start(1000)  # 每秒检测一次

    def capture_and_translate(self):
        if self.selected_region:
            # 使用 mss 截取选定区域
            with mss.mss() as sct:
                screenshot = sct.grab(self.selected_region)

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
