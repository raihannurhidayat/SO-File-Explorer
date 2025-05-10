import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFileSystemModel, QTreeView, QLabel,
    QAbstractItemView, QLineEdit, QToolBar, QWidgetAction, QStyle
)
from PySide6.QtCore import Qt
from utils.history import HistoryManager
from utils.navigation_utils import is_valid_directory, go_up
from utils.undo import UndoRedoManager
from utils.file_utils import (open_file, show_error, copy_item,
                              move_item, delete_item, paste_item, rename_item)


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python File Explorer")
        self.setGeometry(100, 100, 1000, 600)

        self.current_path = os.getcwd()

        self.history = HistoryManager()
        self.undo_redo = UndoRedoManager()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status = QLabel("Ready")

        self.model = QFileSystemModel()
        self.model.setRootPath(self.current_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.tree.doubleClicked.connect(self.navigate)
        self.tree.setColumnWidth(0, 300)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.tree)
        layout.addWidget(self.status)

        # NAVIGATION TOOLBAR
        navbar = QToolBar()
        navbar.setFloatable(False)
        navbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, navbar)
        self.addToolBarBreak(Qt.TopToolBarArea)

        # RIBBON TOOLBAR
        ribbon = QToolBar("File Actions")
        ribbon.setFloatable(False)
        ribbon.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, ribbon)

        # CONTEXT MENU
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        # NAVIGATION ACTIONS
        self.back_action = QWidgetAction(self)
        self.back_action.setIconText("Back to previous location")
        self.back_action.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowBack))
        self.back_action.triggered.connect(self.go_back)
        self.back_action.setEnabled(False)
        navbar.addAction(self.back_action)

        self.forward_action = QWidgetAction(self)
        self.forward_action.setIconText("Forward to next location")
        self.forward_action.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowForward)
        )
        self.forward_action.triggered.connect(self.go_forward)
        self.forward_action.setEnabled(False)
        navbar.addAction(self.forward_action)

        up_action = QWidgetAction(self)
        up_action.setIconText("Go up one level")
        up_action.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        up_action.triggered.connect(self.go_up)
        navbar.addAction(up_action)

        refresh_action = QWidgetAction(self)
        refresh_action.setIconText("Refresh")
        refresh_action.setIcon(
            self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_action.triggered.connect(self.refresh)
        navbar.addAction(refresh_action)

        self.path_input = QLineEdit(self.current_path)
        self.path_input.returnPressed.connect(self.enter_path)
        navbar.addWidget(self.path_input)

        # RIBBON ACTIONS
        copy_btn = ribbon.addAction("Copy")
        copy_btn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        copy_btn.triggered.connect(self.copy_selected)

        move_btn = ribbon.addAction("Cut")
        move_btn.setIcon(self.style().standardIcon(
            QStyle.SP_ToolBarHorizontalExtensionButton))
        move_btn.triggered.connect(self.move_selected)

        paste_btn = ribbon.addAction("Paste")
        paste_btn.setIcon(self.style().standardIcon(
            QStyle.SP_TitleBarNormalButton))
        paste_btn.triggered.connect(self.paste_selected)

        delete_btn = ribbon.addAction("Delete")
        delete_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_btn.triggered.connect(self.delete_selected)

        rename_btn = ribbon.addAction("Rename")
        rename_btn.setIcon(self.style().standardIcon(
            QStyle.SP_FileDialogContentsView))
        rename_btn.triggered.connect(self.rename_selected)

        undo_btn = ribbon.addAction("Undo")
        undo_btn.setIcon(self.style().standardIcon(
            QStyle.SP_DialogCancelButton))
        # undo_btn.setEnabled(False)
        undo_btn.triggered.connect(self.undo_action)

        redo_btn = ribbon.addAction("Redo")
        redo_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        # redo_btn.setEnabled(False)
        redo_btn.triggered.connect(self.redo_action)

    def navigate(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.history.push_back(self.current_path)
            self.update_buttons()
            self.set_path(path)
        else:
            self.status.setText(f"Opening file: {path}")
            open_file(path, self)

    def set_path(self, path):
        if os.path.exists(path):
            self.current_path = path
            self.tree.setRootIndex(self.model.index(path))
            self.path_input.setText(path)
            self.status.setText(f"Opened: {path}")
        else:
            show_error(f"Path does not exist: {path}", self)

    def enter_path(self):
        new_path = self.path_input.text()
        if os.path.isdir(new_path):
            self.history.push_back(self.current_path)
            self.update_buttons()
            self.set_path(new_path)
        else:
            show_error(f"Invalid path: {new_path}", self)

    def go_back(self):
        if self.history.can_go_back():
            self.set_path(self.history.go_back(self.current_path))
            self.update_buttons()

    def go_forward(self):
        if self.history.can_go_forward():
            self.set_path(self.history.go_forward(self.current_path))
            self.update_buttons()

    def go_up(self):
        parent = go_up(self.current_path)
        if parent != self.current_path:
            self.history.push_back(self.current_path)
            self.set_path(parent)
            self.update_buttons()

    def refresh(self):
        self.set_path(self.current_path)

    def update_buttons(self):
        self.back_action.setEnabled(len(self.history.back_stack) > 0)
        self.forward_action.setEnabled(len(self.history.forward_stack) > 0)

    # FILE & FOLDER ACTIONS
    def get_selected_path(self):
        index = self.tree.currentIndex()
        if index.isValid():
            return self.model.filePath(index)
        return None

    def copy_selected(self):
        path = self.get_selected_path()
        if path:
            output = copy_item(path)
            self.status.setText(output)

    def move_selected(self):
        path = self.get_selected_path()
        if path:
            output = move_item(path)
            self.status.setText(output)

    def paste_selected(self):
        output = paste_item(self.current_path, self, self.undo_redo)

        self.refresh()
        self.status.setText(output)

    def delete_selected(self):
        path = self.get_selected_path()
        if path:
            output = delete_item(path, self)

            self.refresh()
            self.status.setText(output)

    def rename_selected(self):
        path = self.get_selected_path()

        if path:
            output = rename_item(path, self, self.undo_redo)

            self.refresh()
            self.status.setText(output)

    def undo_action(self):
        self.undo_redo.undo()
        self.refresh()

    def redo_action(self):
        self.undo_redo.redo()
        self.refresh()

    # CONTEXT MENU
    def show_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return

        from PySide6.QtWidgets import QMenu

        context_menu = QMenu()
        context_menu.addAction("Copy", self.copy_selected)
        context_menu.addAction("Cut", self.move_selected)
        context_menu.addAction("Paste", self.paste_selected)
        context_menu.addAction("Delete", self.delete_selected)
        context_menu.addAction("Rename", self.rename_selected)
        context_menu.exec(self.tree.viewport().mapToGlobal(position))
