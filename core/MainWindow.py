# MainWindow.py
# 主界面，负责管理整体流程：选区、截图、OCR识别、翻译显示

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QApplication, QComboBox, QHBoxLayout
from PyQt5.QtCore import QTimer, QRect
from SelectionOverlay import SelectionWindow
from ScreenCapture import ScreenCapture
from OcrEngine import OcrEngine
from TranslatorEngine import TranslatorEngine
import logging
from DraggableOverlay import DraggableOverlay


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 支持的语言代码映射
        # Language code mappings that align with OCR language codes
        self.languages = {
            'Chinese': 'chi_sim',  # Aligned with LANG_MAPPINGS
            'English': 'eng',
            'Japanese': 'jpn',
            'Korean': 'kor',
            # 'French': 'fra',
            # 'German': 'deu',
            # 'Spanish': 'spa',
            'Chinese (Traditional)': 'chi_tra'
        }

        # Mapping from OCR language codes to Google Translate language codes
        self.translator_codes = {
            'chi_sim': 'zh-cn',
            'eng': 'en',
            'jpn': 'ja',
            'kor': 'ko',
            # 'fra': 'fr',
            # 'deu': 'de',
            # 'spa': 'es',
            'chi_tra': 'zh-tw'
        }

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
        self.draggable_overlay = None

        # 保存上一次识别到的文字，用来对比
        self.last_text = ""

        # 保存上一次识别到的文字，用来对比
        self.last_text = ""

    def initUI(self):
        self.setWindowTitle('translation area')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # 语言选择区域
        lang_layout = QHBoxLayout()

        self.src_lang = QComboBox()
        self.src_lang.addItems(self.languages.keys())
        self.src_lang.setCurrentText('English')
        lang_layout.addWidget(self.src_lang)

        self.dest_lang = QComboBox()
        self.dest_lang.addItems(self.languages.keys())
        self.dest_lang.setCurrentText('Chinese')
        lang_layout.addWidget(self.dest_lang)

        layout.addLayout(lang_layout)

        # 按钮：点击后开始选择区域
        self.btn_select = QPushButton('draw rectangle', self)
        self.btn_select.clicked.connect(self.select_area)
        layout.addWidget(self.btn_select)

        # 显示识别出的原文
        self.text_original = QTextEdit(self)
        self.text_original.setPlaceholderText('source text')
        layout.addWidget(self.text_original)

        # 显示翻译后的内容
        self.text_translated = QTextEdit(self)
        self.text_translated.setPlaceholderText('translated text')
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
        # if self.selected_rect:
        #     logging.info(f"selected area: {rect}")
        #     self.overlay.set_rect(rect)  # 显示浮窗选区
        #     self.show()

        if self.selected_rect:
            logging.info(f"selected area: {rect}")
            # Create draggable overlay instead of normal overlay
            if self.draggable_overlay:
                self.draggable_overlay.close()
            self.draggable_overlay = DraggableOverlay(rect)
            self.draggable_overlay.show()
            self.show()
        self.timer.start(500)  # 每秒处理一次

    def process(self):
        if not self.selected_rect:
            logging.warning("no area selected")
            return

        if not self.selected_rect or not self.draggable_overlay:
            return

        # Don't process if overlay is being dragged
        if self.draggable_overlay.dragging:
            logging.debug("Overlay is being dragged, skipping process")
            return

        self.selected_rect = self.draggable_overlay.geometry()

        try:
            # Get screenshot
            img = self.capture.capture_area(self.selected_rect)
            if img is None:
                logging.error("Failed to capture screen area")
                return

            # OCR recognition
            text = self.ocr.extract_text(img, self.languages[self.src_lang.currentText()])
            if not text:
                logging.debug("OCR result is empty")
                return

            # Compare text (ignoring whitespace)
            current_text = text.strip()
            last_text = self.last_text.strip()

            if current_text != last_text:
                self.last_text = text
                self.text_original.setPlainText(text)

                # Get source and target language codes
                try:
                    src_lang = self.languages[self.src_lang.currentText()]
                    dest_lang = self.languages[self.dest_lang.currentText()]

                    # Translate
                    translation = self.translator.translate(
                        text,
                        src=self.translator_codes[src_lang],
                        dest=self.translator_codes[dest_lang]
                    )
                    self.text_translated.setPlainText(translation)
                    logging.debug(f"Successfully translated text from {src_lang} to {dest_lang}")

                except KeyError as e:
                    logging.error(f"Invalid language code: {str(e)}")
                except Exception as e:
                    logging.error(f"Translation error: {str(e)}")

        except Exception as e:
            logging.error(f"Process error: {str(e)}")

