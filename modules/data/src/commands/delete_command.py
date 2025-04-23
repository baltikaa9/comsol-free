from .command import Command


class DeleteCommand(Command):
    def __init__(self, scene, items):
        self.scene = scene
        self.items = items  # Список удаляемых объектов
        self.selected_items = set(items)  # Для восстановления выделения

    def execute(self):
        for item in self.items:
            self.scene.removeItem(item)

    def undo(self):
        for item in self.items:
            self.scene.addItem(item)