import math

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
        self.font = QFont("Arial",  8)  # размер шрифта для меток
        self._labels = []
        # Как только изменяется область сцены, перерисуем все метки:
        self.sceneRectChanged.connect(self.update_labels)

    def _nice_step(self, span_units: float) -> int:
        """
        span_units = (pixels_span / spacing)
        хотим ~10 делений, но шаг выбираем из {1,2,4,10}×10^exp
        """
        if span_units <= 0:
            return 1
        # целевая «сырая» величина
        raw = span_units / 10.0
        exp = math.floor(math.log10(raw))
        base = raw / (10 ** exp)
        if base < 1.5:
            nice = 1
        elif base < 3:
            nice = 2
        elif base < 7:
            nice = 4
        else:
            nice = 10
        return nice * (10 ** exp)


    def drawBackground(self, painter, rect: QRectF):
        left, top, right, bottom = rect.left(), rect.top(), rect.right(), rect.bottom()

        span_x = (right - left) / self.spacing
        span_y = (bottom - top) / self.spacing

        # получаем красивый шаг unit_step
        step_x = self._nice_step(span_x)
        step_y = self._nice_step(span_y)

        # 1) рисуем тонкие линии только на этих шагах
        first_i = math.ceil((left / self.spacing) / step_x) * step_x
        i = first_i
        while i * self.spacing <= right:
            x = i * self.spacing
            painter.setPen(self.grid_pen)
            painter.drawLine(x, top - 1, x, bottom + 1)
            i += step_x

        first_j = math.ceil((top / self.spacing) / step_y) * step_y
        j = first_j
        while j * self.spacing <= bottom:
            y = j * self.spacing
            painter.setPen(self.grid_pen)
            painter.drawLine(left - 1, y, right + 1, y)
            j += step_y

        # 2) толстые оси всегда
        painter.setPen(self.axis_pen)
        painter.drawLine(left - 1, 0, right + 1, 0)
        painter.drawLine(0, top - 1, 0, bottom + 1)

    def update_labels(self, rect: QRectF):
        # Удаляем старые метки
        for lab in self._labels:
            self.removeItem(lab)
        self._labels.clear()

        left, top, right, bottom = rect.left(), rect.top(), rect.right(), rect.bottom()

        span_x = (right - left) / self.spacing
        span_y = (bottom - top) / self.spacing
        step_x = self._nice_step(span_x)
        step_y = self._nice_step(span_y)

        # X-метки
        first_i = math.ceil((left / self.spacing) / step_x) * step_x
        i = first_i
        while i * self.spacing <= right:
            pos = i * self.spacing
            lab = QGraphicsTextItem(str(i))
            lab.setFont(self.font)
            lab.setFlag(QGraphicsTextItem.ItemIgnoresTransformations, True)
            lab.setPos(QPointF(pos, 0))
            self.addItem(lab)
            self._labels.append(lab)
            i += step_x

        # Y-метки
        first_j = math.ceil((top / self.spacing) / step_y) * step_y
        j = first_j
        while j * self.spacing <= bottom:
            pos = j * self.spacing
            if pos != 0:
                lab = QGraphicsTextItem(str(j))
                lab.setFont(self.font)
                lab.setFlag(QGraphicsTextItem.ItemIgnoresTransformations, True)
                lab.setPos(QPointF(0, pos))
                self.addItem(lab)
                self._labels.append(lab)
            j += step_y

        # Метки по X
        # first_x = int(left) - (int(left) % self.spacing)
        # x = first_x
        # while x <= right:
        #     unit = int(x / self.spacing)
        #     if unit % 10 == 0:
        #         lab = QGraphicsTextItem(str(unit))
        #         lab.setFont(self.font)
        #         lab.setFlag(QGraphicsTextItem.ItemIgnoresTransformations, True)
        #         lab.setPos(QPointF(x, 0))
        #         self.addItem(lab)
        #         self._labels.append(lab)
        #     x += self.spacing
        #
        # # Метки по Y
        # first_y = int(top) - (int(top) % self.spacing)
        # y = first_y
        # while y <= bottom:
        #     unit = int(y / self.spacing)
        #     if y != 0 and unit % 10 == 0:
        #         lab = QGraphicsTextItem(str(unit))
        #         lab.setFont(self.font)
        #         lab.setFlag(QGraphicsTextItem.ItemIgnoresTransformations, True)
        #         lab.setPos(QPointF(0, y))
        #         self.addItem(lab)
        #         self._labels.append(lab)
        #     y += self.spacing

    def find_edge_by_id(self, edge_id: str) -> QGraphicsItem | None:
        """Находит ребро на сцене по его ID."""
        for item in self.items():
            if hasattr(item, 'id') and item.id == edge_id:
                return item
        return None
