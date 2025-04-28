import math

import numpy as np
from PySide6.QtCore import Qt, QPointF, QRectF, QEvent, QLineF, QSizeF
from PySide6.QtGui import QMouseEvent, QPen, QColor, QBrush, QPainter, QPainterPath, QTransform, QKeyEvent
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsLineItem, QGraphicsEllipseItem,
                               QGraphicsRectItem, QGraphicsView, QDialog, QGraphicsPathItem, QInputDialog,
                               QGraphicsItem, QMessageBox)

from modules.data.src.commands.command import Command
from modules.data.src.commands.rotate_command import RotateCommand
from modules.data.src.dialogs.bezier_dialog import BezierDialog
from modules.data.src.dialogs.ellipse_dialog import EllipseDialog
from modules.data.src.dialogs.line_dialog import LineDialog
from modules.data.src.dialogs.rect_dialog import RectDialog
from modules.data.src.commands.add_command import AddCommand
from modules.data.src.commands.delete_command import DeleteCommand
from modules.data.src.commands.move_command import MoveCommand
from modules.data.src.dialogs.parametric_dialog import ParametricDialog
from modules.data.src.editable_bezier import EditableBezierCurveItem
from modules.data.src.event_handler import EventHandler
from modules.data.src.grid_scene import GridScene
from modules.data.src.services.command_service import CommandService
from modules.data.src.services.selection_service import SelectionService
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

        self.selection_service = SelectionService(self.scene)
        self.command_service = CommandService()
        self.event_handler = EventHandler(self.scene, self.ui.graphicsView, self.selection_service, self.command_service)

        self.default_pen = QPen(Qt.black, 0)

        self.dragging = False
        self.drag_start_pos = QPointF()

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
        self.command_service.execute(AddCommand(self.scene, item))
        self.selection_service.select_item(item)

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
        self.command_service.execute(AddCommand(self.scene, item))
        self.selection_service.select_item(item)

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
        self.command_service.execute(AddCommand(self.scene, item))
        self.selection_service.select_item(item)

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
        self.command_service.execute(AddCommand(self.scene, item))
        self.selection_service.select_item(item)

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
        self.command_service.execute(AddCommand(self.scene, item))
        self.selection_service.select_item(item)

    def eventFilter(self, obj, event: QEvent):
        if obj is self.ui.graphicsView.viewport():
            return self.event_handler.event_filter(event)

        return super().eventFilter(obj, event)

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

    def keyPressEvent(self, event: QKeyEvent):
        self.event_handler.key_press_event(event)

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
        self.command_service.execute(AddCommand(self.scene, new_item))
        self.selection_service.select_item(new_item)

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
        sel = self.selection_service.bool_selection
        if len(sel) != 2:
            QMessageBox.warning(self, 'Ошибка',
                                'Выберите сначала первую фигуру, потом вторую с зажатым Ctrl!')
            return

        p1 = self._item_to_scene_path(sel[0])
        p2 = self._item_to_scene_path(sel[1])

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
        self.command_service.execute(AddCommand(self.scene, new_item))

        self.command_service.execute(DeleteCommand(self.scene, sel))

        self.scene.clearSelection()
        new_item.setSelected(True)

        sel.clear()

    def perform_rotate(self):
        sel = self.selection_service.bool_selection
        # Должна быть ровно одна фигура
        if len(sel) != 1:
            QMessageBox.warning(
                self, 'Ошибка',
                'Для поворота выберите ровно одну фигуру (обычный клик).'
            )
            return

        item = sel[0]

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

        self.command_service.execute(RotateCommand(item, angle))


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()