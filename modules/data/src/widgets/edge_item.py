import itertools

from PySide6.QtCore import QLineF
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtWidgets import QGraphicsPathItem

_edge_id_counter = itertools.count(1)

def _next_edge_id() -> int:
    return next(_edge_id_counter)

class PathEdgeItem(QGraphicsPathItem):
    def __init__(self, path: QPainterPath, parent=None):
        super().__init__(path, parent)
        self.id = _next_edge_id()

class LineEdgeItem(QGraphicsLineItem):
    def __init__(self, p1: QPointF, p2: QPointF, parent=None):
        super().__init__(QLineF(p1, p2), parent)
        self.id = _next_edge_id()

class ArcEdgeItem(QGraphicsPathItem):
    def __init__(self, rect, start_angle, arc_len):
        path = QPainterPath()
        path.arcTo(rect, start_angle, arc_len)
        super().__init__(path)
        self.id = _next_edge_id()
        self.rect = rect  # Сохраняем параметры
        self.start_angle = start_angle
        self.arc_len = arc_len

if __name__ == '__main__':
    e = LineEdgeItem(QPointF(0, 0), QPointF(1, 1))
