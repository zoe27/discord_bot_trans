from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor


class OverlayDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.rect_to_draw = None

    def set_rect(self, rect: QRect):
        self.rect_to_draw = rect

        # 重定位并调整自身大小以匹配选区
        self.setGeometry(rect)
        self.show()
        self.update()

    def paintEvent(self, event):
        if self.rect_to_draw:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(QColor(0, 150, 255, 180), 3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(0, 0, self.width()-1, self.height()-1)
