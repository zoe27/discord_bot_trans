# SelectionFrame.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor


class SelectionFrame(QWidget):
    def __init__(self, rect: QRect):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(rect)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(0, 120, 215), 2)  # 蓝色边框
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.rect().adjusted(1, 1, -2, -2))
