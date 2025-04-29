import mss.tools

import sys
import pytesseract
import mss
import mss.tools
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QTimer, QRect
from PIL import Image
from googletrans import Translator
from selection_window import SelectionWindow

translator = Translator()

class ScreenshotTranslator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.selected_region = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture_and_translate)

    def initUI(self):
        # 设置窗口标题和初始大小
        self.setWindowTitle('实时区域截图翻译')
        # 设置窗口的位置和大小，参数分别为x坐标、y坐标、宽度和高度
        self.setGeometry(100, 100, 800, 600)

        # 创建垂直布局
        layout = QVBoxLayout()

        # 添加按钮用于选择截图区域
        self.btn_select_region = QPushButton('选择截图区域', self)
        self.btn_select_region.clicked.connect(self.start_select_region)
        layout.addWidget(self.btn_select_region)

        # 添加文本框用于显示识别出的原文
        self.text_original = QTextEdit(self)
        self.text_original.setPlaceholderText("识别出的原文")
        layout.addWidget(self.text_original)

        # 添加文本框用于显示翻译后的文本
        self.text_translated = QTextEdit(self)
        self.text_translated.setPlaceholderText("翻译后的文本")
        layout.addWidget(self.text_translated)

        # 设置布局
        self.setLayout(layout)

    def start_select_region(self):
        self.hide()
        QApplication.processEvents()  # Force process pending events
        self.selection_window = SelectionWindow(self)
        self.selection_window.show()
        self.selection_window.setGeometry(QApplication.desktop().geometry())  # 自动铺满整个屏幕

    def capture_and_translate(self):
        if self.selected_region:
            # 使用 mss 截取选定区域的屏幕
            with mss.mss() as sct:
                monitor = {
                    "top": self.selected_region.top(),
                    "left": self.selected_region.left(),
                    "width": self.selected_region.width(),
                    "height": self.selected_region.height()
                }
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)

            # 使用 pytesseract 进行 OCR 识别
            text = pytesseract.image_to_string(img, lang='eng')
            self.text_original.setPlainText(text)

            # 如果识别到文字，使用 googletrans 进行翻译
            if text.strip():
                result = translator.translate(text, src='en', dest='zh-cn')
                self.text_translated.setPlainText(result.text)
            else:
                # 如果未识别到文字，显示提示信息
                self.text_translated.setPlainText('没有识别到文字')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScreenshotTranslator()
    ex.show()
    sys.exit(app.exec_())
