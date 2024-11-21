import sys

import matplotlib
import numpy as np
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from services.data_parser import DataParser
from services.plotter import Plotter
from ui.comsol import Ui_MainWindow

matplotlib.use('Qt5Agg')

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, num=1, width=5, height=4, dpi=100, projection=None, title=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#f0f0f0')
        self.ax = self.fig.add_subplot(111, projection=projection, facecolor='#f0f0f0')
        if title:
            self.ax.set_title(title)
        super().__init__(self.fig)

class Comsol(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.canvas_visualization = None
        self.toolbar = None

        self.layout_visualization = QVBoxLayout()

        self.ui.widget_visualisation.setLayout(self.layout_visualization)

        self.ui.pushButton_plot.clicked.connect(self.__plot)

        self.ui.comboBox_expression.currentIndexChanged.connect(
            lambda: self.__toggle_streamlines_check_box(self.ui.comboBox_expression.currentIndex())
        )

        self.show()

    def __plot(self):
        if self.canvas_visualization:
            self.layout_visualization.removeWidget(self.canvas_visualization)
            self.layout_visualization.removeWidget(self.toolbar)
            self.canvas_visualization.deleteLater()
            self.toolbar.deleteLater()
            self.canvas_visualization.hide()
            self.toolbar.hide()

        self.canvas_visualization = MplCanvas(self, num=1, width=5, height=5, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas_visualization, self)

        self.layout_visualization.addWidget(self.canvas_visualization)
        self.layout_visualization.addWidget(self.toolbar)

        data_path, expression, stream_lines, levels, color = self.__get_plot_settings()

        Plotter.plot_geometry(self.canvas_visualization.ax, color)

        print(data_path, expression, stream_lines, levels)

        if not data_path or not levels:
            return

        data = DataParser(data_path).parse()

        print(data)

        self.color_bar = Plotter.plot_surface(
            self.canvas_visualization.fig,
            self.canvas_visualization.ax,
            data['x'],
            data['y'],
            data['p (Pa) @ alpha=18' if expression else 'spf.U (m/s) @ alpha=18'],
            levels=levels,
            cmap='rainbow',
        )

        self.canvas_visualization.ax.set_title('Поле скоростей' if not expression else 'Поле давления')

        if stream_lines:
            Plotter.plot_streamline(
                self.canvas_visualization.fig,
                self.canvas_visualization.ax,
                data['x'],
                data['y'],
                data['u (m/s) @ alpha=18'],
                data['v (m/s) @ alpha=18'],
            )

    def __get_plot_settings(self) -> tuple[str, int, bool, int, str]:
        data_path = self.ui.lineEdit_data_path.text()
        expression = self.ui.comboBox_expression.currentIndex()
        stream_lines = self.ui.checkBox_stream_lines.isChecked()
        levels = self.ui.lineEdit_levels.text()
        color = self.ui.lineEdit_geometry_color.text()
        return data_path, expression, stream_lines, int(levels), color

    def __toggle_streamlines_check_box(self, current_index: int):
        self.ui.checkBox_stream_lines.setDisabled(current_index != 0)
        if current_index != 0:
            self.ui.checkBox_stream_lines.setCheckState(Qt.CheckState.Unchecked)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Comsol()

    app.exec()
