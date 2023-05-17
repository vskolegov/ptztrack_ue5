import sys

from PySide6.QtWidgets import QApplication

from frontend.controllers import PTZCameras
from frontend.windows import MainWindow

from backend.connector import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(PTZCameras())
    window.resize(1000, 600)
    window.setStyleSheet(open('frontend/styles/main.qss').read())
    window.show()
    sys.exit(app.exec())
