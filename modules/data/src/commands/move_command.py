from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsItem

from .command import Command


class MoveCommand(Command):
    def __init__(self, items: list[QGraphicsItem], delta: QPointF):
        self.items = items
        self.delta = delta

    def execute(self):
        for item in self.items:
            item.moveBy(self.delta.x(), self.delta.y())

    def undo(self):
        for item in self.items:
            item.moveBy(-self.delta.x(), -self.delta.y())
