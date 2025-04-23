from .command import Command


class MoveCommand(Command):
    def __init__(self, items, delta):
        self.items = items  # Список перемещаемых объектов
        self.delta = delta  # Вектор перемещения

    def execute(self):
        for item in self.items:
            item.moveBy(self.delta.x(), self.delta.y())

    def undo(self):
        for item in self.items:
            item.moveBy(-self.delta.x(), -self.delta.y())
