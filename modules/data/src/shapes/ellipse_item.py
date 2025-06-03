from PySide6.QtCore import QPointF
from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtWidgets import QGraphicsItem

from src.widgets.edge_item import EdgeItem


class EllipseItem(QGraphicsEllipseItem):
    def __init__(self, rect: QRectF):
        super().__init__(rect)
        self.edges: list[EdgeItem] = []
        self.generate_edges()

    def generate_edges(self):
        rect = self.rect()
        points = {
            0: QPointF(rect.right(), rect.center().y()),
            90: QPointF(rect.center().x(), rect.top()),
            180: QPointF(rect.left(), rect.center().y()),
            270: QPointF(rect.center().x(), rect.bottom()),
        }

        for angle, start in points.items():
            edge = EdgeItem(self.get_path(start, rect, angle))
            edge.setParentItem(self)
            edge.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.edges.append(edge)

    @staticmethod
    def get_path(p: QPointF, rect: QRectF, angle: float) -> QPainterPath:
        path = QPainterPath()
        path.moveTo(p)
        path.arcTo(rect, angle, 90)
        return path

    def __repr__(self):
        return f'{self.__class__.__name__}({[edge.path() for edge in self.edges]})'

if __name__ == '__main__':
    el = EllipseItem(QRectF(0, 0, 100, 100))
    print(el.rect())
