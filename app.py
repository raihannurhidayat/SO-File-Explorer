import sys
import os
import shutil
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileSystemModel,
    QTreeView,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QLineEdit,
    QSplitter,
    QMessageBox,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern File Explorer - PySide6")
        self.setGeometry(200, 100, 1000, 600)

        self.current_path = os.getcwd()
        self.clipboard = None
        self.operation_mode = None

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Toolbar
        toolbar = QHBoxLayout()
        self.rename_input = QLineEdit()
        self.rename_input.setPlaceholderText("Enter new name here...")

        toolbar.addWidget(QPushButton("Back", clicked=self.go_back))
        toolbar.addWidget(
            QPushButton("Copy", clicked=lambda: self.set_clipboard("copy"))
        )
        toolbar.addWidget(
            QPushButton("Move", clicked=lambda: self.set_clipboard("move"))
        )
        toolbar.addWidget(QPushButton("Paste", clicked=self.perform_transfer))
        toolbar.addWidget(QPushButton("Rename", clicked=self.perform_rename))
        toolbar.addWidget(QPushButton("Delete", clicked=self.perform_delete))
        toolbar.addWidget(self.rename_input)

        # File Tree
        self.model = QFileSystemModel()
        self.model.setRootPath(self.current_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.tree.setColumnWidth(0, 300)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionBehavior(self.tree.SelectionBehavior.SelectRows)
        self.tree.doubleClicked.connect(self.navigate)

        # Status Bar
        self.status = QLabel("Ready")
        self.status.setStyleSheet("padding: 5px;")

        # Assemble
        main_layout.addLayout(toolbar)
        main_layout.addWidget(self.tree)
        main_layout.addWidget(self.status)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def selected_path(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return None
        return self.model.filePath(index)

    def go_back(self):
        self.current_path = os.path.dirname(self.current_path)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.status.setText(f"Current directory: {self.current_path}")

    def set_clipboard(self, mode):
        path = self.selected_path()
        if path:
            self.clipboard = (path, mode)
            self.status.setText(f"{mode.capitalize()} set: {path}")

    def perform_transfer(self):
        if not self.clipboard:
            return

        src, mode = self.clipboard
        dst = self.current_path
        name = os.path.basename(src)
        dst_path = os.path.join(dst, name)

        try:
            if mode == "copy":
                if os.path.isdir(src):
                    shutil.copytree(src, dst_path)
                else:
                    shutil.copy2(src, dst_path)
            elif mode == "move":
                shutil.move(src, dst_path)

            self.status.setText(f"{mode.capitalize()} completed")
            self.clipboard = None
            self.tree.setRootIndex(self.model.index(self.current_path))
        except Exception as e:
            self.show_error(str(e))

    def perform_rename(self):
        path = self.selected_path()
        new_name = self.rename_input.text().strip()

        if not path or not new_name:
            return

        new_path = os.path.join(os.path.dirname(path), new_name)
        try:
            os.rename(path, new_path)
            self.status.setText(f"Renamed to: {new_name}")
            self.rename_input.clear()
            self.tree.setRootIndex(self.model.index(self.current_path))
        except Exception as e:
            self.show_error(str(e))

    def perform_delete(self):
        path = self.selected_path()
        if not path:
            return

        confirm = QMessageBox.question(
            self,
            "Delete",
            f"Delete '{os.path.basename(path)}' permanently?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.status.setText("Deleted successfully")
                self.tree.setRootIndex(self.model.index(self.current_path))
            except Exception as e:
                self.show_error(str(e))

    def navigate(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.current_path = path
            self.tree.setRootIndex(self.model.index(path))
            self.status.setText(f"Opened: {path}")
        else:
            os.startfile(path)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.status.setText("Operation failed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec())
