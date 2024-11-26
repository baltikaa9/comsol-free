import logging
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from mpl_canvas import MplCanvas
from services.data_parser import DataParser
from services.plotter import Plotter
from ui.comsol import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger(__name__)

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

        self.ui.pushButton_select_file.clicked.connect(self.__select_file)

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

        if not data_path or not levels:
            return

        Plotter.plot_geometry(self.canvas_visualization.ax, color)

        data = DataParser(data_path).parse()

        self.color_bar = Plotter.plot_surface(
            self.canvas_visualization.fig,
            self.canvas_visualization.ax,
            data['x'],
            data['y'],
            data['p' if expression else 'U'],
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
                data['u'],
                data['v'],
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

    def __select_file(self):
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a file',
            dir=os.getcwd(),
            filter='Text File (*.txt)',
        )

        self.logger.debug(f'Выбран файл: {response}')

        self.ui.lineEdit_data_path.setText(response[0])
