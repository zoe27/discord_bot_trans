from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QApplication, QComboBox, QHBoxLayout, QLabel
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QTimer
import sys
import logging

# 安装： pip install googletrans==4.0.0-rc1
from googletrans import Translator


class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.SizeAllCursor)  # Set cursor to four-directional arrow

        # Add variables for tracking mouse position
        self.dragging = False
        self.offset = None

        layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def set_text(self, text):
        self.label.setText(text)
        self.adjustSize()


class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.setWindowTitle("实时翻译器")
        self.resize(500, 400)

        self.translator = Translator()
        self.last_text = ""  # 存储上次翻译的文本
        self.floating_window = FloatingWindow()

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_and_translate)
        self.timer.start(1000)  # 每秒检查一次

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 语言选择布局
        lang_layout = QHBoxLayout()

        # 自动翻译开关
        self.auto_translate = QPushButton("停止自动翻译")
        self.auto_translate.setCheckable(True)
        self.auto_translate.setChecked(True)
        self.auto_translate.clicked.connect(self.toggle_auto_translate)
        lang_layout.addWidget(self.auto_translate)

        # 复制按钮
        self.copy_button = QPushButton("复制翻译")
        self.copy_button.clicked.connect(self.copy_translation)
        lang_layout.addWidget(self.copy_button)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "zh-CN",  # 中文
            "en",  # 英文
            "ja",  # 日语
            "ko",  # 韩语
            "fr",  # 法语
            "de",  # 德语
        ])
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.lang_combo)

        layout.addLayout(lang_layout)

        # 合并的文本框
        self.combined_text = QTextEdit()
        self.combined_text.setPlaceholderText("在此输入要翻译的内容")
        layout.addWidget(self.combined_text)

        self.setLayout(layout)

    def toggle_auto_translate(self):
        if self.auto_translate.isChecked():
            self.timer.start()
            self.auto_translate.setText("停止自动翻译")
        else:
            self.timer.stop()
            self.auto_translate.setText("开始自动翻译")

    def check_and_translate(self):
        if not self.auto_translate.isChecked():
            return

        text = self.combined_text.toPlainText()
        input_text = text.split('\n\n---\n\n')[-1].strip()

        # 只在文本发生变化时才翻译
        if input_text and input_text != self.last_text:
            self.last_text = input_text
            self.translate_text()

    def on_language_changed(self, new_lang):
        """Handle language change event"""
        self.logger.info(f"语言切换为: {new_lang}")
        self.translate_text()

    def translate_text(self):
        text = self.combined_text.toPlainText()
        input_text = text.split('\n\n---\n\n')[-1].strip()
        if not input_text:
            return

        target_lang = self.lang_combo.currentText()
        self.logger.info(f"正在翻译文本到 {target_lang}")

        try:
            result = self.translator.translate(input_text, dest=target_lang)
            translated_text = result.text
            # 更新悬浮窗内容
            self.floating_window.set_text(translated_text)
            # Only set initial position if window hasn't been moved by user
            if not self.floating_window.dragging:
                pos = self.combined_text.mapToGlobal(self.combined_text.rect().topLeft())
                self.floating_window.move(pos.x(), pos.y() - self.floating_window.height())
            self.floating_window.show()
            # 更新文本框内容
            # Keep only the input text in the text box
            # self.combined_text.setPlainText(input_text)
            self.logger.info("翻译成功")
        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            self.combined_text.setPlainText(f"错误: {error_msg}\n\n---\n\n{input_text}")
            self.logger.error(error_msg)

    def copy_translation(self):
        """Copy translated text from floating window to clipboard"""
        translated_text = self.floating_window.label.text()
        if translated_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(translated_text)
            self.logger.info("翻译结果已复制到剪贴板")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = TranslatorApp()
#     window.show()
#     sys.exit(app.exec_())