import os
import shutil


def create_folder(path):
    try:
        os.mkdir(path)
        return True, None
    except Exception as e:
        return False, str(e)


def create_file(path):
    try:
        with open(path, "w") as f:
            f.write("")
        return True, None
    except Exception as e:
        return False, str(e)


def delete_path(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True, None
    except Exception as e:
        return False, str(e)


def rename_path(src, dst):
    try:
        os.rename(src, dst)
        return True, None
    except Exception as e:
        return False, str(e)


def copy_path(src, dst):
    try:
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return True, None
    except Exception as e:
        return False, str(e)


def move_path(src, dst):
    try:
        shutil.move(src, dst)
        return True, None
    except Exception as e:
        return False, str(e)
