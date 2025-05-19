from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QApplication, QComboBox, QHBoxLayout, QLabel
)
from PyQt5.QtCore import QTimer, Qt, QPoint, pyqtSignal, QObject
from PyQt5.QtGui import QPalette, QColor
from concurrent.futures import ThreadPoolExecutor
import sys
import logging
import time
from googletrans import Translator

class SignalHandler(QObject):
    update_translation = pyqtSignal(str)
    update_error = pyqtSignal(str, str)

class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.SizeAllCursor)

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
        self.last_text = ""
        self.last_process_time = time.time()
        self.process_interval = 0.5
        self.translation_cache = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=1)

        # 创建信号处理器
        self.signal_handler = SignalHandler()
        self.signal_handler.update_translation.connect(self.update_translation_ui)
        self.signal_handler.update_error.connect(self.update_error_ui)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.resize(450, 200)

        self.translator = Translator()
        self.floating_window = FloatingWindow()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_and_translate)
        self.timer.setInterval(500)
        self.timer.start()

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        text_container = QWidget()
        text_container.setMinimumWidth(300)
        text_layout = QVBoxLayout(text_container)

        self.combined_text = QTextEdit()
        self.combined_text.setPlaceholderText("在此输入要翻译的内容")
        text_layout.addWidget(self.combined_text)
        layout.addWidget(text_container)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignTop)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "zh-CN",
            "en",
            "ja",
            "ko",
            "fr",
            "de"
        ])
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        right_layout.addWidget(self.lang_combo)

        copy_button = QPushButton("复制")
        copy_button.clicked.connect(self.copy_translation)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 5px;
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        right_layout.addWidget(copy_button)

        layout.addWidget(right_container)
        self.setLayout(layout)

    def check_and_translate(self):
        """检查是否需要翻译（带防抖）"""
        if self.dragging:
            return

        current_time = time.time()
        if current_time - self.last_process_time < self.process_interval:
            return

        text = self.combined_text.toPlainText()
        input_text = text.split('\n\n---\n\n')[-1].strip()

        if input_text and input_text != self.last_text:
            self.last_text = input_text
            self.translate_text()
            self.last_process_time = current_time

    def translate_text(self):
        """处理翻译请求"""
        text = self.combined_text.toPlainText()
        input_text = text.split('\n\n---\n\n')[-1].strip()
        if not input_text:
            return

        target_lang = self.lang_combo.currentText()
        self.logger.info(f"正在翻译文本到 {target_lang}")

        # 检查缓存
        cache_key = f"{input_text}_{target_lang}"
        if cache_key in self.translation_cache:
            self.signal_handler.update_translation.emit(self.translation_cache[cache_key])
            return

        # 在线程池中执行翻译
        self.thread_pool.submit(self.translate_in_background, input_text, target_lang)

    def translate_in_background(self, text, target_lang):
        """在后台执行翻译"""
        try:
            result = self.translator.translate(text, dest=target_lang)
            translated_text = result.text

            # 更新缓存
            cache_key = f"{text}_{target_lang}"
            self.translation_cache[cache_key] = translated_text

            # 通过信号发送翻译结果到主线程
            self.signal_handler.update_translation.emit(translated_text)
            self.logger.info("翻译成功")

        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            self.signal_handler.update_error.emit(error_msg, text)
            self.logger.error(error_msg)

    def update_translation_ui(self, translated_text):
        """在主线程中更新UI（由信号触发）"""
        self.floating_window.set_text(translated_text)
        if not self.floating_window.dragging:
            self.update_floating_window_position()
        self.floating_window.show()

    def update_error_ui(self, error_msg, original_text):
        """在主线程中更新错误信息（由信号触发）"""
        self.combined_text.setPlainText(f"错误: {error_msg}\n\n---\n\n{original_text}")

    def update_floating_window_position(self):
        """更新悬浮窗位置"""
        pos = self.combined_text.mapToGlobal(self.combined_text.rect().topLeft())
        self.floating_window.move(pos.x(), pos.y() - self.floating_window.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPos() - self.offset
            self.move(new_pos)
            self.update_floating_window_position()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def on_language_changed(self, new_lang):
        """语言改变时的处理"""
        self.logger.info(f"语言切换为: {new_lang}")
        self.translate_text()

    def copy_translation(self):
        """复制翻译结果到剪贴板"""
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