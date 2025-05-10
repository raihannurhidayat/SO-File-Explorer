import os
import shutil
import subprocess
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileSystemModel,
    QTreeView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QMenu,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QStyle,
    QInputDialog,
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QPoint


# Dialog input nama
class InputNameDialog(QDialog):
    def __init__(self, title="Input", label="Enter name:", icon_type=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(320, 130)
        layout = QVBoxLayout()
        if icon_type:
            icon_layout = QHBoxLayout()
            icon_label = QLabel()
            icon = self.style().standardIcon(icon_type)
            icon_label.setPixmap(icon.pixmap(24, 24))
            icon_layout.addWidget(icon_label)
            icon_layout.addWidget(QLabel(label))
            layout.addLayout(icon_layout)
        else:
            layout.addWidget(QLabel(label))
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Leave empty for default name...")
        layout.addWidget(self.input_field)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_input(self):
        result = self.exec()
        return self.input_field.text().strip(), result == QDialog.Accepted


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python File Explorer")
        self.setGeometry(100, 100, 900, 600)

        self.current_path = os.getcwd()  # Awal relatif ke working directory
        self.clipboard = None
        self.undo_stack = []
        self.redo_stack = []

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        toolbar = QHBoxLayout()

        self.rename_input = QLineEdit()
        self.rename_input.setPlaceholderText("Enter new name here...")

        toolbar.addWidget(
            self.create_button(QStyle.SP_DirIcon, "New Folder", self.create_new_folder)
        )
        toolbar.addWidget(
            self.create_button(QStyle.SP_FileIcon, "New File", self.create_new_file)
        )
        toolbar.addWidget(self.create_button(QStyle.SP_ArrowBack, "Back", self.go_back))
        toolbar.addWidget(
            self.create_button(
                QStyle.SP_DialogOpenButton, "Copy", lambda: self.set_clipboard("copy")
            )
        )
        toolbar.addWidget(
            self.create_button(
                QStyle.SP_DialogSaveButton, "Move", lambda: self.set_clipboard("move")
            )
        )
        toolbar.addWidget(
            self.create_button(
                QStyle.SP_DialogApplyButton, "Paste", self.perform_transfer
            )
        )
        toolbar.addWidget(
            self.create_button(
                QStyle.SP_FileDialogContentsView, "Rename", self.perform_rename
            )
        )
        toolbar.addWidget(
            self.create_button(QStyle.SP_TrashIcon, "Delete", self.perform_delete)
        )
        toolbar.addWidget(
            self.create_button(QStyle.SP_BrowserReload, "Refresh", self.refresh_view)
        )
        toolbar.addWidget(
            self.create_button(QStyle.SP_ArrowUp, "Undo", self.undo_action)
        )
        toolbar.addWidget(
            self.create_button(QStyle.SP_ArrowDown, "Redo", self.redo_action)
        )

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

    def create_button(self, icon_type, tooltip, slot):
        btn = QPushButton()
        icon = self.style().standardIcon(icon_type)
        btn.setIcon(icon)
        btn.setToolTip(tooltip)
        btn.clicked.connect(slot)
        return btn

    def get_selected_path(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return None
        return self.model.filePath(index)

    def go_back(self):
        self.current_path = os.path.dirname(self.current_path)
        self.tree.setRootIndex(self.model.index(self.current_path))

    def navigate(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.current_path = path
            self.tree.setRootIndex(self.model.index(self.current_path))
        else:
            self.open_file(path)

    def open_file(self, path):
        try:
            os.startfile(path)
        except Exception as e:
            self.show_error(str(e))

    def open_context_menu(self, position: QPoint):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return
        selected_path = self.model.filePath(index)
        menu = QMenu()
        menu.addAction("Open", lambda: self.open_file(selected_path))
        menu.addAction(
            "Open in VS Code", lambda: subprocess.Popen(["code", selected_path])
        )
        menu.addAction("Copy", lambda: self.set_clipboard("copy"))
        menu.addAction("Move", lambda: self.set_clipboard("move"))
        menu.addAction("Paste", self.perform_transfer)
        menu.addAction("Rename", self.perform_rename)
        menu.addAction("Delete", self.perform_delete)
        menu.addSeparator()
        menu.addAction("Refresh", self.refresh_view)
        menu.exec(self.tree.viewport().mapToGlobal(position))

    def set_clipboard(self, mode):
        path = self.get_selected_path()
        if path:
            self.clipboard = (path, mode)
            self.status.setText(f"{mode.title()} set: {os.path.basename(path)}")

    def perform_transfer(self):
        if not self.clipboard:
            return
        src, op = self.clipboard
        dst = os.path.join(self.current_path, os.path.basename(src))
        if os.path.exists(dst):
            QMessageBox.warning(self, "Error", "Destination already exists.")
            return
        try:
            if op == "copy":
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                self.undo_stack.append(("delete", dst))
            elif op == "move":
                shutil.move(src, dst)
                self.undo_stack.append(("move", dst, src))
            self.redo_stack.clear()
            self.status.setText(f"{op.title()} completed")
            self.clipboard = None
            self.refresh_view()
        except Exception as e:
            self.show_error(str(e))

    def perform_rename(self):
        path = self.get_selected_path()
        new_name = self.rename_input.text().strip()
        if path and new_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            try:
                os.rename(path, new_path)
                self.undo_stack.append(("rename", new_path, path))
                self.redo_stack.clear()
                self.status.setText("Renamed successfully")
                self.refresh_view()
            except Exception as e:
                self.show_error(str(e))
        else:
            self.status.setText("Select file and enter new name")

    def perform_delete(self):
        path = self.get_selected_path()
        if path:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.undo_stack.append(("create", path))
                self.redo_stack.clear()
                self.status.setText("Deleted successfully")
                self.refresh_view()
            except Exception as e:
                self.show_error(str(e))

    def refresh_view(self):
        self.tree.setModel(None)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.status.setText("Refreshed")

    def get_available_name(self, base_name, extension=""):
        i = 1
        name = base_name + extension
        while os.path.exists(os.path.join(self.current_path, name)):
            name = f"{base_name} ({i}){extension}"
            i += 1
        return name

    def create_new_folder(self):
        dialog = InputNameDialog(
            "New Folder", "Enter folder name:", icon_type=QStyle.SP_DirIcon, parent=self
        )
        name, ok = dialog.get_input()
        if not ok:
            self.status.setText("Folder creation cancelled.")
            return
        folder_name = self.get_available_name(name if name else "Folder Baru")
        path = os.path.join(self.current_path, folder_name)
        try:
            os.mkdir(path)
            self.undo_stack.append(("delete", path))
            self.redo_stack.clear()
            self.status.setText(f"Folder created: {folder_name}")
            self.refresh_view()
        except Exception as e:
            self.show_error(str(e))

    def create_new_file(self):
        dialog = InputNameDialog(
            "New File",
            "Enter file name (with extension):",
            icon_type=QStyle.SP_FileIcon,
            parent=self,
        )
        name, ok = dialog.get_input()
        if not ok:
            self.status.setText("File creation cancelled.")
            return
        if name:
            base, ext = os.path.splitext(name)
            file_name = self.get_available_name(base, ext if ext else ".txt")
        else:
            file_name = self.get_available_name("File Baru", ".txt")
        path = os.path.join(self.current_path, file_name)
        try:
            with open(path, "w") as f:
                f.write("")
            self.undo_stack.append(("delete", path))
            self.redo_stack.clear()
            self.status.setText(f"File created: {file_name}")
            self.refresh_view()
        except Exception as e:
            self.show_error(str(e))

    def undo_action(self):
        if not self.undo_stack:
            self.status.setText("Nothing to undo.")
            return
        action = self.undo_stack.pop()
        self.redo_stack.append(action)
        kind = action[0]
        try:
            if kind == "delete":
                if os.path.isdir(action[1]):
                    shutil.rmtree(action[1])
                else:
                    os.remove(action[1])
            elif kind == "create":
                # Cannot fully restore deleted file without backup
                self.status.setText("Cannot restore deleted item.")
                return
            elif kind == "rename":
                os.rename(action[1], action[2])
            elif kind == "move":
                shutil.move(action[1], action[2])
            self.refresh_view()
            self.status.setText(f"Undo: {kind}")
        except Exception as e:
            self.show_error(str(e))

    def redo_action(self):
        if not self.redo_stack:
            self.status.setText("Nothing to redo.")
            return
        action = self.redo_stack.pop()
        self.undo_stack.append(action)
        kind = action[0]
        try:
            if kind == "delete":
                if os.path.isdir(action[1]):
                    shutil.rmtree(action[1])
                else:
                    os.remove(action[1])
            elif kind == "create":
                if os.path.isdir(action[1]):
                    os.mkdir(action[1])
                else:
                    open(action[1], "w").close()
            elif kind == "rename":
                os.rename(action[2], action[1])
            elif kind == "move":
                shutil.move(action[2], action[1])
            self.refresh_view()
            self.status.setText(f"Redo: {kind}")
        except Exception as e:
            self.show_error(str(e))

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec())
