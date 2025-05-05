from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsEllipseItem

from modules.data.src.widgets.edge_item import ArcEdgeItem
from modules.data.src.widgets.edge_item import EdgeItem


class EllipseItem(QGraphicsEllipseItem):
    def __init__(self, rect: QRectF):
        super().__init__(rect)
        self.edges: list[EdgeItem] = []
        self.generate_edges()

    def generate_edges(self):
        rect = self.rect()
        angles = [0, 90, 180, 270]
        for start in angles:
            edge = ArcEdgeItem(rect, start, 90)
            edge.setParentItem(self)
            edge.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.edges.append(edge)