from PySide6.QtCore import Qt, QPointF, QRectF, QEvent
from PySide6.QtGui import QMouseEvent, QPen, QColor, QBrush
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsScene,
                               QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsRectItem)

from src.ui.template import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)

        self.selected_items = set()
        self.default_pen = QPen(Qt.black, 2)
        self.selected_pen = QPen(Qt.red, 2)
        self.selection_pen = QPen(Qt.blue, 1, Qt.DashLine)
        self.selection_brush = QBrush(QColor(0, 0, 255, 50))

        self.dragging = False
        self.drag_start_pos = QPointF()
        self.selection_rect = None
        self.moving_items = False
        self.move_start_pos = QPointF()
        self.last_selection_rect = QRectF()

        self.current_tool = 'select'
        self.start_point = None
        self.temp_item = None

        self.ui.actionSelect.triggered.connect(lambda: self.set_tool('select'))
        self.ui.actionDrawLine.triggered.connect(lambda: self.set_tool('line'))
        self.ui.actionDrawRect.triggered.connect(lambda: self.set_tool('rect'))
        self.ui.actionDrawCircle.triggered.connect(lambda: self.set_tool('circle'))

        self.ui.graphicsView.viewport().installEventFilter(self)

    def set_tool(self, tool):
        if tool != self.current_tool:
            self.clear_selection()
        self.current_tool = tool

    def eventFilter(self, obj, event):
        if obj is self.ui.graphicsView.viewport():
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                return self.mouse_press(event)
            elif event.type() == QEvent.MouseMove:
                return self.mouse_move(event)
            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                return self.mouse_release(event)
        return super().eventFilter(obj, event)

    def mouse_press(self, event: QMouseEvent):
        scene_pos = self.ui.graphicsView.mapToScene(event.position().toPoint())
        self.start_point = scene_pos
        self.last_selection_rect = QRectF()

        if self.current_tool == 'select':
            item = self.scene.itemAt(scene_pos, self.ui.graphicsView.transform())

            ctrl_pressed = event.modifiers() & Qt.ControlModifier

            if not ctrl_pressed and item not in self.selected_items:
                self.clear_selection()

            if item:
                if ctrl_pressed:
                    self.toggle_item_selection(item)
                else:
                    self.select_item(item)

                self.moving_items = True
                self.move_start_pos = scene_pos
            else:
                self.selection_rect = QGraphicsRectItem()
                self.selection_rect.setPen(self.selection_pen)
                self.selection_rect.setBrush(self.selection_brush)
                self.scene.addItem(self.selection_rect)

        elif self.current_tool in ['line', 'rect', 'circle']:
            self.clear_selection()
            if self.current_tool == 'line':
                self.temp_item = QGraphicsLineItem()
            elif self.current_tool == 'rect':
                self.temp_item = QGraphicsRectItem()
            elif self.current_tool == 'circle':
                self.temp_item = QGraphicsEllipseItem()

            self.temp_item.setPen(self.default_pen)
            self.scene.addItem(self.temp_item)

        return True

    def toggle_item_selection(self, item):
        if item in self.selected_items:
            item.setPen(self.default_pen)
            self.selected_items.remove(item)
        else:
            item.setPen(self.selected_pen)
            self.selected_items.add(item)

    def select_item(self, item):
        item.setPen(self.selected_pen)
        self.selected_items.add(item)

    def clear_selection(self):
        for item in self.selected_items:
            item.setPen(self.default_pen)
        self.selected_items.clear()

    def update_selection(self, selection_rect):
        new_selection = set()

        for item in self.scene.items():
            if isinstance(item, (QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem)):
                if selection_rect.intersects(item.sceneBoundingRect()):
                    new_selection.add(item)

        for item in self.selected_items - new_selection:
            item.setPen(self.default_pen)

        for item in new_selection - self.selected_items:
            item.setPen(self.selected_pen)

        self.selected_items = new_selection

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.selected_items:
            for item in list(self.selected_items):
                self.scene.removeItem(item)
            self.selected_items.clear()

    def mouse_move(self, event: QMouseEvent):
        scene_pos = self.ui.graphicsView.mapToScene(event.position().toPoint())

        if self.current_tool == 'select':
            if self.moving_items and self.selected_items:
                delta = scene_pos - self.move_start_pos
                for item in self.selected_items:
                    item.moveBy(delta.x(), delta.y())
                self.move_start_pos = scene_pos
                return True
            elif self.selection_rect:
                rect = QRectF(self.start_point, scene_pos).normalized()
                self.selection_rect.setRect(rect)

                if rect != self.last_selection_rect:
                    self.update_selection(rect)
                    self.last_selection_rect = rect
            return True

        if not self.temp_item or not self.start_point:
            return True

        current_pos = scene_pos
        rect = QRectF(self.start_point, current_pos).normalized()

        if isinstance(self.temp_item, QGraphicsLineItem):
            self.temp_item.setLine(self.start_point.x(), self.start_point.y(),
                                   current_pos.x(), current_pos.y())
        elif isinstance(self.temp_item, QGraphicsRectItem):
            self.temp_item.setRect(rect)
        elif isinstance(self.temp_item, QGraphicsEllipseItem):
            self.temp_item.setRect(rect)
        return True

    def mouse_release(self, event: QMouseEvent):
        if self.current_tool == 'select':
            if self.selection_rect:
                self.scene.removeItem(self.selection_rect)
                self.selection_rect = None
            self.moving_items = False
        else:
            if self.temp_item:
                self.temp_item.setPen(self.default_pen)
                self.select_item(self.temp_item)

        self.temp_item = None
        self.start_point = None
        return True


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()