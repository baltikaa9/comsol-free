import uuid
from abc import ABC

from PySide6.QtCore import QLineF
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtWidgets import QGraphicsPathItem


class EdgeItem(ABC):
    ...

class PathEdgeItem(QGraphicsPathItem):
    def __init__(self, path: QPainterPath, parent=None):
        super().__init__(path, parent)
        self.id = uuid.uuid4().hex

class LineEdgeItem(QGraphicsLineItem):
    def __init__(self, p1: QPointF, p2: QPointF, parent=None):
        super().__init__(QLineF(p1, p2), parent)
        self.id = uuid.uuid4().hex

class ArcEdgeItem(QGraphicsPathItem):
    def __init__(self, rect, start_angle, arc_len):
        path = QPainterPath()
        path.arcTo(rect, start_angle, arc_len)
        super().__init__(path)
        self.id = uuid.uuid4().hex