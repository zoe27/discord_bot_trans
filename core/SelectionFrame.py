# SelectionFrame.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor


class SelectionFrame(QWidget):
    def __init__(self, rect: QRect):
        super().__init__()
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus)
        # self.setWindowFlags(
        #     # Qt.FramelessWindowHint |
        #     Qt.WindowStaysOnTopHint |
        #     Qt.Tool |
        #     Qt.WindowDoesNotAcceptFocus |
        #     Qt.X11BypassWindowManagerHint |
        #     Qt.SubWindow  # Add SubWindow flag to maintain topmost status
        # )
        self.setAttribute(Qt.WA_ShowWithoutActivating)  # Show window without focus
        # self.setAttribute(Qt.WA_X11NetWmWindowTypeUtility)  # Set as utility window
        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable translucent background
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Make mouse events pass through
        self.setAttribute(Qt.WA_NoSystemBackground)  # Remove system background
        self.setAttribute(Qt.WA_AlwaysStackOnTop)  # Ensure window stays on top
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setWindowTitle("Selection Frame")
        self.setGeometry(rect)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(0, 120, 215), 2)  # 蓝色边框
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        # painter.setRenderHint(QPainter.Antialiasing)
        painter.drawRect(self.rect().adjusted(1, 1, -2, -2))
