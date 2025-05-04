from PySide6.QtGui import QTransform
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtWidgets import QGraphicsLineItem, QWidget, QGraphicsItem
from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtWidgets import QInputDialog
from PySide6.QtWidgets import QMessageBox

from modules.data.src.commands.add_command import AddCommand
from modules.data.src.commands.rotate_command import RotateCommand
from modules.data.src.widgets.editable_bezier import EditableBezierCurveItem
from modules.data.src.widgets.grid_scene import GridScene
from modules.data.src.services.command_service import CommandService
from modules.data.src.services.selection_service import SelectionService


class TransformationOperations:
    def __init__(
            self,
            parent: QWidget,
            scene: GridScene,
            command_service: CommandService,
            selection_service: SelectionService,
    ):
        self.parent = parent
        self.scene = scene
        self.command_service = command_service
        self.selection_service = selection_service

    def perform_mirror(self):
        selected = self.scene.selectedItems()
        if len(selected) != 1:
            print(f'Выберите одну фигуру для отражения! {len(selected)}')
            return

        item = selected[0]
        axis, ok = QInputDialog.getItem(
            self.parent,
            'Выбор оси отражения',
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

    def perform_rotate(self):
        sel = self.selection_service.bool_selection
        # Должна быть ровно одна фигура
        if len(sel) != 1:
            QMessageBox.warning(
                self.parent,
                'Ошибка',
                'Для поворота выберите ровно одну фигуру (обычный клик).'
            )
            return

        item = sel[0]

        # Спрашиваем угол в градусах
        angle, ok = QInputDialog.getDouble(
            self.parent,
            'Поворот', 'Угол поворота (градусы):',
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
