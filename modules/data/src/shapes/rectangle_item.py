from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsRectItem

from modules.data.src.widgets.edge_item import LineEdgeItem


class RectangleItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF):
        super().__init__(rect)
        self.edges: list = []
        self.generate_edges()


    def generate_edges(self):
        rect = self.rect()
        self.edges = [
            LineEdgeItem(rect.topLeft(), rect.topRight()),
            LineEdgeItem(rect.topRight(), rect.bottomRight()),
            LineEdgeItem(rect.bottomRight(), rect.bottomLeft()),
            LineEdgeItem(rect.bottomLeft(), rect.topLeft())
        ]
        for edge in self.edges:
            edge.setParentItem(self)
            edge.setFlag(QGraphicsItem.ItemIsSelectable, True)
