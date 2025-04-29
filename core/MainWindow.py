'''
管理整体界面、定时截图、调用 OCR 和 翻译模块
'''

# MainWindow.py
# 主界面，负责管理整体流程：选区、截图、OCR识别、翻译显示

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QApplication
from PyQt5.QtCore import QTimer
from SelectionOverlay import SelectionWindow
from ScreenCapture import ScreenCapture
from OcrEngine import OcrEngine
from TranslatorEngine import TranslatorEngine


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # 保存选中的区域
        self.selected_rect = None

        # 定时器，每隔一段时间截图识别
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)

        # 初始化核心功能模块
        self.capture = ScreenCapture()
        self.ocr = OcrEngine()
        self.translator = TranslatorEngine()

        # 保存上一次识别到的文字，用来对比
        self.last_text = ""

    def initUI(self):
        self.setWindowTitle('实时区域监控翻译')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # 按钮：点击后开始选择区域
        self.btn_select = QPushButton('选择实时翻译区域', self)
        self.btn_select.clicked.connect(self.select_area)
        layout.addWidget(self.btn_select)

        # 显示识别出的原文
        self.text_original = QTextEdit(self)
        self.text_original.setPlaceholderText('识别到的原文')
        layout.addWidget(self.text_original)

        # 显示翻译后的内容
        self.text_translated = QTextEdit(self)
        self.text_translated.setPlaceholderText('翻译后的文本')
        layout.addWidget(self.text_translated)

        self.setLayout(layout)

    def select_area(self):
        self.hide()
        QApplication.processEvents()  # Force process pending events
        self.selection_window = SelectionWindow(self)
        self.selection_window.show()
        self.selection_window.setGeometry(QApplication.desktop().geometry())  # 自动铺满整个屏幕

    def on_area_selected(self, rect):
        # 用户选好区域后回调
        self.selected_rect = rect
        self.overlay.hide()
        self.overlay.close()
        self.show()
        self.timer.start(1000)  # 每秒处理一次（可以根据需求调节）

    def process(self):
        # 主处理逻辑：截图、OCR、翻译
        if not self.selected_rect:
            print("没有选定区域")
            return

        img = self.capture.capture_area(self.selected_rect)
        text = self.ocr.extract_text(img)

        print(f"识别到的文本: {text}")

        # 只有识别结果变化时才更新（防止频繁翻译）
        if text.strip() and text != self.last_text:
            self.last_text = text
            self.text_original.setPlainText(text)
            translation = self.translator.translate(text)
            self.text_translated.setPlainText(translation)
