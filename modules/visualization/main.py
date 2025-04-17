import logging
import sys

from PySide6.QtWidgets import QApplication

from src.main_window import MainWindow

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s', stream=sys.stdout)

    app = QApplication(sys.argv)
    window = MainWindow()

    app.exec()
