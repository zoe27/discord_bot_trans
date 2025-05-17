from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QMouseEvent
import logging

from ScreenCapture import ScreenCapture
from OcrEngine import OcrEngine
from TranslatorEngine import TranslatorEngine


class TranslationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        # 初始化核心功能模块
        self.capture = ScreenCapture()
        self.ocr = OcrEngine()
        self.translator = TranslatorEngine()
        self.last_text = ""
        self.selected_rect = None
        self.logger = logging.getLogger(__name__)

        # Mouse tracking variables
        self.dragging = False
        self.drag_position = QPoint()
        self.last_process_time = 0
        self.setCursor(Qt.SizeAllCursor)
        self.setMouseTracking(True)

        # Initialize timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.process)

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

    def initUI(self):
        """Initialize the UI components"""
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Main layout
        layout = QVBoxLayout()

        # Translation label
        self.translation_label = QLabel()
        self.translation_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
                min-width: 200px;
                cursor: size_all;
            }
        """)
        layout.addWidget(self.translation_label)

        self.setLayout(layout)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            # Resume processing after drag ends
            event.accept()

    def on_area_selected(self, rect):
        """Callback when area is selected"""
        self.selected_rect = rect
        if not self.selected_rect:
            self.logger.warning("No area selected")
            return

        # Show translation window
        if not self.isVisible():
            self.show()
        # Position window near selected area
        self.move(rect.x(), rect.y() - self.height())

        # Start the periodic update timer
        self.timer.start(500)  # Check every 500ms

    def process(self):
        """Periodically process the selected area for updates"""
        # Skip processing if dragging
        if self.dragging:
            # self.timer.stop()
            return

        self.selected_rect = self.draggable_overlay.geometry()

        if not self.selected_rect:
            return

        try:
            # Capture and process the selected area
            img = self.capture.capture_area(self.selected_rect)
            if img is None:
                self.logger.error("Failed to capture screen area")
                return

            # Perform OCR
            text = self.ocr.extract_text(img, 'eng')
            if not text:
                self.logger.debug("OCR result is empty")
                return

            # Compare with last text (ignore whitespace)
            current_text = text.strip()
            last_text = self.last_text.strip()

            # Only proceed with translation if text has changed
            if current_text and current_text != last_text:
                self.last_text = text
                # Translate the text
                translation = self.translator.translate(
                    text,
                    src='en',
                    dest='zh-cn'
                )
                self.translation_label.setText(translation)
                self.logger.debug("Translation updated successfully")
            else:
                self.logger.debug("Text unchanged, skipping translation")

        except Exception as e:
            self.logger.error(f"Process error: {str(e)}")