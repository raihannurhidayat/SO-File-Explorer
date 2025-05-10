from PySide6.QtWidgets import QMessageBox


def show_error(message, parent=None):
    QMessageBox.critical(parent, "Error", message)
