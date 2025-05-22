# logic/undo_manager.py

from logic.undo_redo import Command


class UndoManager:
    def __init__(self):
        self.stack = []
        self.redo_stack = []

    def push(self, command: Command):
        command.do()
        self.stack.append(command)
        self.redo_stack.clear()

    def undo(self):
        if self.stack:
            command = self.stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.do()
            self.stack.append(command)

    def clear(self):
        self.stack.clear()
        self.redo_stack.clear()


# Global instance
undo_manager = UndoManager()
