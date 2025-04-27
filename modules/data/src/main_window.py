import math

import numpy as np
from PySide6.QtCore import Qt, QPointF, QRectF, QEvent, QLineF, QSizeF
from PySide6.QtGui import QMouseEvent, QPen, QColor, QBrush, QPainter, QPainterPath, QTransform
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsLineItem, QGraphicsEllipseItem,
                               QGraphicsRectItem, QGraphicsView, QDialog, QGraphicsPathItem, QInputDialog,
                               QGraphicsItem, QMessageBox)

from modules.data.src.commands.command import Command
from modules.data.src.dialogs.bezier_dialog import BezierDialog
from modules.data.src.dialogs.ellipse_dialog import EllipseDialog
from modules.data.src.dialogs.line_dialog import LineDialog
from modules.data.src.dialogs.rect_dialog import RectDialog
from modules.data.src.commands.add_command import AddCommand
from modules.data.src.commands.delete_command import DeleteCommand
from modules.data.src.commands.move_command import MoveCommand
from modules.data.src.dialogs.parametric_dialog import ParametricDialog
from modules.data.src.editable_bezier import EditableBezierCurveItem
from modules.data.src.grid_scene import GridScene
from modules.data.src.ui.template import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scene = GridScene(spacing=50)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHints(QPainter.Antialiasing)
        self.grid_spacing = 1
        self.ui.graphicsView.scale(self.grid_spacing, -self.grid_spacing)
        self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.default_pen = QPen(Qt.black, 0)
        self.selected_pen = QPen(Qt.red, 0)
        self.selection_pen = QPen(Qt.blue, 0, Qt.DashLine)
        self.selection_brush = QBrush(QColor(0, 0, 255, 50))

        self.dragging = False
        self.drag_start_pos = QPointF()
        self.selection_rect = None
        self.moving_items = False
        self.move_start_pos = QPointF()
        self.move_initial_pos = QPointF()
        self.last_selection_rect = QRectF()

        self.current_tool = 'select'
        self.start_point = None
        self.temp_item = None
        self.curve_points = []
        self.temp_curve_item = None

        self.undo_stack: list[Command] = []
        self.bool_selection: list[QGraphicsItem] = []

        self.ui.actionDrawLineByParams.triggered.connect(self.on_draw_line_by_params)
        self.ui.actionDrawRectByParams.triggered.connect(self.on_draw_rect_by_params)
        self.ui.actionDrawCircleByParams.triggered.connect(self.on_draw_circle_by_params)
        self.ui.actionDrawCurveByParams.triggered.connect(self.on_draw_curve_by_params)
        self.ui.actionDrawParametric.triggered.connect(self.on_draw_parametric)
        self.ui.actionUnion.triggered.connect(self.perform_union)
        self.ui.actionDifference.triggered.connect(self.perform_difference)
        self.ui.actionIntersection.triggered.connect(self.perform_intersection)
        self.ui.actionMirror.triggered.connect(self.perform_mirror)
        self.ui.actionRotate.triggered.connect(self.perform_rotate)

        self.ui.graphicsView.viewport().installEventFilter(self)

    def on_draw_line_by_params(self):
        dlg = LineDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data:
            print('Invalid line parameters')
            return

        scale = self.scene.spacing
        line = QLineF(data['start'] * scale, data['end'] * scale)
        item = QGraphicsLineItem(line)
        item.setPen(self.default_pen)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        command = AddCommand(self.scene, item)
        command.execute()
        self.undo_stack.append(command)
        self.select_item(item)

    def on_draw_rect_by_params(self):
        dlg = RectDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data:
            print('Invalid rectangle parameters')
            return

        scale = self.scene.spacing
        rect = QRectF(data['top_left'] * scale, QSizeF(data['width'] * scale, data['height'] * scale))
        item = QGraphicsRectItem(rect)
        item.setPen(self.default_pen)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        command = AddCommand(self.scene, item)
        command.execute()
        self.undo_stack.append(command)
        self.select_item(item)

    def on_draw_circle_by_params(self):
        dlg = EllipseDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data:
            print('Invalid ellipse parameters')
            return

        scale = self.scene.spacing
        rect = QRectF(data['center'].x() * scale - data['radius_x'] * scale,
                      data['center'].y() * scale - data['radius_y'] * scale,
                      2 * data['radius_x'] * scale, 2 * data['radius_y'] * scale)
        item = QGraphicsEllipseItem(rect)
        item.setPen(self.default_pen)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        command = AddCommand(self.scene, item)
        command.execute()
        self.undo_stack.append(command)
        self.select_item(item)

    def on_draw_curve_by_params(self):
        dlg = BezierDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        points = dlg.get_data()
        if not points:
            print('Invalid Bezier curve parameters')
            return

        item = EditableBezierCurveItem(points, pen=self.default_pen, scene=self.scene)
        item.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        command = AddCommand(self.scene, item)
        command.execute()
        self.undo_stack.append(command)
        self.select_item(item)

    def finish_curve(self):
        if len(self.curve_points) > 1:
            curve = EditableBezierCurveItem(self.curve_points, pen=self.default_pen, scene=self.scene)
            curve.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
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
        if not data:
            print('Invalid parametric curve parameters')
            return

        t_vals = np.linspace(data['t_min'], data['t_max'], data['samples'])
        try:
            x_vals = [eval(data['x_expr'], {'t': t, **safe_globals}) for t in t_vals]
            y_vals = [eval(data['y_expr'], {'t': t, **safe_globals}) for t in t_vals]
        except Exception as e:
            print(f'Error in expression: {e}')
            return

        scale = self.scene.spacing
        x_vals = [x * scale for x in x_vals]
        y_vals = [y * scale for y in y_vals]

        path = QPainterPath()
        path.moveTo(x_vals[0], y_vals[0])
        for x, y in zip(x_vals[1:], y_vals[1:]):
            path.lineTo(x, y)

        item = QGraphicsPathItem(path)
        item.setPen(self.default_pen)
        item.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        command = AddCommand(self.scene, item)
        command.execute()
        self.undo_stack.append(command)
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

        if event.button() != Qt.LeftButton:
            return False

        item = self.scene.itemAt(scene_pos, self.ui.graphicsView.transform())
        ctrl_pressed = event.modifiers() & Qt.ControlModifier
        if item:
            if ctrl_pressed:
                if item not in self.bool_selection:
                    self.bool_selection.append(item)
                item.setSelected(not item.isSelected())
            else:
                self.clear_selection()
                self.bool_selection = [item]
                item.setSelected(True)
            self.moving_items = True
            self.move_initial_pos = scene_pos
            self.move_start_pos = scene_pos
        else:
            self.selection_rect = QGraphicsRectItem()
            self.selection_rect.setPen(self.selection_pen)
            self.selection_brush = QBrush(QColor(0, 0, 255, 50))
            self.selection_rect.setBrush(self.selection_brush)
            self.scene.addItem(self.selection_rect)
        return True

    def mouse_move(self, event: QMouseEvent):
        scene_pos = self.ui.graphicsView.mapToScene(event.position().toPoint())
        if self.moving_items:
            selected = self.scene.selectedItems()
            if selected:
                delta = scene_pos - self.move_start_pos
                for item in selected:
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
        if self.selection_rect:
            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None
        if self.moving_items:
            selected = self.scene.selectedItems()
            if selected:
                scene_pos = self.ui.graphicsView.mapToScene(event.position().toPoint())
                delta = scene_pos - self.move_initial_pos
                if delta.x() != 0 or delta.y() != 0:
                    command = MoveCommand(selected, delta)
                    self.undo_stack.append(command)
            self.moving_items = False

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

    def select_item(self, item):
        self.clear_selection()
        item.setSelected(True)
        self.bool_selection.append(item)

    def clear_selection(self):
        self.scene.clearSelection()
        self.bool_selection.clear()

    def update_selection(self, selection_rect):
        self.clear_selection()
        for item in self.scene.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                if selection_rect.intersects(item.sceneBoundingRect()):
                    item.setSelected(True)
                    self.bool_selection.append(item)

    def select_all(self):
        self.clear_selection()
        for item in self.scene.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                item.setSelected(True)
                self.bool_selection.append(item)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_A:
            self.select_all()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Z:
            if self.undo_stack:
                command = self.undo_stack.pop()
                command.undo()
                self.clear_selection()
        elif event.key() == Qt.Key_Delete:
            selected = self.scene.selectedItems()
            if selected:
                command = DeleteCommand(self.scene, selected)
                command.execute()
                self.undo_stack.append(command)

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
        axis, ok = QInputDialog.getItem(
            self, 'Выбор оси отражения',
            'Отразить по оси:',
            ['По горизонтали (X)', 'По вертикали (Y)', 'По диагонали (XY)'],
            0, False
        )
        if not ok:
            return

        if axis == 'По горизонтали (X)':
            transform = QTransform().scale(1, -1)
        elif axis == 'По вертикали (Y)':
            transform = QTransform().scale(-1, 1)
        elif axis == 'По диагонали (XY)':
            transform = QTransform().scale(-1, -1)
        else:
            return

        pen = item.pen()
        bounding_rect = item.sceneBoundingRect()

        if isinstance(item, QGraphicsLineItem):
            line = item.line()
            new_line = transform.map(line)
            new_item = QGraphicsLineItem(new_line)
        elif isinstance(item, QGraphicsRectItem):
            rect = item.rect()
            new_rect = transform.mapRect(rect)
            new_item = QGraphicsRectItem(new_rect)
        elif isinstance(item, QGraphicsEllipseItem):
            rect = item.rect()
            new_rect = transform.mapRect(rect)
            new_item = QGraphicsEllipseItem(new_rect)
        elif isinstance(item, QGraphicsPathItem):
            path = item.path()
            new_path = transform.map(path)
            new_item = QGraphicsPathItem(new_path)
        elif isinstance(item, EditableBezierCurveItem):
            points = item.get_control_points()
            new_points = [transform.map(p) for p in points]
            new_item = EditableBezierCurveItem(new_points, pen=pen, scene=self.scene)
        else:
            print(f'Тип фигуры не поддерживается для отражения: {type(item)}')
            return

        new_item.setPen(pen)
        new_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        command = AddCommand(self.scene, new_item)
        command.execute()
        self.undo_stack.append(command)
        self.select_item(new_item)

    def _item_to_scene_path(self, item):
        """
        Преобразует любой поддерживаемый QGraphicsItem
        в замкнутый QPainterPath в координатах сцены.
        """
        # 1) Берём локальный path
        if isinstance(item, QGraphicsPathItem):
            path = item.path()
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
            return None

        # 2) Замыкаем, если надо
        if not path.isEmpty():
            # первая точка
            e0 = path.elementAt(0)
            start = QPointF(e0.x, e0.y)
            end = path.currentPosition()
            if start != end:
                path.closeSubpath()

        # 3) Преобразуем в координаты сцены
        transform = item.sceneTransform()
        return transform.map(path)

    def boolean_operation(self, op_type: str):
        if len(self.bool_selection) != 2:
            QMessageBox.warning(self, 'Ошибка',
                                'Выберите сначала первую фигуру, потом вторую с зажатым Ctrl!')
            return

        p1 = self._item_to_scene_path(self.bool_selection[0])
        p2 = self._item_to_scene_path(self.bool_selection[1])

        if p1 is None or p2 is None:
            QMessageBox.warning(self, 'Ошибка',
                                'Булевы операции поддерживаются только для линий, прямоугольников, эллипсов и путей.')
            return

        if op_type == 'union':
            result = p1.united(p2)
        elif op_type == 'difference':
            result = p1.subtracted(p2)
        else:  # 'intersection'
            result = p1.intersected(p2)

        new_item = QGraphicsPathItem(result)
        new_item.setPen(self.default_pen)
        new_item.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        cmd = AddCommand(self.scene, new_item)
        cmd.execute()
        self.undo_stack.append(cmd)

        cmd = DeleteCommand(self.scene, self.bool_selection)
        cmd.execute()
        self.undo_stack.append(cmd)

        self.scene.clearSelection()
        new_item.setSelected(True)

        self.bool_selection.clear()

    def perform_rotate(self):
        # Должна быть ровно одна фигура
        if len(self.bool_selection) != 1:
            QMessageBox.warning(
                self, 'Ошибка',
                'Для поворота выберите ровно одну фигуру (обычный клик).'
            )
            return

        item = self.bool_selection[0]

        # Спрашиваем угол в градусах
        angle, ok = QInputDialog.getDouble(
            self, 'Поворот', 'Угол поворота (градусы):',
            0.0,  # начальное значение
            -3600.0,  # мин
            3600.0,  # макс
            1  # шаг
        )
        if not ok:
            return

        # Определяем точку поворота — центр boundingRect()
        center = item.sceneBoundingRect().center()
        item.setTransformOriginPoint(center)

        # Прибавляем угол к текущей ротации
        current_rotation = item.rotation()
        item.setRotation(current_rotation + angle)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()