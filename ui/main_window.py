import os
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileSystemModel,
    QTreeView,
    QLabel,
    QLineEdit,
    QAbstractItemView,
    QMenu,
    QStyle,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPoint, QDir

from ui.dialogs import InputNameDialog
from utils.file_ops import *
from utils.history import ActionHistory
from utils.utils import get_available_name, show_error


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python File Explorer")
        self.setGeometry(100, 100, 900, 600)
        self.current_path = QDir.currentPath()
        self.clipboard = None
        self.history = ActionHistory()
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        toolbar = QHBoxLayout()

        self.rename_input = QLineEdit()
        self.rename_input.setPlaceholderText("Enter new name here...")

        buttons = [
            (QStyle.SP_DirIcon, "New Folder", self.create_new_folder),
            (QStyle.SP_FileIcon, "New File", self.create_new_file),
            (QStyle.SP_ArrowBack, "Back", self.go_back),
            (QStyle.SP_DialogOpenButton, "Copy", lambda: self.set_clipboard("copy")),
            (QStyle.SP_DialogSaveButton, "Move", lambda: self.set_clipboard("move")),
            (QStyle.SP_DialogApplyButton, "Paste", self.perform_transfer),
            (QStyle.SP_FileDialogContentsView, "Rename", self.perform_rename),
            (QStyle.SP_TrashIcon, "Delete", self.perform_delete),
            (QStyle.SP_BrowserReload, "Refresh", self.refresh_view),
            (QStyle.SP_ArrowUp, "Undo", self.undo_action),
            (QStyle.SP_ArrowDown, "Redo", self.redo_action),
        ]

        for icon_type, tooltip, callback in buttons:
            btn = self.create_button(icon_type, tooltip)
            btn.clicked.connect(callback)
            toolbar.addWidget(btn)

        toolbar.addWidget(self.rename_input)
        self.status = QLabel("Ready")

        self.model = QFileSystemModel()
        self.model.setRootPath(self.current_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.tree.doubleClicked.connect(self.navigate)
        self.tree.setColumnWidth(0, 300)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)

        main_layout.addLayout(toolbar)
        main_layout.addWidget(self.tree)
        main_layout.addWidget(self.status)
        central_widget.setLayout(main_layout)

    def create_button(self, icon_type, tooltip):
        btn = QPushButton()
        btn.setIcon(self.style().standardIcon(icon_type))
        btn.setToolTip(tooltip)
        return btn

    def get_selected_path(self):
        index = self.tree.currentIndex()
        return self.model.filePath(index) if index.isValid() else None

    def go_back(self):
        self.current_path = os.path.dirname(self.current_path)
        self.tree.setRootIndex(self.model.index(self.current_path))

    def navigate(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.current_path = path
            self.tree.setRootIndex(self.model.index(self.current_path))
        else:
            os.startfile(path)

    def open_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return

        path = self.model.filePath(index)
        menu = QMenu()
        menu.addAction("Open", lambda: os.startfile(path))
        menu.addAction("Copy", lambda: self.set_clipboard("copy"))
        menu.addAction("Move", lambda: self.set_clipboard("move"))
        menu.addAction("Paste", self.perform_transfer)
        menu.addAction("Rename", self.perform_rename)
        menu.addAction("Delete", self.perform_delete)
        menu.addSeparator()
        menu.addAction("Refresh", self.refresh_view)
        menu.exec(self.tree.viewport().mapToGlobal(position))

    def set_clipboard(self, mode):
        if path := self.get_selected_path():
            self.clipboard = (path, mode)
            self.status.setText(f"{mode.title()} set: {os.path.basename(path)}")

    def perform_transfer(self):
        if not self.clipboard:
            return

        src, op = self.clipboard
        dst = os.path.join(self.current_path, os.path.basename(src))

        if os.path.exists(dst):
            show_error("Destination already exists.", self)
            return

        if op == "copy":
            success, error = copy_path(src, dst)
            action = ("delete", dst)
        elif op == "move":
            success, error = move_path(src, dst)
            action = ("move", dst, src)

        if success:
            self.history.add_action(action)
            self.status.setText(f"{op.title()} completed")
            self.clipboard = None
            self.refresh_view()
        else:
            show_error(error, self)

    def perform_rename(self):
        if path := self.get_selected_path():
            new_name = self.rename_input.text().strip()
            if new_name:
                new_path = os.path.join(os.path.dirname(path), new_name)
                success, error = rename_path(path, new_path)
                if success:
                    self.history.add_action(("rename", new_path, path))
                    self.status.setText("Renamed successfully")
                    self.refresh_view()
                else:
                    show_error(error, self)

    def perform_delete(self):
        if path := self.get_selected_path():
            success, error = delete_path(path)
            if success:
                self.history.add_action(("create", path))
                self.status.setText("Deleted successfully")
                self.refresh_view()
            else:
                show_error(error, self)

    def refresh_view(self):
        self.tree.viewport().update()

    def create_new_folder(self):
        dialog = InputNameDialog(
            "New Folder", "Enter folder name:", QStyle.SP_DirIcon, self
        )
        name, ok = dialog.get_input()
        if not ok:
            return

        base_name = name or "Folder Baru"
        folder_name = get_available_name(self.current_path, base_name)
        path = os.path.join(self.current_path, folder_name)

        success, error = create_folder(path)
        if success:
            self.history.add_action(("delete", path))
            self.status.setText(f"Folder created: {folder_name}")
            self.refresh_view()
        else:
            show_error(error, self)

    def create_new_file(self):
        dialog = InputNameDialog(
            "New File", "Enter file name:", QStyle.SP_FileIcon, self
        )
        name, ok = dialog.get_input()
        if not ok:
            return

        if name:
            base, ext = os.path.splitext(name)
            ext = ext or ".txt"
        else:
            base, ext = "File Baru", ".txt"

        file_name = get_available_name(self.current_path, base, ext)
        path = os.path.join(self.current_path, file_name)

        success, error = create_file(path)
        if success:
            self.history.add_action(("delete", path))
            self.status.setText(f"File created: {file_name}")
            self.refresh_view()
        else:
            show_error(error, self)

    def undo_action(self):
        action = self.history.undo()
        if not action:
            self.status.setText("Nothing to undo.")
            return

        try:
            if action[0] == "delete":
                success, error = delete_path(action[1])
            elif action[0] == "move":
                success, error = move_path(action[1], action[2])
            elif action[0] == "rename":
                success, error = rename_path(action[1], action[2])
            elif action[0] == "create":
                show_error("Cannot restore deleted item.", self)
                return

            if success:
                self.status.setText(f"Undo: {action[0]}")
                self.refresh_view()
            else:
                raise Exception(error)
        except Exception as e:
            show_error(str(e), self)

    def redo_action(self):
        action = self.history.redo()
        if not action:
            self.status.setText("Nothing to redo.")
            return

        try:
            if action[0] == "delete":
                success, error = delete_path(action[1])
            elif action[0] == "move":
                success, error = move_path(action[2], action[1])
            elif action[0] == "rename":
                success, error = rename_path(action[2], action[1])
            elif action[0] == "create":
                success = os.path.exists(action[1])

            if success:
                self.status.setText(f"Redo: {action[0]}")
                self.refresh_view()
            else:
                raise Exception(error)
        except Exception as e:
            show_error(str(e), self)
