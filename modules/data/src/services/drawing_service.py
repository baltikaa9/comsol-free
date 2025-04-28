import math

import numpy as np
from PySide6.QtCore import Qt, QRectF, QLineF, QSizeF, QPointF
from PySide6.QtGui import QPen, QPainterPath
from PySide6.QtWidgets import (QGraphicsLineItem, QGraphicsEllipseItem,
                               QGraphicsRectItem, QDialog, QGraphicsPathItem, QGraphicsItem, QWidget)

from modules.data.src.commands.add_command import AddCommand
from modules.data.src.dialogs.dialog import Dialog
from modules.data.src.dialogs.dialog_factory import DialogFactory
from modules.data.src.editable_bezier import EditableBezierCurveItem
from modules.data.src.grid_scene import GridScene
from modules.data.src.services.command_service import CommandService
from modules.data.src.services.selection_service import SelectionService


class DrawingService:
    def __init__(
            self,
            scene: GridScene,
            dialog_parent: QWidget,
            command_service: CommandService,
            selection_service: SelectionService,
    ):
        self.scene = scene
        self.dialog_parent = dialog_parent
        self.command_service = command_service
        self.selection_service = selection_service

        self.default_pen = QPen(Qt.black, 0)

    def draw_line_by_params(self):
        data = self.__get_data(DialogFactory.create_dialog('line', self.dialog_parent))

        scale = self.scene.spacing
        line = QLineF(data['start'] * scale, data['end'] * scale)
        item = QGraphicsLineItem(line)
        item.setPen(self.default_pen)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.command_service.execute(AddCommand(self.scene, item))
        self.selection_service.select_item(item)

    def draw_rect_by_params(self):
        data = self.__get_data(DialogFactory.create_dialog('rect', self.dialog_parent))

        scale = self.scene.spacing
        rect = QRectF(data['top_left'] * scale, QSizeF(data['width'] * scale, data['height'] * scale))
        item = QGraphicsRectItem(rect)
        item.setPen(self.default_pen)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.command_service.execute(AddCommand(self.scene, item))
        self.selection_service.select_item(item)

    def draw_ellipse_by_params(self):
        data = self.__get_data(DialogFactory.create_dialog('ellipse', self.dialog_parent))

        scale = self.scene.spacing
        rect = QRectF(data['center'].x() * scale - data['radius_x'] * scale,
                      data['center'].y() * scale - data['radius_y'] * scale,
                      2 * data['radius_x'] * scale, 2 * data['radius_y'] * scale)
        item = QGraphicsEllipseItem(rect)
        item.setPen(self.default_pen)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.command_service.execute(AddCommand(self.scene, item))
        self.selection_service.select_item(item)

    def draw_curve_by_params(self):
        data = self.__get_data(DialogFactory.create_dialog('bezier', self.dialog_parent))

        item = EditableBezierCurveItem(data, pen=self.default_pen, scene=self.scene)
        item.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        self.command_service.execute(AddCommand(self.scene, item))
        self.selection_service.select_item(item)

    def draw_parametric(self):
        data = self.__get_data(DialogFactory.create_dialog('parametric', self.dialog_parent))

        safe_globals = {
            'math': math,
            **{name: getattr(math, name) for name in dir(math) if not name.startswith('_')}
        }


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

    def __get_data(self, dialog: Dialog) -> dict[str, str | float | int | QPointF] | None:
        if dialog.exec() != QDialog.Accepted:
            return None

        data = dialog.get_data()
        if not data:
            print('Invalid parameters')
            return None

        return data
