import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFileSystemModel, QTreeView, QLabel,
    QAbstractItemView, QLineEdit, QToolBar, QWidgetAction, QStyle
)
from PySide6.QtCore import Qt
from utils import open_file, show_error


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python File Explorer")
        self.setGeometry(100, 100, 1000, 600)

        self.current_path = os.getcwd()
        self.back_stack = []
        self.forward_stack = []

        self.init_ui()

    def init_ui(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        self.back_action = QWidgetAction(self)
        self.back_action.setIconText("◀")
        self.back_action.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowBack))
        self.back_action.triggered.connect(self.go_back)
        self.back_action.setEnabled(False)
        toolbar.addAction(self.back_action)

        self.forward_action = QWidgetAction(self)
        self.forward_action.setIconText("▶")
        self.forward_action.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowForward)
        )
        self.forward_action.triggered.connect(self.go_forward)
        self.forward_action.setEnabled(False)
        toolbar.addAction(self.forward_action)

        up_action = QWidgetAction(self)
        up_action.setIconText("🔼")
        up_action.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        up_action.triggered.connect(self.go_up)
        toolbar.addAction(up_action)

        refresh_action = QWidgetAction(self)
        refresh_action.setIconText("🔄")
        refresh_action.setIcon(
            self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_action.triggered.connect(self.refresh)
        toolbar.addAction(refresh_action)

        self.path_input = QLineEdit(self.current_path)
        self.path_input.returnPressed.connect(self.enter_path)
        toolbar.addWidget(self.path_input)

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

    def navigate(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.back_stack.append(self.current_path)
            self.forward_stack.clear()
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
            self.back_stack.append(self.current_path)
            self.forward_stack.clear()
            self.update_buttons()
            self.set_path(new_path)
        else:
            show_error(f"Invalid path: {new_path}", self)

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.back_stack.append(self.current_path)
            self.forward_stack.clear()
            self.update_buttons()
            self.set_path(parent)

    def go_back(self):
        if self.back_stack:
            self.forward_stack.append(self.current_path)
            self.current_path = self.back_stack.pop()
            self.set_path(self.current_path)
            self.update_buttons()

    def go_forward(self):
        if self.forward_stack:
            self.back_stack.append(self.current_path)
            self.current_path = self.forward_stack.pop()
            self.set_path(self.current_path)
            self.update_buttons()

    def refresh(self):
        self.set_path(self.current_path)

    def update_buttons(self):
        self.back_action.setEnabled(len(self.back_stack) > 0)
        self.forward_action.setEnabled(len(self.forward_stack) > 0)
