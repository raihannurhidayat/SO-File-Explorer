import os
from PySide6.QtWidgets import (
    QTreeView,
    QFileSystemModel,
    QMenu,
    QAbstractItemView,
    QSizePolicy,
)
from PySide6.QtCore import Signal, QObject, Qt, QDir
from utils.navigation_utils import show_error


class Sidebar(QObject):
    path_selected = Signal(str)

    def __init__(self, start_path, parent=None):
        super().__init__()
        self.parent = parent  # FileManager reference for actions if needed

        # Create the model for the tree view
        self.model = QFileSystemModel()
        # Show directories and drives
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Drives)
        # Empty string shows the root of the file system (all drives)
        self.model.setRootPath("")

        # tree
        self.tree = QTreeView()
        self.tree.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.tree.setModel(self.model)

        self.tree.setRootIndex(self.model.index(""))
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setSortingEnabled(True)

        # Only show column
        for i in range(1, self.model.columnCount()):
            self.tree.hideColumn(i)

        self.tree.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.clicked.connect(self._emit_path_selected)

        # Set the minimum width for the sidebar
        self.tree.setMinimumWidth(200)

        self.tree.setIndentation(10)
        # Expand the drives by default
        self.tree.expandToDepth(0)

        # Find and select the current path
        index = self.model.index(start_path)
        if index.isValid():
            self.tree.setCurrentIndex(index)
            # Expand to make the current path visible
            parent_index = self.model.parent(index)
            while parent_index.isValid():
                self.tree.expand(parent_index)
                parent_index = self.model.parent(parent_index)

    def widget(self):
        return self.tree

    def set_root_path(self, path):
        """Update the selection in the sidebar to match the current path"""
        if os.path.exists(path):
            # Don't change the root - just select the path
            index = self.model.index(path)
            if index.isValid():
                self.tree.setCurrentIndex(index)
                self.tree.scrollTo(index)

                # Expand to make sure the path is visible
                parent_index = self.model.parent(index)
                while parent_index.isValid():
                    self.tree.expand(parent_index)
                    parent_index = self.model.parent(parent_index)
        else:
            show_error(f"Path does not exist: {path}", self.parent)

    def get_selected_path(self):
        index = self.tree.currentIndex()
        if index.isValid():
            return self.model.filePath(index)
        return None

    def show_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu()
        menu.addAction("Copy", lambda: self.parent.copy_selected())
        menu.addAction("Cut", lambda: self.parent.move_selected())
        menu.addAction("Paste", lambda: self.parent.paste_selected())
        menu.addAction("Delete", lambda: self.parent.delete_selected())
        menu.addAction("Rename", lambda: self.parent.rename_selected())
        menu.exec(self.tree.viewport().mapToGlobal(position))

    def _emit_path_selected(self, index):
        path = self.model.filePath(index)
        self.path_selected.emit(path)
