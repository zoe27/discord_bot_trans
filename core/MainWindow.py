# MainWindow.py
# 管理整体界面：选区、截图、OCR识别、翻译显示

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QApplication
from PyQt5.QtCore import QTimer, QRect
from PyQt5.QtGui import QPainter, QPen, QColor
from SelectionOverlay import SelectionWindow
from ScreenCapture import ScreenCapture
from OcrEngine import OcrEngine
from TranslatorEngine import TranslatorEngine


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_rect = None
        self.last_text = ""

        self.capture = ScreenCapture()
        self.ocr = OcrEngine()
        self.translator = TranslatorEngine()

        self.initUI()

        # 定时器：每秒处理一次
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)

    def initUI(self):
        self.setWindowTitle('实时区域监控翻译')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.btn_select = QPushButton('选择实时翻译区域', self)
        self.btn_select.clicked.connect(self.select_area)
        layout.addWidget(self.btn_select)

        self.text_original = QTextEdit(self)
        self.text_original.setPlaceholderText('识别到的原文')
        layout.addWidget(self.text_original)

        self.text_translated = QTextEdit(self)
        self.text_translated.setPlaceholderText('翻译后的文本')
        layout.addWidget(self.text_translated)

        self.setLayout(layout)

    def select_area(self):
        self.hide()
        QApplication.processEvents()  # 防止界面卡死
        self.selection_window = SelectionWindow(self)
        self.selection_window.show()
        self.selection_window.setGeometry(QApplication.desktop().geometry())

    # def on_area_selected(self, rect: QRect):
    #     """选区完成后的回调函数"""
    #     self.selected_rect = rect
    #     if self.selected_rect:
    #         print(f"已选定区域: {self.selected_rect}")
    #         self.show()
    #         self.update()  # 请求重绘选区框
    #         self.timer.start(1000)  # 每秒处理一次

    # def paintEvent(self, event):
    #     """绘制用户选定的区域边框"""
    #     if self.selected_rect:
    #         painter = QPainter(self)
    #         pen = QPen(QColor(255, 0, 0), 2)  # 红色边框
    #         painter.setPen(pen)
    #         painter.drawRect(self.selected_rect)

    def process(self):
        """核心处理逻辑：截图 -> OCR -> 翻译 -> 显示"""
        if not self.selected_rect:
            print("未选定区域")
            return

        img = self.capture.capture_area(self.selected_rect)
        text = self.ocr.extract_text(img)

        if text.strip() and text != self.last_text:
            self.last_text = text
            self.text_original.setPlainText(text)
            translation = self.translator.translate(text)
            self.text_translated.setPlainText(translation)
