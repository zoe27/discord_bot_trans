from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox
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
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Main layout
        layout = QVBoxLayout()

        # Source and target language selection
        lang_layout = QHBoxLayout()

        self.src_lang = QComboBox()
        self.src_lang.addItems(self.languages.keys())
        self.src_lang.setCurrentText('English')
        self.src_lang.setStyleSheet("""
                    QComboBox {
                        background-color: rgba(0, 0, 0, 0.8);
                        color: white;
                        padding: 5px;
                        border-radius: 5px;
                        border: 1px solid rgba(255, 255, 255, 0.3);
                    }
                    QComboBox::drop-down {
                        border: none;
                        width: 20px;
                    }
                    QComboBox::down-arrow {
                        width: 12px;
                        height: 12px;
                        border: 2px solid white;
                        border-width: 0 2px 2px 0;
                        transform: rotate(45deg);
                        margin-top: -5px;
                    }
                    QComboBox QAbstractItemView {
                        background-color: rgba(0, 0, 0, 0.8);
                        color: white;
                        selection-background-color: rgba(255, 255, 255, 0.2);
                    }
                """)

        lang_layout.addWidget(self.src_lang)

        self.dest_lang = QComboBox()
        self.dest_lang.addItems(self.languages.keys())
        self.dest_lang.setCurrentText('Chinese')
        self.dest_lang.setStyleSheet("""
                    QComboBox {
                        background-color: rgba(0, 0, 0, 0.8);
                        color: white;
                        padding: 5px;
                        border-radius: 5px;
                        border: 1px solid rgba(255, 255, 255, 0.3);
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow {
                        image: none;
                    }
                    QComboBox QAbstractItemView {
                        background-color: rgba(0, 0, 0, 0.8);
                        color: white;
                        selection-background-color: rgba(255, 255, 255, 0.2);
                    }
                """)
        lang_layout.addWidget(self.dest_lang)

        # Show original text checkbox
        self.show_original = QCheckBox("Show Original")
        self.show_original.setStyleSheet("""
                    QCheckBox {
                        color: white;
                        background-color: rgba(0, 0, 0, 0.8);
                        padding: 5px;
                        border-radius: 5px;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                    }
                    QCheckBox::indicator:unchecked {
                        border: 1px solid rgba(255, 255, 255, 0.3);
                        background: rgba(0, 0, 0, 0.8);
                    }
                    QCheckBox::indicator:checked {
                        border: 1px solid rgba(255, 255, 255, 0.3);
                        background: rgba(255, 255, 255, 0.8);
                    }
                """)
        self.show_original.stateChanged.connect(self.handle_show_original)
        lang_layout.addWidget(self.show_original)

        layout.addLayout(lang_layout)

        # Original text label (hidden by default)
        self.original_label = QLabel()
        self.original_label.setStyleSheet("""
                    QLabel {
                        background-color: rgba(0, 0, 0, 0.8);
                        color: white;
                        padding: 10px;
                        border-radius: 5px;
                        min-width: 200px;
                    }
                """)
        self.original_label.hide()
        layout.addWidget(self.original_label)

        # Translation label
        self.translation_label = QLabel()
        self.translation_label.setStyleSheet("""
                    QLabel {
                        background-color: rgba(0, 0, 0, 0.8);
                        color: white;
                        padding: 10px;
                        border-radius: 5px;
                        min-width: 200px;
                    }
                """)
        layout.addWidget(self.translation_label)

        self.setLayout(layout)

    def handle_show_original(self, state):
        """Handle show original checkbox state change"""
        if state:
            self.original_label.setText(self.last_text)
            self.original_label.show()
        else:
            self.original_label.hide()

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
            src_lang = self.languages[self.src_lang.currentText()]
            text = self.ocr.extract_text(img, src_lang)

            if not text:
                self.logger.debug("OCR result is empty")
                return

            # Compare with last text (ignore whitespace)
            current_text = text.strip()
            last_text = self.last_text.strip()

            # Only proceed with translation if text has changed
            logging.info(f"Current text: {current_text}, Last text: {last_text}")
            if current_text and current_text != last_text:
                self.last_text = text
                # Update original text if showing
                if self.show_original.isChecked():
                    self.original_label.setText(text)
                    self.original_label.show()
                else:
                    self.original_label.hide()

                # Get translation language codes
                src_lang_code = self.translator_codes[src_lang]
                dest_lang_code = self.translator_codes[self.languages[self.dest_lang.currentText()]]

                # Translate the text
                translation = self.translator.translate(
                    text,
                    src=src_lang_code,
                    dest=dest_lang_code
                )
                self.translation_label.setText(translation)
                self.logger.debug("Translation updated successfully")
            else:
                self.logger.debug("Text unchanged, skipping translation")

        except Exception as e:
            print("Error during processing:", str(e))
            self.logger.error(f"Process error: {str(e)}")