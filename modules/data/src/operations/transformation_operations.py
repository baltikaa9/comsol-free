from PySide6.QtGui import QTransform
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QInputDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QWidget

from src.commands.add_command import AddCommand
from src.commands.rotate_command import RotateCommand
from src.services.command_service import CommandService
from src.services.selection_service import SelectionService
from src.shapes.ellipse_item import EllipseItem
from src.shapes.line_item import LineItem
from src.shapes.parametric_curve_item import ParametricCurveItem
from src.shapes.rectangle_item import RectangleItem
from src.widgets.editable_bezier import EditableBezierCurveItem
from src.widgets.grid_scene import GridScene


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

        if isinstance(item, LineItem):
            line = item.line()
            new_line = transform.map(line)
            new_item = LineItem(new_line)
        elif isinstance(item, RectangleItem):
            rect = item.rect()
            new_rect = transform.mapRect(rect)
            new_item = RectangleItem(new_rect)
        elif isinstance(item, EllipseItem):
            rect = item.rect()
            new_rect = transform.mapRect(rect)
            new_item = EllipseItem(new_rect)
        elif isinstance(item, ParametricCurveItem):
            path = item.path()
            new_path = transform.map(path)
            new_item = ParametricCurveItem(new_path)
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
        self.selection_service.clear_and_select_item(new_item)

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
