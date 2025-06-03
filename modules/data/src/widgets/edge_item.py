import itertools

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsPathItem

from src.physics.turbulence_models import BoundaryConditions

_edge_id_counter = itertools.count(1)


def _next_edge_id() -> int:
    return next(_edge_id_counter)


class EdgeItem(QGraphicsPathItem):
    boundary_conditions: BoundaryConditions
    
    def __init__(self, path: QPainterPath, parent=None):
        super().__init__(path, parent)
        self.id = _next_edge_id()

    @property
    def p1(self) -> QPointF:
        return self.path().pointAtPercent(0.0)

    @property
    def p2(self) -> QPointF:
        return self.path().pointAtPercent(1.0)

    def reverse(self):
        """Поменять направление кривой на обратное."""
        orig = self.path()
        rev = QPainterPath()
        # обходим все сегменты в обратном порядке
        n = orig.elementCount()
        # первый элемент в rev — последний из orig
        last_elem = orig.elementAt(n - 1)
        rev.moveTo(last_elem.x, last_elem.y)
        # теперь добавляем сегменты в обратном порядке:
        for i in range(n - 2, -1, -1):
            e = orig.elementAt(i)
            rev.lineTo(e.x, e.y)
        self.setPath(rev)


if __name__ == '__main__':
    p = QPainterPath()
    p.moveTo(0.0, 0.0)
    p.lineTo(0.0, 1.0)
    e = EdgeItem(p)

    p1 = QPointF(0.0, 0.0)
    p2 = QPointF(0.0, 0.0)

    print({(p1.x(), p1.y()), (p2.x(), p2.y())})

    # print(p1 - p2).man
    # print(e.p2)
