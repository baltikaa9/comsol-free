from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor
from PySide6.QtGui import QPainterPath
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsPathItem


class DraggablePoint(QGraphicsEllipseItem):
    def __init__(self, curve_ref, index, center: QPointF, radius=5.0):
        super().__init__(-radius, -radius, 2*radius, 2*radius)
        self.curve_ref = curve_ref
        self.index = index
        self.setBrush(QBrush(QColor("blue")))
        self.setPen(QPen(Qt.black))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsScenePositionChanges | QGraphicsItem.ItemIsSelectable)
        self.setZValue(10)
        self.setPos(center)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemScenePositionHasChanged:
            if self.curve_ref:
                self.curve_ref.update_path()
        return super().itemChange(change, value)


class EditableBezierCurveItem(QGraphicsPathItem):
    def __init__(self, points, pen=None, scene=None):
        super().__init__()
        self.points = points[:]
        self.point_items = []
        self.setPen(pen or QPen(Qt.black, 0.02))
        self.setZValue(1)
        self.scene_ref = scene
        self._init_points()
        self.update_path()

    def _init_points(self):
        for i, pt in enumerate(self.points):
            p_item = DraggablePoint(self, i, pt)
            self.point_items.append(p_item)
            if self.scene_ref:
                self.scene_ref.addItem(p_item)

    def update_path(self):
        path = QPainterPath()
        if not self.point_items or len(self.point_items) < 2:
            self.setPath(path)
            return

        points = [item.scenePos() for item in self.point_items]
        path.moveTo(points[0])

        for i in range(1, len(points)):
            p0 = points[i - 1]
            p1 = points[i]

            if i == 1:
                ctrl1 = p0 + (p1 - p0) * 0.33
            else:
                prev_p = points[i - 2]
                ctrl1 = p0 + (p0 - prev_p) * 0.33

            if i == len(points) - 1:
                ctrl2 = p1 - (p1 - p0) * 0.33
            else:
                next_p = points[i + 1]
                ctrl2 = p1 - (next_p - p1) * 0.33

            path.cubicTo(ctrl1, ctrl2, p1)

        self.setPath(path)

    def add_to_scene(self):
        if self.scene_ref:
            self.scene_ref.addItem(self)
            for p in self.point_items:
                self.scene_ref.addItem(p)

    def remove_from_scene(self):
        for p in self.point_items:
            if p.scene():
                p.scene().removeItem(p)
        if self.scene():
            self.scene().removeItem(self)