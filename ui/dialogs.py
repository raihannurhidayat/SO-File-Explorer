from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt


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
