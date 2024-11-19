import numpy as np
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.figure import Figure
from pandas import Series
from scipy.interpolate import griddata


class Plotter:
    @staticmethod
    def plot_geometry(ax: Axes):
        s = np.linspace(0, 1, 1000)
        c = 1.8
        x = c * s - c
        y = c * 0.594689181 * (0.298222773 * np.sqrt(s) -
                    0.127125232 * s - 0.357907906 * s ** 2 + 0.291984971 * s ** 3 - 0.105174696 * s ** 4)

        ax.plot(x, y, color='r')
        ax.plot(x, -y, color='r')

    @staticmethod
    def plot_surface(fig: Figure, ax: Axes, x: Series, y: Series, z: Series, *args, **kwargs) -> Colorbar:
        plot = ax.tricontourf(x, y, z, *args, **kwargs)
        return fig.colorbar(plot)

    @staticmethod
    def plot_streamline(fig: Figure, ax: Axes, x: Series, y: Series, u: Series, v: Series, *args, **kwargs):
        x = x.values
        y = y.values
        u = u.values
        v = v.values

        xi = np.linspace(-5, 5, 3000)
        yi = np.linspace(-5, 5, 3000)

        ui = griddata((x, y), u, (xi[None, :], yi[:, None]), method='cubic')
        vi = griddata((x, y), v, (xi[None, :], yi[:, None]), method='cubic')

        ax.streamplot(
            xi, yi, ui, vi,
            density=(0.5, 10),
            color='black',
            broken_streamlines=False,
            start_points=np.array(([0 for _ in np.arange(-2, 2, 0.05)], np.arange(-2, 2, 0.05))).T
        )
