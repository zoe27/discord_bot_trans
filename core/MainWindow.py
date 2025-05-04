# MainWindow.py
# 主界面，负责管理整体流程：选区、截图、OCR识别、翻译显示
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QApplication
from PyQt5.QtCore import QTimer, QRect
from SelectionOverlay import SelectionWindow
from ScreenCapture import ScreenCapture
from OcrEngine import OcrEngine
from TranslatorEngine import TranslatorEngine
from OverlayDisplay import OverlayDisplay


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

        # 初始化浮窗
        self.overlay = OverlayDisplay()

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
        QApplication.processEvents()
        self.selection_window = SelectionWindow(self)
        self.selection_window.show()
        self.selection_window.setGeometry(QApplication.desktop().geometry())

    def on_area_selected(self, rect: QRect):
        """Callback when area is selected"""
        self.selected_rect = rect
        if self.selected_rect:
            print("已选定区域:", rect)
            self.overlay.set_rect(rect)  # 显示浮窗选区
            self.show()
        self.timer.start(1000)  # 每秒处理一次

    def process(self):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 运行截图")
        if not self.selected_rect:
            print("没有选定区域")
            return

        img = self.capture.capture_area(self.selected_rect)
        text = self.ocr.extract_text(img)

        # 如果OCR结果为空或与上次相同，不进行翻译
        if not text.strip():
            return

        # 比较文本是否有实质变化（忽略空白字符的差异）
        current_text = text.strip()
        last_text = self.last_text.strip()

        if current_text != last_text:
            self.last_text = text
            self.text_original.setPlainText(text)
            translation = self.translator.translate(text)
            self.text_translated.setPlainText(translation)
