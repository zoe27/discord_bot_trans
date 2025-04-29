# core/SelectionOverlay.py

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QGuiApplication

class SelectionOverlay(QWidget):
    regionSelected = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)

        self.start_pos = None
        self.end_pos = None
        self.background = self.capture_fullscreen()

        # 支持多显示器，自动全屏
        geometry = QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geometry)

    def capture_fullscreen(self):
        # 支持多显示器截图
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0)
        return screenshot

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPos()
            self.end_pos = self.start_pos
            self.update()
        elif event.button() == Qt.RightButton:
            # 右键取消选择
            self.close()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            self.end_pos = event.globalPos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos).normalized()
            self.regionSelected.emit(rect)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # 按 ESC 取消选择
            self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 先绘制截图背景
        painter.drawPixmap(self.rect(), self.background)

        # 覆盖一层透明黑色
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        # 如果用户在拉框，绘制红框
        if self.start_pos and self.end_pos:
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)
            selection_rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.drawRect(selection_rect)
