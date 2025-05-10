import os
import platform
import subprocess
from PySide6.QtWidgets import QMessageBox


def open_file(path, parent=None):
    try:
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.call(('open', path))
        else:
            subprocess.call(('xdg-open', path))
    except Exception as e:
        show_error(str(e), parent)


def show_error(message, parent=None):
    QMessageBox.critical(parent, "Error", message)
