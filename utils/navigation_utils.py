import os
from utils.utils import show_error


def go_up(current_path):
    parent = os.path.dirname(current_path)
    if parent and parent != current_path:
        return parent
    return current_path


def is_valid_directory(path):
    return os.path.isdir(path)