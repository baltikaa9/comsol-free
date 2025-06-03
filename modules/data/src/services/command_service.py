from src.commands.command import Command


class CommandService:
    def __init__(self):
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []

    def append(self, command: Command):
        self.undo_stack.append(command)

    def execute(self, command: Command):
        self.append(command)
        command.execute()

    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)
