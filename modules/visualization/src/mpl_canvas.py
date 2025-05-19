import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, num=1, width=5, height=4, dpi=100, projection=None, title=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#fff')
        self.ax = self.fig.add_subplot(111, projection=projection, facecolor='#fff')
        if title:
            self.ax.set_title(title)
        super().__init__(self.fig)
