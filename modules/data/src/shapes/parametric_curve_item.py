from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsPathItem

from modules.data.src.widgets.edge_item import EdgeItem


class ParametricCurveItem(QGraphicsPathItem):
    def __init__(self, path: QPainterPath):
        super().__init__(path)
        self.edges: list[EdgeItem] = []
        self.generate_edges()

    def generate_edges(self):
        self.edges = [EdgeItem(self.path(), self)]
        self.edges[0].setParentItem(self)
        self.edges[0].setFlag(QGraphicsItem.ItemIsSelectable, True)

    def __repr__(self):
        return f'{self.__class__.__name__}({[edge.path() for edge in self.edges]})'
