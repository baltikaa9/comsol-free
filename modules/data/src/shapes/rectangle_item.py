from PySide6.QtCore import QPointF
from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsRectItem

from modules.data.src.widgets.edge_item import EdgeItem


class RectangleItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF):
        super().__init__(rect)
        self.edges: list[EdgeItem] = []
        self.generate_edges()


    def generate_edges(self):
        rect = self.rect()
        self.edges = [
            EdgeItem(self.get_path(rect.bottomLeft(), rect.bottomRight())),
            EdgeItem(self.get_path(rect.bottomRight(), rect.topRight())),
            EdgeItem(self.get_path(rect.topRight(), rect.topLeft())),
            EdgeItem(self.get_path(rect.topLeft(), rect.bottomLeft()))
        ]
        for edge in self.edges:
            edge.setParentItem(self)
            edge.setFlag(QGraphicsItem.ItemIsSelectable, True)

    @staticmethod
    def get_path(p1: QPointF, p2: QPointF) -> QPainterPath:
        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        return path

    def __repr__(self):
        return f'{self.__class__.__name__}({[edge.path() for edge in self.edges]})'
