import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout,
    QDesktopWidget
)
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QIcon
from SelectionOverlay import SelectionWindow
from DraggableOverlay import DraggableOverlay
import logging

from Chat import TranslatorApp


class DraggableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(500, 80)
        self.setStyleSheet("background-color: #f2f2f2; border-radius: 10px;")

        # Position window at bottom-right corner of screen
        screen = QDesktopWidget().screenGeometry()
        window_geometry = self.geometry()
        x = screen.width() - window_geometry.width() - 20  # 20px margin from right
        y = screen.height() - window_geometry.height() - 40  # 40px margin from bottom
        self.move(x, y)

        # Initialize selection related attributes
        # Initialize selection related attributes
        self.selection_window = None
        self.selected_rect = None
        self.draggable_overlay = None

        self.window = TranslatorApp()

        self.initUI()
        self.oldPos = self.pos()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        icons = [
            ("🅧", self.on_close),
            ("🪟", self.on_button1),
            ("🖥️", self.translation),
            ("⬚", self.screen_trans),
            ("⛶", self.on_button4),
            ("⧉", self.on_button5),
        ]

        for icon, callback in icons:
            btn = QPushButton(icon)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                "background-color: white; border: 1px solid #ccc; border-radius: 5px;"
            )
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        # "选项" 和 "录制" 模拟
        option_label = QLabel("选项 ▼")
        # record_label = QLabel("录制")
        option_label.setFixedWidth(60)
        # record_label.setFixedWidth(40)

        layout.addWidget(option_label)
        # layout.addWidget(record_label)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def on_close(self):
        self.close()

    def on_button1(self):
        print("点击了按钮 1")

    def translation(self):
        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show()

    def screen_trans(self):
        """Implement area selection functionality"""
        self.hide()
        QApplication.processEvents()
        self.selection_window = SelectionWindow(self)
        self.selection_window.show()
        self.selection_window.setGeometry(QApplication.desktop().geometry())

    def on_button4(self):
        print("点击了按钮 4")

    def on_button5(self):
        print("点击了按钮 5")

    def on_area_selected(self, rect: QRect):
        """Callback when area is selected"""
        self.selected_rect = rect

        if self.selected_rect:
            logging.info(f"selected area: {rect}")
            # Create draggable overlay
            if self.draggable_overlay:
                self.draggable_overlay.close()
            self.draggable_overlay = DraggableOverlay(rect)
            self.draggable_overlay.show()

            # Create and show translation window
            if not hasattr(self, 'translation_window'):
                from TranslationWindow import TranslationWindow
                self.translation_window = TranslationWindow(self)
            self.translation_window.draggable_overlay = self.draggable_overlay
            self.translation_window.on_area_selected(rect)

            self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DraggableWindow()
    window.show()
    sys.exit(app.exec_())
