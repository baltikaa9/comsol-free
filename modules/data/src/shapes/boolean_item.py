from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsPathItem

from src.widgets.edge_item import EdgeItem


class BooleanShapeItem(QGraphicsPathItem):
    def __init__(self, path: QPainterPath, p1, p2):
        super().__init__(path)
        self.edges: list[EdgeItem] = []
        self.generate_edges(p1, p2)

    def generate_edges(self, p1, p2):
        self.edges = p1.edges.copy() + p2.edges.copy()
        for edge in self.edges:
            edge.setParentItem(self)
            edge.setFlag(QGraphicsItem.ItemIsSelectable, True)
        ...

    def __repr__(self):
        return f'{self.__class__.__name__}({[edge.path() for edge in self.edges]})'
