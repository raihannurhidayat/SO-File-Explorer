import os
from PySide6.QtWidgets import QMessageBox


def get_available_name(parent_path, base_name, extension=""):
    i = 1
    name = base_name + extension
    path = os.path.join(parent_path, name)

    while os.path.exists(path):
        name = f"{base_name} ({i}){extension}"
        path = os.path.join(parent_path, name)
        i += 1

    return name


def show_error(message, parent=None):
    QMessageBox.critical(parent, "Error", message)
