from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem

from .command import Command


class DeleteCommand(Command):
    def __init__(self, scene: QGraphicsScene, items: list[QGraphicsItem], mesh_map=None):
        self.scene = scene
        self.items = items  # Список удаляемых объектов
        self.selected_items = set(items)  # Для восстановления выделения
        self.mesh_map = mesh_map or {}
        self.removed_mesh = {}

    def execute(self):
        for item in self.items:
            if item in self.mesh_map:
                for mesh_item in self.mesh_map[item]:
                    self.scene.removeItem(mesh_item)
                self.removed_mesh[item] = self.mesh_map.pop(item)

            self.scene.removeItem(item)

    def undo(self):
        for item in self.items:
            self.scene.addItem(item)

            if item in self.removed_mesh:
                for mesh_item in self.removed_mesh[item]:
                    self.scene.addItem(mesh_item)
                self.mesh_map[item] = self.removed_mesh[item]