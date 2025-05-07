import itertools

from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsPathItem

_edge_id_counter = itertools.count(1)


def _next_edge_id() -> int:
    return next(_edge_id_counter)


class EdgeItem(QGraphicsPathItem):
    def __init__(self, path: QPainterPath, parent=None):
        super().__init__(path, parent)
        self.id = _next_edge_id()


class PathEdgeItem(QGraphicsPathItem):
    def __init__(self, path: QPainterPath, parent=None):
        super().__init__(path, parent)
        self.id = _next_edge_id()
