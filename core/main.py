# 启动程序，创建 QApplication 实例，显示主界面
# main.py
# 入口文件，启动整个应用程序
import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

