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
        self.dragging = False
        self.offset = None

        # Remove window decorations and keep on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.resize(450, 200)  # Smaller default size

        self.translator = Translator()
        self.last_text = ""  # 存储上次翻译的文本
        self.floating_window = FloatingWindow()

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_and_translate)
        self.timer.start(1000)  # 每秒检查一次
        self.init_ui()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPos() - self.offset
            self.move(new_pos)
            # Update floating window position
            self.update_floating_window_position()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def update_floating_window_position(self):
        pos = self.combined_text.mapToGlobal(self.combined_text.rect().topLeft())
        self.floating_window.move(pos.x(), pos.y() - self.floating_window.height())

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins for a cleaner look
        # Left side - Text input
        text_container = QWidget()
        text_container.setMinimumWidth(300)  # Slightly smaller width
        text_layout = QVBoxLayout(text_container)

        self.combined_text = QTextEdit()
        self.combined_text.setPlaceholderText("在此输入要翻译的内容")
        text_layout.addWidget(self.combined_text)
        layout.addWidget(text_container)

        # Right side - Language selection
        lang_container = QWidget()
        lang_container.setMaximumWidth(80)  # Slightly smaller width
        lang_layout = QVBoxLayout(lang_container)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setAlignment(Qt.AlignTop)

        # Language selector
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

        layout.addWidget(lang_container)
        self.setLayout(layout)

    def check_and_translate(self):
        # Skip translation if window is being dragged
        if self.dragging:
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
            # if not self.floating_window.dragging:
            #     pos = self.combined_text.mapToGlobal(self.combined_text.rect().topLeft())
            #     self.floating_window.move(pos.x(), pos.y() - self.floating_window.height())
            # self.floating_window.show()

            if not self.floating_window.dragging:
                self.update_floating_window_position()
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec_())