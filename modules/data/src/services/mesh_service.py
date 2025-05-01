from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainterPath
from PySide6.QtGui import QPainterPathStroker
from PySide6.QtGui import QPolygonF
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtWidgets import QGraphicsPolygonItem
from PySide6.QtWidgets import QGraphicsRectItem
from scipy.spatial._qhull import Delaunay

from modules.data.src.grid_scene import GridScene
from modules.data.src.services.drawing_service import DrawingService


class MeshService:
    mesh_map: dict[QGraphicsItem, list[QGraphicsItem]] = {}

    def __init__(self, scene: GridScene, drawing_service: DrawingService):
        self.scene = scene
        self.drawing_service = drawing_service

    def build_mesh(self, selected_items: list[QGraphicsItem], dx: float, dy: float):
        item = selected_items[0]
        if hasattr(item, 'path'):
            path: QPainterPath = item.path()
        elif isinstance(item, QGraphicsRectItem):
            path = QPainterPath()
            path.addRect(item.rect())
        elif isinstance(item, QGraphicsEllipseItem):
            path = QPainterPath()
            path.addEllipse(item.rect())
        elif isinstance(item, QGraphicsLineItem):
            path = QPainterPath()
            line = item.line()
            path.moveTo(line.p1())
            path.lineTo(line.p2())
        else:
            print(f"Тип {type(item)} не поддерживается.")
            return

        path = item.mapToScene(path)

        subpaths = path.toSubpathPolygons()
        max_h, max_w = 0, 0
        outer_i = 0
        for i in range(len(subpaths)):
            if (w := subpaths[i].boundingRect().width()) > max_w and (h := subpaths[i].boundingRect().height()) > max_h:
                max_w = w
                max_h = h

                outer_polygon = subpaths[i]
                outer_i = i

        holes = [subpaths[i] for i in range(len(subpaths)) if i != outer_i]

        rect = outer_polygon.boundingRect()

        min_x, max_x = rect.left(), rect.right()
        min_y, max_y = rect.top(), rect.bottom()

        stroker = QPainterPathStroker()
        stroker.setWidth(0.01)  # ширина должна быть хотя бы чуть больше погрешности
        expanded_path = stroker.createStroke(path)
        expanded_path.addPath(path)

        grid = []
        y = min_y
        while y <= max_y:
            x = min_x
            while x <= max_x:
                point = QPointF(x, y)
                if expanded_path.contains(point) and all(
                        not hole.containsPoint(point, Qt.FillRule.WindingFill) for hole in
                        holes):  # Qt-версия фильтрации
                    grid.append(point)
                x += dx
            y += dy

        triangles = Delaunay(list(map(lambda p: (p.x(), p.y()), grid)))
        triangle_polygon_items = []

        for triangle in triangles.simplices:
            p0 = grid[triangle[0]]
            p1 = grid[triangle[1]]
            p2 = grid[triangle[2]]

            mesh_item = QGraphicsPolygonItem(QPolygonF((p0, p1, p2)))
            mesh_item.setPen(self.drawing_service.default_pen)
            mesh_item.setZValue(-1)
            self.scene.addItem(mesh_item)
            triangle_polygon_items.append(mesh_item)

        self.mesh_map[item] = triangle_polygon_items
