from PySide6.QtCore import QLineF
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsLineItem

from src.widgets.edge_item import EdgeItem


class LineItem(QGraphicsLineItem):
    def __init__(self, line: QLineF):
        super().__init__(line)
        self.edges: list[EdgeItem] = []
        self.generate_edges()

    def generate_edges(self):
        line = self.line()
        self.edges = [EdgeItem(self.get_path(line.p1(), line.p2()))]
        self.edges[0].setParentItem(self)
        self.edges[0].setFlag(QGraphicsItem.ItemIsSelectable, True)

    @staticmethod
    def get_path(p1: QPointF, p2: QPointF) -> QPainterPath:
        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        return path

    def __repr__(self):
        return f'{self.__class__.__name__}({[edge.path() for edge in self.edges]})'
