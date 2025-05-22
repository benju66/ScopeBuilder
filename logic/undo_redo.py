# logic/undo_redo.py

class Command:
    """A reversible command with do and undo functions."""
    def __init__(self, do_func, undo_func, description=""):
        self.do_func = do_func
        self.undo_func = undo_func
        self.description = description

    def do(self):
        self.do_func()

    def undo(self):
        self.undo_func()


class UndoRedoStack:
    """Maintains undo/redo history using stacks."""
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def push(self, command: Command):
        """Execute and store a new command."""
        command.do()
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def undo(self):
        """Undo the last command."""
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self):
        """Redo the last undone command."""
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.do()
            self.undo_stack.append(command)

    def can_undo(self):
        return bool(self.undo_stack)

    def can_redo(self):
        return bool(self.redo_stack)

    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
