import math

import numpy as np
from PySide6.QtCore import Qt, QPointF, QRectF, QEvent
from PySide6.QtGui import QMouseEvent, QPen, QColor, QBrush, QPainter
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsLineItem, QGraphicsEllipseItem,
                               QGraphicsRectItem, QGraphicsView, QDialog)
from PySide6.QtWidgets import QGraphicsPathItem

from .commands.add_command import AddCommand
from .commands.delete_command import DeleteCommand
from .commands.move_command import MoveCommand
from .editable_bezier import EditableBezierCurveItem
from .grid_scene import GridScene
from .parametric_dialog import ParametricDialog
from .ui.template import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scene = GridScene(spacing=1)
        self.scene.setSceneRect(-500, -500, 1000, 1000)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHints(QPainter.Antialiasing)
        self.grid_spacing = 50  # пикселей на одну клетку
        self.ui.graphicsView.scale(self.grid_spacing, -self.grid_spacing)
        self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.selected_items = set()
        self.default_pen = QPen(Qt.black, 0)
        self.selected_pen = QPen(Qt.red, 0)
        self.selection_pen = QPen(Qt.blue, 0, Qt.DashLine)
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
        # self.ui.actionDrawParametric.triggered.connect(lambda: self.set_tool('parametric'))
        self.ui.actionDrawParametric.triggered.connect(self.on_draw_parametric)
        self.ui.actionUnion.triggered.connect(self.perform_union)
        self.ui.actionDifference.triggered.connect(self.perform_difference)
        self.ui.actionIntersection.triggered.connect(self.perform_intersection)
        self.ui.actionMirror.triggered.connect(self.perform_mirror)

        self.ui.graphicsView.viewport().installEventFilter(self)

    def set_tool(self, tool):
        if tool != self.current_tool:
            self.clear_selection()
            self.finish_curve()
        self.current_tool = tool
        print(f'Current tool set to: {tool}')  # Отладочный вывод

    def finish_curve(self):
        if len(self.curve_points) > 1:
            curve = EditableBezierCurveItem(self.curve_points, pen=self.default_pen, scene=self.scene)
            curve.setFlag(QGraphicsPathItem.ItemIsSelectable, True)  # <--- ДОБАВИТЬ!
            command = AddCommand(self.scene, curve)
            command.execute()
            self.undo_stack.append(command)
            self.select_item(curve)
        if self.temp_curve_item:
            self.scene.removeItem(self.temp_curve_item)
            self.temp_curve_item = None
        self.curve_points = []

    def on_draw_parametric(self):
        dlg = ParametricDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        safe_globals = {
            'math': math,
            **{name: getattr(math, name) for name in dir(math) if not name.startswith('_')}
        }

        data = dlg.get_data()
        t_vals = np.linspace(data['t_min'], data['t_max'], data['samples'])
        try:
            x_vals = [eval(data['x_expr'], {'t': t, **safe_globals}) for t in t_vals]
            y_vals = [eval(data['y_expr'], {'t': t, **safe_globals}) for t in t_vals]
        except Exception as e:
            print(f'Ошибка в выражении: {e}')
            return
        path = QPainterPath()
        path.moveTo(x_vals[0], y_vals[0])
        for x, y in zip(x_vals[1:], y_vals[1:]):
            path.lineTo(x, y)

        item = QGraphicsPathItem(path)
        item.setPen(self.default_pen)
        item.setFlag(QGraphicsPathItem.ItemIsSelectable, True)  # <--- ДОБАВИТЬ!
        self.scene.addItem(item)
        self.select_item(item)

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
        elif self.current_tool in ['line', 'rect', 'circle']:
            self.clear_selection()
            if self.current_tool == 'line':
                self.temp_item = QGraphicsLineItem()
            elif self.current_tool == 'rect':
                self.temp_item = QGraphicsRectItem()
            elif self.current_tool == 'circle':
                self.temp_item = QGraphicsEllipseItem()
            self.temp_item.setPen(self.default_pen)
            self.temp_item.setFlag(QGraphicsLineItem.ItemIsSelectable, True)  # <--- ДОБАВИТЬ!
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
        # self.scene.clearSelection()
        item.setPen(self.selected_pen)
        self.scene.selectedItems().append(item)
        item.setSelected(True)
        self.selected_items.add(item)

    def clear_selection(self):
        self.scene.clearSelection()
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

    def perform_union(self):
        self.boolean_operation('union')

    def perform_difference(self):
        self.boolean_operation('difference')

    def perform_intersection(self):
        self.boolean_operation('intersection')

    def perform_mirror(self):
        selected = self.scene.selectedItems()
        if len(selected) != 1:
            print(f'Выберите одну фигуру для отражения! {len(selected)}')
            return

        item = selected[0]

        from PySide6.QtWidgets import QInputDialog
        axis, ok = QInputDialog.getItem(
            self, 'Выбор оси отражения',
            'Отразить по оси:',
            ['По горизонтали (X)', 'По вертикали (Y)', 'По диагонали (XY)'],
            0, False
        )

        if not ok:
            return

        path = item.path()
        center = path.boundingRect().center()

        from PySide6.QtGui import QTransform

        if axis == 'По горизонтали (X)':
            transform = QTransform().scale(1, -1)
        elif axis == 'По вертикали (Y)':
            transform = QTransform().scale(-1, 1)
        elif axis == 'По диагонали (XY)':
            transform = QTransform().scale(-1, -1)
        else:
            return

        path = transform.map(path)
        item.setPath(path)

    def boolean_operation(self, op_type: str):
        selected = self.scene.selectedItems()
        if len(selected) != 2:
            print(f'Выберите ровно 2 фигуры! А не {len(selected)}')
            return

        item1, item2 = selected
        if not (hasattr(item1, 'path') and hasattr(item2, 'path')):
            print('Выберите фигуры с путями!')
            return

        path1 = item1.path()
        path2 = item2.path()

        if op_type == 'union':
            result = path1.united(path2)
        elif op_type == 'difference':
            result = path1.subtracted(path2)
        elif op_type == 'intersection':
            result = path1.intersected(path2)
        else:
            return

        # Создаём новый элемент
        new_item = QGraphicsPathItem(result)
        new_item.setPen(self.default_pen)
        new_item.setFlag(QGraphicsPathItem.ItemIsSelectable, True)  # <--- ДОБАВИТЬ!
        self.scene.addItem(new_item)

        # Удаляем старые
        self.scene.removeItem(item1)
        self.scene.removeItem(item2)

        self.select_item(new_item)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
