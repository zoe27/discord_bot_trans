# SelectionOverlay.py
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QGuiApplication
from SelectionFrame import SelectionFrame  # ✅ 新增导入

class SelectionWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)

        self.start_pos = None
        self.end_pos = None
        self.background = self.capture_fullscreen()

        geometry = QGuiApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geometry)

    def capture_fullscreen(self):
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0)
        return screenshot

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPos()
            self.end_pos = self.start_pos
            self.update()
        elif event.button() == Qt.RightButton:
            self.close()
            self.parent.show()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            self.end_pos = event.globalPos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos and self.end_pos:
            self.finish_selection()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            self.parent.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(self.rect(), self.background)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))  # 遮罩

        if self.start_pos and self.end_pos:
            pen = QPen(Qt.white, 2, Qt.DashLine)
            painter.setPen(pen)
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.drawRect(rect)

    def finish_selection(self):
        rect = QRect(self.start_pos, self.end_pos).normalized()
        self.parent.selected_rect = rect

        # ✅ 显示持久框
        self.selection_frame = SelectionFrame(rect)

        self.close()
        self.parent.show()
        if hasattr(self.parent, 'timer'):
            self.parent.timer.start(1000)
        # SelectionOverlay.py 中最后需要回调 MainWindow
        self.parent.on_area_selected(rect)

