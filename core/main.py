import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow


def setup_logging():
    if getattr(sys, 'frozen', False):  # .app / EXE 打包后
        # log_dir = os.path.expanduser('~/Library/Logs/ScreenTranslator')
        if sys.platform == 'win32':
            log_dir = os.path.join(os.getenv('APPDATA'), 'ScreenTranslator')
        else:  # macOS
            log_dir = os.path.expanduser('~/Library/Logs/ScreenTranslator')
    else:  # 脚本运行
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'my_ocr_app.log')

    # 滚动日志，最大 5MB，最多保留 3 个备份
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

    logging.info("=== 日志系统初始化完成 - {} ===".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    logging.info(f"📁 日志路径: {log_file}")


if __name__ == "__main__":
    setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logging.info("🚀 应用启动")
    sys.exit(app.exec_())
