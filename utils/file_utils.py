import os
import shutil
import platform
import subprocess
from PySide6.QtWidgets import QInputDialog
from utils.utils import show_error

clipboard = {"action": None, "path": None}


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


def copy_item(path):
    clipboard["action"] = "copy"
    clipboard["path"] = path


def move_item(path):
    clipboard["action"] = "move"
    clipboard["path"] = path


def paste_item(target_dir, parent=None):
    if not clipboard["path"] or not clipboard["action"]:
        return
    try:
        src = clipboard["path"]
        dst = os.path.join(target_dir, os.path.basename(src))
        if clipboard["action"] == "copy":
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        elif clipboard["action"] == "move":
            shutil.move(src, dst)
        clipboard["action"] = None
        clipboard["path"] = None
    except Exception as e:
        show_error(str(e), parent)


def delete_item(path, parent=None):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except Exception as e:
        show_error(str(e), parent)


def rename_item(path, parent=None):
    base_dir = os.path.dirname(path)
    old_name = os.path.basename(path)
    new_name, ok = QInputDialog.getText(
        parent, "Rename", "Enter new name:", text=old_name)
    if ok and new_name:
        new_path = os.path.join(base_dir, new_name)
        try:
            os.rename(path, new_path)
        except Exception as e:
            show_error(str(e), parent)
