"""Translate editor primitives and edge conditions to MUSCL's native geometry."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF
from src.physics.turbulence_models import (
    BoundaryConditionType,
    WallBoundaryConditions,
    WallType,
)
from src.services.muscl_case_exporter import MusclSolid
from src.shapes.boolean_item import BooleanShapeItem
from src.shapes.ellipse_item import EllipseItem
from src.shapes.rectangle_item import RectangleItem


class MusclGeometryAdapter:
    """Convert only exact, supported editor shapes; refuse lossy mappings."""

    TOLERANCE = 1e-5

    def __init__(self, scene, grid_spacing: float, boundary_edges):
        if grid_spacing <= 0:
            raise ValueError("Шаг координат редактора должен быть положительным")
        self.scene = scene
        self.scale = float(grid_spacing)
        self.boundary_edges = list(boundary_edges)

    def convert(self) -> tuple[dict, tuple[MusclSolid, ...], tuple[int, int, int, int]]:
        shapes = self._top_level_shapes()
        rectangles = [item for item in shapes if isinstance(item, RectangleItem)]
        if not rectangles:
            raise ValueError("Для MUSCL нужен внешний прямоугольник расчётной области")

        domain_item = max(
            rectangles, key=lambda item: item.rect().width() * item.rect().height()
        )
        domain = self._rectangle_bounds(domain_item)
        if domain["xmin"] >= domain["xmax"] or domain["ymin"] >= domain["ymax"]:
            raise ValueError("Внешний прямоугольник расчётной области вырожден")

        solids: list[MusclSolid] = []
        for shape in shapes:
            if shape is domain_item:
                continue
            if isinstance(shape, EllipseItem):
                solids.append(self._ellipse(shape))
                self._require_solid_wall_conditions(shape)
            elif isinstance(shape, RectangleItem):
                bounds = self._rectangle_bounds(shape)
                solids.append(
                    MusclSolid(
                        "rectangle",
                        (
                            (bounds["xmin"], bounds["ymin"]),
                            (bounds["xmax"], bounds["ymax"]),
                        ),
                    )
                )
                self._require_solid_wall_conditions(shape)
            elif isinstance(shape, BooleanShapeItem):
                raise ValueError("Булевы фигуры MUSCL напрямую не поддерживает")
            else:
                raise ValueError(
                    f"Форма {type(shape).__name__} не поддерживается как препятствие MUSCL"
                )

        boundary_codes = self._domain_boundary_codes(domain_item, domain)
        return domain, tuple(solids), boundary_codes

    def _top_level_shapes(self):
        shapes = []
        for item in self.scene.items():
            if item.parentItem() is not None:
                continue
            if isinstance(item, (RectangleItem, EllipseItem, BooleanShapeItem)):
                shapes.append(item)
            elif getattr(item, "edges", None):
                raise ValueError(
                    f"Форма {type(item).__name__} не поддерживается экспортом MUSCL"
                )
        return shapes

    def _point(self, point: QPointF) -> tuple[float, float]:
        return point.x() / self.scale, point.y() / self.scale

    def _rectangle_bounds(self, item: RectangleItem) -> dict[str, float]:
        rect = item.rect()
        corners = [
            item.mapToScene(rect.topLeft()),
            item.mapToScene(rect.topRight()),
            item.mapToScene(rect.bottomRight()),
            item.mapToScene(rect.bottomLeft()),
        ]
        xs = [point.x() for point in corners]
        ys = [point.y() for point in corners]
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
        expected = {(xmin, ymin), (xmin, ymax), (xmax, ymin), (xmax, ymax)}
        actual = {(round(point.x(), 7), round(point.y(), 7)) for point in corners}
        expected_rounded = {(round(x, 7), round(y, 7)) for x, y in expected}
        if actual != expected_rounded:
            raise ValueError("Поворот/наклон прямоугольников MUSCL не поддерживается")
        return {
            "xmin": xmin / self.scale,
            "xmax": xmax / self.scale,
            "ymin": ymin / self.scale,
            "ymax": ymax / self.scale,
        }

    def _ellipse(self, item: EllipseItem) -> MusclSolid:
        rect = item.rect()
        center = item.mapToScene(rect.center())
        right = item.mapToScene(QPointF(rect.right(), rect.center().y()))
        top = item.mapToScene(QPointF(rect.center().x(), rect.top()))
        rx = math.hypot(right.x() - center.x(), right.y() - center.y()) / self.scale
        ry = math.hypot(top.x() - center.x(), top.y() - center.y()) / self.scale
        if rx <= 0 or ry <= 0:
            raise ValueError("Эллипс-препятствие имеет нулевую полуось")
        # MUSCL supports axis-aligned ellipses only.
        if (
            abs(right.y() - center.y()) > self.TOLERANCE
            or abs(top.x() - center.x()) > self.TOLERANCE
        ):
            raise ValueError("Поворот эллипса MUSCL не поддерживается")
        return MusclSolid("ellipse", (self._point(center), (rx, ry)))

    def _assigned_bc(self, edge):
        if edge not in self.boundary_edges or not hasattr(edge, "boundary_conditions"):
            raise ValueError(
                "Назначьте граничное условие каждому ребру области и препятствий"
            )
        return edge.boundary_conditions

    def _require_solid_wall_conditions(self, item):
        for edge in getattr(item, "edges", []):
            bc = self._assigned_bc(edge)
            if bc.type != BoundaryConditionType.WALL:
                raise ValueError(
                    "Для препятствий MUSCL поддерживается только условие Wall"
                )

    def _domain_boundary_codes(self, item, domain) -> tuple[int, int, int, int]:
        sides: dict[str, set[int]] = {
            key: set() for key in ("left", "right", "bottom", "top")
        }
        bounds_scene = {key: value * self.scale for key, value in domain.items()}
        for edge in getattr(item, "edges", []):
            bc = self._assigned_bc(edge)
            code = self._boundary_code(bc)
            path = edge.mapToScene(edge.path())
            rect = path.boundingRect()
            if (
                abs(rect.left() - bounds_scene["xmin"]) <= self.TOLERANCE
                and abs(rect.right() - bounds_scene["xmin"]) <= self.TOLERANCE
            ):
                sides["left"].add(code)
            elif (
                abs(rect.left() - bounds_scene["xmax"]) <= self.TOLERANCE
                and abs(rect.right() - bounds_scene["xmax"]) <= self.TOLERANCE
            ):
                sides["right"].add(code)
            elif (
                abs(rect.top() - bounds_scene["ymin"]) <= self.TOLERANCE
                and abs(rect.bottom() - bounds_scene["ymin"]) <= self.TOLERANCE
            ):
                sides["bottom"].add(code)
            elif (
                abs(rect.top() - bounds_scene["ymax"]) <= self.TOLERANCE
                and abs(rect.bottom() - bounds_scene["ymax"]) <= self.TOLERANCE
            ):
                sides["top"].add(code)
            else:
                raise ValueError(
                    "Ребро внешней области не лежит на стороне прямоугольника"
                )

        for side, codes in sides.items():
            if not codes:
                raise ValueError(f"Не назначено граничное условие стороне {side}")
            if len(codes) != 1:
                raise ValueError(
                    f"На стороне {side} разные условия; MUSCL задаёт только одно условие на сторону"
                )
        # MUSCL ordering: x-left, x-right, y-bottom, y-top.
        return (
            next(iter(sides["left"])),
            next(iter(sides["right"])),
            next(iter(sides["bottom"])),
            next(iter(sides["top"])),
        )

    @staticmethod
    def _boundary_code(bc) -> int:
        if bc.type == BoundaryConditionType.OPEN:
            return 0  # MUSCL free boundary
        if bc.type == BoundaryConditionType.INLET:
            raise ValueError(
                "MUSCL не задаёт скорость на inlet-границе; выберите поддерживаемый тип условия"
            )
        if bc.type == BoundaryConditionType.WALL and isinstance(
            bc, WallBoundaryConditions
        ):
            return 1 if bc.wall == WallType.SLIP else 2
        raise ValueError(f"Тип границы {bc.type.value} не поддерживается MUSCL")
