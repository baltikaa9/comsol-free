from .command import Command


class AddCommand(Command):
    def __init__(self, scene, item):
        self.scene = scene
        self.item = item

    def execute(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)