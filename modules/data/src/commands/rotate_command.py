from PySide6.QtWidgets import QGraphicsItem

from src.commands.command import Command


class RotateCommand(Command):
    def __init__(self, item: QGraphicsItem, angle_delta: float):
        self.item = item
        self.angle_delta = angle_delta
        self.start_rotation = item.rotation()

    def execute(self):
        self.item.setRotation(self.start_rotation + self.angle_delta)

    def undo(self):
        self.item.setRotation(self.start_rotation)
