from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QWidget

from modules.data.src.commands.add_command import AddCommand
from modules.data.src.commands.delete_command import DeleteCommand
from modules.data.src.grid_scene import GridScene
from modules.data.src.services.command_service import CommandService
from modules.data.src.services.drawing_service import DrawingService
from modules.data.src.services.selection_service import SelectionService


class BooleanOperations:
    def __init__(
            self,
            parent: QWidget,
            scene: GridScene,
            command_service: CommandService,
            drawing_service: DrawingService,
            selection_service: SelectionService
    ):
        self.parent = parent
        self.scene = scene
        self.command_service = command_service
        self.drawing_service = drawing_service
        self.selection_service = selection_service

    def perform_union(self):
        self.__boolean_operation('union')

    def perform_difference(self):
        self.__boolean_operation('difference')

    def perform_intersection(self):
        self.__boolean_operation('intersection')

    def __boolean_operation(self, op_type: str):
        sel = self.selection_service.bool_selection
        if len(sel) != 2:
            QMessageBox.warning(
                self.parent,
                'Ошибка',
                'Выберите сначала первую фигуру, потом вторую с зажатым Ctrl!')
            return

        p1 = self.__item_to_scene_path(sel[0])
        p2 = self.__item_to_scene_path(sel[1])

        if p1 is None or p2 is None:
            QMessageBox.warning(
                self.parent,
                'Ошибка',
                'Булевы операции поддерживаются только для линий, прямоугольников, эллипсов и путей.')
            return

        if op_type == 'union':
            result = p1.united(p2)
        elif op_type == 'difference':
            result = p1.subtracted(p2)
        else:  # 'intersection'
            result = p1.intersected(p2)

        new_item = QGraphicsPathItem(result)
        new_item.setPen(self.drawing_service.default_pen)
        new_item.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        self.command_service.execute(AddCommand(self.scene, new_item))

        self.command_service.execute(DeleteCommand(self.scene, sel))

        self.scene.clearSelection()
        new_item.setSelected(True)

        sel.clear()

    def __item_to_scene_path(self, item: QGraphicsItem) -> QPainterPath | None:
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