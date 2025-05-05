from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsPathItem


class BooleanShapeItem(QGraphicsPathItem):
    def __init__(self, path: QPainterPath, p1, p2):
        super().__init__(path)
        self.edges = []
        self.generate_edges(p1, p2)
        c=1

    def generate_edges(self, p1, p2):
        self.edges = p1.edges + p2.edges
        for edge in self.edges:
            edge.setParentItem(self)
            edge.setFlag(QGraphicsItem.ItemIsSelectable, True)
