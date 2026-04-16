import logging
import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
        stream=sys.stdout,
    )

    app = QApplication(sys.argv)

    # Установка иконки приложения
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "src", "assets", "icon.svg")

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    app.exec()
