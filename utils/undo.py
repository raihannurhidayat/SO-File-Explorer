import shutil
import os


class UndoRedoManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def register_action(self, undo_func, redo_func):
        self.undo_stack.append((undo_func, redo_func))
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            undo_func, redo_func = self.undo_stack.pop()
            undo_func()
            self.redo_stack.append((undo_func, redo_func))

    def redo(self):
        if self.redo_stack:
            undo_func, redo_func = self.redo_stack.pop()
            redo_func()
            self.undo_stack.append((undo_func, redo_func))

    def can_undo(self):
        return bool(self.undo_stack)

    def can_redo(self):
        return bool(self.redo_stack)