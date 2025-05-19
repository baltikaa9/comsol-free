from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QGraphicsView


class GraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Полная перерисовка при обновлении
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        # Масштаб относительно курсора
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._panning = False
        self._pan_start = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._panning and self._pan_start is not None:
            # Текущая и стартовая точки в координатах сцены
            start_scene = self.mapToScene(self._pan_start)
            current_scene = self.mapToScene(event.pos())
            delta_scene = start_scene - current_scene

            # Обновляем позицию для следующего события
            self._pan_start = event.pos()

            # Сдвигаем область сцены
            scene = self.scene()
            if scene is not None:
                rect = scene.sceneRect()
                rect.translate(delta_scene.x(), delta_scene.y())
                scene.setSceneRect(rect)
        # if self._panning and self._pan_start is not None:
        #     delta = self._pan_start - event.pos()
        #     self._pan_start = event.pos()
        #     self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
        #     self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.15 if delta > 0 else 1 / 1.15
            self.scale(factor, factor)

            if scene := self.scene():
                # получаем прямоугольник видимой области в координатах сцены
                visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
                scene.setSceneRect(visible_rect)
        else:
            super().wheelEvent(event)
