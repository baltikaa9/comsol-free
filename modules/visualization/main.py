import logging
import sys

import matplotlib
from PySide6.QtWidgets import QApplication

from src.main_window import MainWindow

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s', stream=sys.stdout)

    font = {
        'family': 'normal',
        'size': 20
    }

    matplotlib.rc('font', **font)

    app = QApplication(sys.argv)
    window = MainWindow()

    app.exec()
