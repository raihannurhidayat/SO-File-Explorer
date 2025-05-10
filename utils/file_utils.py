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

    return f"Copied: {os.path.basename(path)}"


def move_item(path):
    clipboard["action"] = "move"
    clipboard["path"] = path

    return f"Moved: {os.path.basename(path)}"


def paste_item(target_dir, parent=None, undo_redo=None):
    if not clipboard["path"] or not clipboard["action"]:
        return

    src = clipboard["path"]
    dst = os.path.join(target_dir, os.path.basename(src))

    status = ""

    try:
        if clipboard["action"] == "copy":
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

            status = f"Copied: {os.path.basename(src)}"

            if undo_redo:
                def undo():
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)

                    status = f"Undo copy: {os.path.basename(src)}"

                def redo():
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)

                    status = f"Redo copy: {os.path.basename(src)}"

                undo_redo.register_action(undo, redo)

        elif clipboard["action"] == "move":
            shutil.move(src, dst)

            status = f"Moved: {os.path.basename(src)}"

            if undo_redo:
                def undo():
                    shutil.move(dst, src)
                    status = f"Undo move: {os.path.basename(src)}"

                def redo():
                    shutil.move(src, dst)
                    status = f"Redo move: {os.path.basename(src)}"

                undo_redo.register_action(undo, redo)

        clipboard["action"] = None
        clipboard["path"] = None

        return status

    except Exception as e:
        show_error(str(e), parent)


def delete_item(path, parent=None):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

        return f"Deleted: {os.path.basename(path)}"

    except Exception as e:
        show_error(str(e), parent)


def rename_item(path, parent=None, undo_redo=None):
    base_dir = os.path.dirname(path)
    old_name = os.path.basename(path)
    new_name, ok = QInputDialog.getText(
        parent, "Rename", "Enter new name:", text=old_name)

    status = ""

    if ok and new_name:
        new_path = os.path.join(base_dir, new_name)

        try:
            os.rename(path, new_path)

            status = f"Renamed: {old_name} -> {new_name}"

            def undo():
                os.rename(new_path, path)
                status = f"Undo rename: {new_name} -> {old_name}"

            def redo():
                os.rename(path, new_path)
                status = f"Redo rename: {old_name} -> {new_name}"

            undo_redo.register_action(undo, redo)

            return status

        except Exception as e:
            show_error(str(e), parent)
