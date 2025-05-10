import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileSystemModel,
    QTreeView,
    QLabel,
    QAbstractItemView,
)


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python File Explorer")
        self.setGeometry(100, 100, 900, 600)

        self.current_path = os.getcwd()  # Awal relatif ke working directory

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        self.status = QLabel("Ready")
        self.model = QFileSystemModel()
        self.model.setRootPath(self.current_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.tree.doubleClicked.connect(self.navigate)
        self.tree.setColumnWidth(0, 300)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)

        main_layout.addWidget(self.tree)
        main_layout.addWidget(self.status)
        central_widget.setLayout(main_layout)

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


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec())
