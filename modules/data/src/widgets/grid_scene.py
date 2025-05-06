from PySide6.QtCore import QPointF
from PySide6.QtCore import QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtWidgets import QGraphicsTextItem


class GridScene(QGraphicsScene):
    def __init__(self, spacing: int = 50, *args, **kwargs):
        """
        :param spacing: расстояние между линиями сетки в пикселях
        """
        super().__init__(*args, **kwargs)
        self.spacing = spacing
        self.grid_pen = QPen(Qt.lightGray, 0)
        self.axis_pen = QPen(Qt.black, 0)
        self.font = QFont("Arial",  6)  # размер шрифта для меток
        self._labels = []
        # Как только изменяется область сцены, перерисуем все метки:
        self.sceneRectChanged.connect(self.update_labels)

    def drawBackground(self, painter, rect: QRectF):
        # 1) рисуем тонкую серую сетку
        left = int(rect.left()) - (int(rect.left()) % self.spacing)
        top = int(rect.top()) - (int(rect.top()) % self.spacing)

        x = left
        while x < rect.right():
            painter.setPen(self.grid_pen)
            painter.drawLine(x, rect.top() - 1, x, rect.bottom() + 1)
            x += self.spacing

        y = top
        while y < rect.bottom():
            painter.setPen(self.grid_pen)
            painter.drawLine(rect.left() - 1, y, rect.right() + 1, y)
            y += self.spacing

        # 2) рисуем толстые оси
        painter.setPen(self.axis_pen)
        painter.drawLine(rect.left() - 1, 0, rect.right() + 1, 0)   # X‑ось
        painter.drawLine(0, rect.top() - 1,   0, rect.bottom() + 1) # Y‑ось

    def update_labels(self, rect: QRectF):
        # Удаляем старые метки
        for lab in self._labels:
            self.removeItem(lab)
        self._labels.clear()

        left, top, right, bottom = rect.left(), rect.top(), rect.right(), rect.bottom()

        # Метки по X
        first_x = int(left) - (int(left) % self.spacing)
        x = first_x
        while x <= right:
            unit = int(x / self.spacing)
            lab = QGraphicsTextItem(str(unit))
            lab.setFont(self.font)
            lab.setFlag(QGraphicsTextItem.ItemIgnoresTransformations, True)
            lab.setPos(QPointF(x, 0))
            self.addItem(lab)
            self._labels.append(lab)
            x += self.spacing

        # Метки по Y
        first_y = int(top) - (int(top) % self.spacing)
        y = first_y
        while y <= bottom:
            if y != 0:
                unit = int(y / self.spacing)
                lab = QGraphicsTextItem(str(unit))
                lab.setFont(self.font)
                lab.setFlag(QGraphicsTextItem.ItemIgnoresTransformations, True)
                lab.setPos(QPointF(0, y))
                self.addItem(lab)
                self._labels.append(lab)
            y += self.spacing

    def find_edge_by_id(self, edge_id: str) -> QGraphicsItem | None:
        """Находит ребро на сцене по его ID."""
        for item in self.items():
            if hasattr(item, 'id') and item.id == edge_id:
                return item
        return None
