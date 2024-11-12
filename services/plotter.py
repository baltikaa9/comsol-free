import numpy as np
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.figure import Figure
from pandas import Series


class Plotter:
    @staticmethod
    def plot_geometry(ax: Axes):
        s = np.linspace(0, 1, 1000)
        c = 1.8
        x = c * s - c
        y = c * 0.594689181 * (0.298222773 * np.sqrt(
            s) - 0.127125232 * s - 0.357907906 * s ** 2 + 0.291984971 * s ** 3 - 0.105174696 * s ** 4)

        ax.plot(x, y, color='black')
        ax.plot(x, -y, color='black')

    @staticmethod
    def plot_data(fig: Figure, ax: Axes, x: Series, y: Series, z: Series, *args, **kwargs) -> Colorbar:
        plot = ax.tricontourf(x, y, z, *args, **kwargs)
        return fig.colorbar(plot)
