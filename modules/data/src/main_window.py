import math

from PySide6.QtCore import Qt, QPointF, QRectF, QEvent
from PySide6.QtGui import QMouseEvent, QPen, QColor, QBrush, QPainterPath, QPainter
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsLineItem, QGraphicsEllipseItem,
                               QGraphicsRectItem, QGraphicsPathItem, QGraphicsView)

from .commands.add_command import AddCommand
from .commands.delete_command import DeleteCommand
from .commands.move_command import MoveCommand
from .editable_bezier import EditableBezierCurveItem
from .grid_scene import GridScene
from .ui.template import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scene = GridScene(spacing=50)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHints(QPainter.Antialiasing)
        self.ui.graphicsView.scale(1, -1)
        self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

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
        self.curve_points = []
        self.temp_curve_item = None

        self.undo_stack = []

        self.ui.actionSelect.triggered.connect(lambda: self.set_tool('select'))
        self.ui.actionDrawLine.triggered.connect(lambda: self.set_tool('line'))
        self.ui.actionDrawRect.triggered.connect(lambda: self.set_tool('rect'))
        self.ui.actionDrawCircle.triggered.connect(lambda: self.set_tool('circle'))
        self.ui.actionDrawCurve.triggered.connect(lambda: self.set_tool('curve'))
        self.ui.actionDrawParametric.triggered.connect(lambda: self.set_tool('parametric'))

        self.ui.graphicsView.viewport().installEventFilter(self)

    def set_tool(self, tool):
        if tool != self.current_tool:
            self.clear_selection()
            self.finish_curve()
        self.current_tool = tool
        print(f"Current tool set to: {tool}")  # Отладочный вывод

    def finish_curve(self):
        if len(self.curve_points) > 1:
            curve = EditableBezierCurveItem(self.curve_points, pen=self.default_pen, scene=self.scene)
            command = AddCommand(self.scene, curve)
            command.execute()
            self.undo_stack.append(command)
            self.select_item(curve)
        if self.temp_curve_item:
            self.scene.removeItem(self.temp_curve_item)
            self.temp_curve_item = None
        self.curve_points = []

    def generate_parametric_path(self, start_pos):
        print("Generating parametric path at:", start_pos)  # Отладочный вывод
        num_points = 1000
        c = 100.0
        s = [i / (num_points - 1) for i in range(num_points)]
        x = [c * si for si in s]
        y = [c * 0.594689181 * (0.298222773 * math.sqrt(si) - 0.127125232 * si -
                                0.357907906 * si**2 + 0.291984971 * si**3 -
                                0.105174696 * si**4) for si in s]
        path = QPainterPath()
        path.moveTo(start_pos.x() + x[0], start_pos.y() + y[0])
        for i in range(1, num_points):
            path.lineTo(start_pos.x() + x[i], start_pos.y() + y[i])
        return path

    def eventFilter(self, obj, event):
        if obj is self.ui.graphicsView.viewport():
            if event.type() == QEvent.MouseButtonPress:
                return self.mouse_press(event)
            elif event.type() == QEvent.MouseMove:
                if event.buttons() & Qt.LeftButton:
                    return self.mouse_move(event)
                return False
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.MiddleButton:
                    return False
                return self.mouse_release(event)
        return super().eventFilter(obj, event)

    def mouse_press(self, event: QMouseEvent):
        scene_pos = self.ui.graphicsView.mapToScene(event.position().toPoint())
        self.start_point = scene_pos
        self.last_selection_rect = QRectF()

        if event.button() != Qt.LeftButton and self.current_tool != 'curve':
            return False

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
        elif self.current_tool == 'curve':
            if event.button() == Qt.LeftButton:
                if not self.curve_points:
                    self.curve_points = [scene_pos]
                    path = QPainterPath()
                    path.moveTo(scene_pos)
                    self.temp_curve_item = QGraphicsPathItem(path)
                    self.temp_curve_item.setPen(self.default_pen)
                    self.scene.addItem(self.temp_curve_item)
                else:
                    self.curve_points.append(scene_pos)
                    self.update_curve()
            return True
        elif self.current_tool == 'parametric':
            print("Drawing parametric curve at:", scene_pos)  # Отладочный вывод
            path = self.generate_parametric_path(scene_pos)
            item = QGraphicsPathItem(path)
            item.setPen(self.default_pen)
            command = AddCommand(self.scene, item)
            command.execute()
            self.undo_stack.append(command)
            self.select_item(item)
            print("Items in scene:", len(self.scene.items()))  # Отладочный вывод
            return True
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

    def update_curve(self):
        if not self.curve_points or not self.temp_curve_item:
            return
        path = QPainterPath()
        path.moveTo(self.curve_points[0])
        if len(self.curve_points) < 2:
            self.temp_curve_item.setPath(path)
            return
        for i in range(1, len(self.curve_points)):
            p0 = self.curve_points[i - 1]
            p1 = self.curve_points[i]
            if i == 1:
                ctrl1 = p0 + (p1 - p0) * 0.33
            else:
                prev_p = self.curve_points[i - 2]
                ctrl1 = p0 + (p0 - prev_p) * 0.33
            if i == len(self.curve_points) - 1:
                ctrl2 = p1 - (p1 - p0) * 0.33
            else:
                next_p = self.curve_points[i + 1]
                ctrl2 = p1 - (next_p - p1) * 0.33
            path.cubicTo(ctrl1, ctrl2, p1)
        self.temp_curve_item.setPath(path)

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
            if isinstance(item, (QGraphicsLineItem, QGraphicsRectItem,
                                 QGraphicsEllipseItem, QGraphicsPathItem)):
                if selection_rect.intersects(item.sceneBoundingRect()):
                    new_selection.add(item)
        for item in self.selected_items - new_selection:
            item.setPen(self.default_pen)
        for item in new_selection - self.selected_items:
            item.setPen(self.selected_pen)
        self.selected_items = new_selection

    def select_all(self):
        self.clear_selection()
        for item in self.scene.items():
            if isinstance(item, (QGraphicsLineItem, QGraphicsRectItem,
                                 QGraphicsEllipseItem, EditableBezierCurveItem)):
                self.select_item(item)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_A:
            self.select_all()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Z:
            if self.undo_stack:
                command = self.undo_stack.pop()
                command.undo()
                self.clear_selection()
        elif event.key() == Qt.Key_Delete and self.selected_items:
            command = DeleteCommand(self.scene, list(self.selected_items))
            command.execute()
            self.undo_stack.append(command)
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
        if self.current_tool == 'curve':
            if self.temp_curve_item and self.curve_points:
                temp_points = self.curve_points + [scene_pos]
                path = QPainterPath()
                path.moveTo(temp_points[0])
                for i in range(1, len(temp_points)):
                    p0 = temp_points[i - 1]
                    p1 = temp_points[i]
                    if i == 1:
                        ctrl1 = p0 + (p1 - p0) * 0.33
                    else:
                        prev_p = temp_points[i - 2]
                        ctrl1 = p0 + (p0 - prev_p) * 0.33
                    if i == len(temp_points) - 1:
                        ctrl2 = p1 - (p1 - p0) * 0.33
                    else:
                        next_p = temp_points[i + 1] if i + 1 < len(temp_points) else p1
                        ctrl2 = p1 - (next_p - p1) * 0.33
                    path.cubicTo(ctrl1, ctrl2, p1)
                self.temp_curve_item.setPath(path)
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
            if self.moving_items and self.selected_items:
                delta = self.ui.graphicsView.mapToScene(event.position().toPoint()) - self.move_start_pos
                if delta.x() != 0 or delta.y() != 0:
                    command = MoveCommand(list(self.selected_items), delta)
                    self.undo_stack.append(command)
            self.moving_items = False
        elif self.current_tool == 'curve':
            if event.button() == Qt.RightButton:
                self.finish_curve()
            return True
        elif self.current_tool in ['line', 'rect', 'circle']:
            if self.temp_item:
                command = AddCommand(self.scene, self.temp_item)
                self.undo_stack.append(command)
                self.select_item(self.temp_item)
        self.temp_item = None
        self.start_point = None
        return True


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()