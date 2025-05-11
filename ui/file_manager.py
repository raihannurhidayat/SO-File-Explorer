import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileSystemModel, QTreeView, QLabel,
    QAbstractItemView, QLineEdit, QToolBar, QWidgetAction, QStyle, QSplitter, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QDir
from ui.sidebar import Sidebar

from utils.history import HistoryManager
from utils.navigation_utils import is_valid_directory, go_up
from utils.undo import UndoRedoManager
from utils.file_utils import (open_file, show_error, copy_item,
                              move_item, delete_item, paste_item, rename_item,
                              create_new_file, create_new_folder)


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python File Explorer")
        self.setGeometry(100, 100, 1100, 600)

        self.current_path = os.getcwd()

        self.history = HistoryManager()
        self.undo_redo = UndoRedoManager()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # Remove margins for a cleaner look
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create horizontal splitter for sidebar and content area
        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(splitter, 1)

        # Left side - tree view navigation that shows the entire drive hierarchy
        self.sidebar = Sidebar(self.current_path, parent=self)
        self.sidebar.path_selected.connect(self.navigate_to_path)
        self.sidebar.tree.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        splitter.addWidget(self.sidebar.tree)

        # Right side - content view
        content_widget = QWidget()
        content_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        content_layout.setSpacing(0)
        splitter.addWidget(content_widget)

        # File view for the current directory
        self.content_model = QFileSystemModel()
        self.content_model.setRootPath(self.current_path)

        self.content_view = QTreeView()
        self.content_view.setModel(self.content_model)
        self.content_view.setRootIndex(
            self.content_model.index(self.current_path))
        self.content_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.content_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.content_view.doubleClicked.connect(self.content_item_activated)
        self.content_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.content_view.customContextMenuRequested.connect(
            self.show_content_context_menu)

        # Adjust column widths for content view
        self.content_view.header().setSectionResizeMode(
            0, QHeaderView.Stretch)  # Name column stretches
        self.content_view.header().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)  # Size column
        self.content_view.header().setSectionResizeMode(
            2, QHeaderView.ResizeToContents)  # Type column
        self.content_view.header().setSectionResizeMode(
            3, QHeaderView.ResizeToContents)  # Date column

        content_layout.addWidget(self.content_view)

        # Status bar for messages
        self.status = QLabel("Ready")
        # self.status.setFrameStyle(QLabel.Sunken | QLabel.Panel)
        self.status.setMargin(3)
        self.status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setContentsMargins(5, 5, 5, 5)
        self.status.setFixedHeight(28)
        main_layout.addWidget(self.status, 0)

        # Set the starting splitter position
        splitter.setSizes([250, 950])  # Left gets 250px, right gets 950px

        # NAVIGATION TOOLBAR
        navbar = QToolBar()
        navbar.setFloatable(False)
        navbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, navbar)
        self.addToolBarBreak(Qt.TopToolBarArea)

        # RIBBON TOOLBAR
        ribbon = QToolBar("File Actions")
        ribbon.setFloatable(False)
        ribbon.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, ribbon)

        # NAVIGATION ACTIONS
        self.back_action = QWidgetAction(self)
        self.back_action.setIconText("Back")
        self.back_action.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowBack))
        self.back_action.triggered.connect(self.go_back)
        self.back_action.setEnabled(False)
        navbar.addAction(self.back_action)

        self.forward_action = QWidgetAction(self)
        self.forward_action.setIconText("Forward")
        self.forward_action.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowForward)
        )
        self.forward_action.triggered.connect(self.go_forward)
        self.forward_action.setEnabled(False)
        navbar.addAction(self.forward_action)

        up_action = QWidgetAction(self)
        up_action.setIconText("Up")
        up_action.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        up_action.triggered.connect(self.go_up)
        navbar.addAction(up_action)

        refresh_action = QWidgetAction(self)
        refresh_action.setIconText("Refresh")
        refresh_action.setIcon(
            self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_action.triggered.connect(self.refresh)
        navbar.addAction(refresh_action)

        self.path_input = QLineEdit(self.current_path)
        self.path_input.returnPressed.connect(self.enter_path)
        navbar.addWidget(self.path_input)

        # RIBBON ACTIONS
        new_folder_action = QWidgetAction(self)
        new_folder_action.setIconText("📁 New Folder")
        new_folder_action.triggered.connect(self.create_new_folder)
        ribbon.addAction(new_folder_action)

        new_file_action = QWidgetAction(self)
        new_file_action.setIconText("📄 New File")
        new_file_action.triggered.connect(self.create_new_file)
        ribbon.addAction(new_file_action)

        copy_btn = ribbon.addAction("Copy")
        copy_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        copy_btn.triggered.connect(self.copy_selected)

        move_btn = ribbon.addAction("Cut")
        move_btn.setIcon(self.style().standardIcon(
            QStyle.SP_DialogCloseButton))
        move_btn.triggered.connect(self.move_selected)

        paste_btn = ribbon.addAction("Paste")
        paste_btn.setIcon(self.style().standardIcon(
            QStyle.SP_FileIcon))
        paste_btn.triggered.connect(self.paste_selected)

        delete_btn = ribbon.addAction("Delete")
        delete_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_btn.triggered.connect(self.delete_selected)

        rename_btn = ribbon.addAction("Rename")
        rename_btn.setIcon(self.style().standardIcon(
            QStyle.SP_FileDialogContentsView))
        rename_btn.triggered.connect(self.rename_selected)

        undo_btn = ribbon.addAction("Undo")
        undo_btn.setIcon(self.style().standardIcon(
            QStyle.SP_ArrowLeft))
        undo_btn.triggered.connect(self.undo_action)

        redo_btn = ribbon.addAction("Redo")
        redo_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        redo_btn.triggered.connect(self.redo_action)

    def navigate_to_path(self, path):
        """Navigate when a path is selected from the sidebar"""
        if os.path.isdir(path):
            self.history.push_back(self.current_path)
            self.update_buttons()
            self.set_path(path)
        else:
            open_file(path, self)

    def content_item_activated(self, index):
        """Handle double-click on content view items"""
        path = self.content_model.filePath(index)
        if os.path.isdir(path):
            self.history.push_back(self.current_path)
            self.update_buttons()
            self.set_path(path)
        else:
            open_file(path, self)

    def set_path(self, path):
        """Set the current path and update both views"""
        if os.path.exists(path):
            self.current_path = path

            # Update sidebar selection (this won't change the root, just highlight the folder)
            self.sidebar.set_root_path(path)

            # Update content view
            self.content_view.setRootIndex(self.content_model.index(path))

            # Update path display
            self.path_input.setText(path)
            self.status.setText(f"Opened: {path}")
        else:
            show_error(f"Path does not exist: {path}", self)

    def enter_path(self):
        new_path = self.path_input.text()
        if os.path.isdir(new_path):
            self.history.push_back(self.current_path)
            self.update_buttons()
            self.set_path(new_path)
        else:
            show_error(f"Invalid path: {new_path}", self)

    def go_back(self):
        if self.history.can_go_back():
            self.set_path(self.history.go_back(self.current_path))
            self.update_buttons()

    def go_forward(self):
        if self.history.can_go_forward():
            self.set_path(self.history.go_forward(self.current_path))
            self.update_buttons()

    def go_up(self):
        parent = go_up(self.current_path)
        if parent != self.current_path:
            self.history.push_back(self.current_path)
            self.set_path(parent)
            self.update_buttons()

    def refresh(self):
        # Force QFileSystemModel to refresh
        self.content_model.setRootPath("")
        self.content_model.setRootPath(self.current_path)
        self.set_path(self.current_path)

    def update_buttons(self):
        self.back_action.setEnabled(len(self.history.back_stack) > 0)
        self.forward_action.setEnabled(len(self.history.forward_stack) > 0)

    # FILE & FOLDER ACTIONS
    def get_selected_path(self):
        """Get selected path from the content view (primary) or sidebar (fallback)"""
        selected_indexes = self.content_view.selectedIndexes()
        if selected_indexes and selected_indexes[0].isValid() and selected_indexes[0].column() == 0:
            return self.content_model.filePath(selected_indexes[0])
        else:
            return self.sidebar.get_selected_path()

    def copy_selected(self):
        path = self.get_selected_path()
        if path:
            output = copy_item(path)
            self.status.setText(output)

    def move_selected(self):
        path = self.get_selected_path()
        if path:
            output = move_item(path)
            self.status.setText(output)

    def paste_selected(self):
        output = paste_item(self.current_path, self, self.undo_redo)
        self.refresh()
        self.status.setText(output)

    def delete_selected(self):
        path = self.get_selected_path()
        if path:
            output = delete_item(path, self)
            self.refresh()
            self.status.setText(output)

    def rename_selected(self):
        path = self.get_selected_path()
        if path:
            output = rename_item(path, self, self.undo_redo)
            self.refresh()
            self.status.setText(output)

    def create_new_folder(self):
        target = self.get_selected_path() or self.current_path
        if os.path.isfile(target):
            target = os.path.dirname(target)
        try:
            create_new_folder(target)
            self.refresh()
        except Exception as e:
            show_error(str(e), self)

    def create_new_file(self):
        target = self.get_selected_path() or self.current_path
        if os.path.isfile(target):
            target = os.path.dirname(target)
        try:
            create_new_file(target)
            self.refresh()
        except Exception as e:
            show_error(str(e), self)

    def undo_action(self):
        self.undo_redo.undo()
        self.refresh()

    def redo_action(self):
        self.undo_redo.redo()
        self.refresh()

    # CONTEXT MENU
    def show_context_menu(self, position):
        """Sidebar context menu (kept for backward compatibility)"""
        index = self.sidebar.tree.indexAt(position)
        if not index.isValid():
            return

        from PySide6.QtWidgets import QMenu

        context_menu = QMenu()
        context_menu.addAction("Copy", self.copy_selected)
        context_menu.addAction("Cut", self.move_selected)
        context_menu.addAction("Paste", self.paste_selected)
        context_menu.addAction("Delete", self.delete_selected)
        context_menu.addAction("Rename", self.rename_selected)
        context_menu.exec(self.sidebar.tree.viewport().mapToGlobal(position))

    def show_content_context_menu(self, position):
        """Context menu for content view items"""
        index = self.content_view.indexAt(position)

        from PySide6.QtWidgets import QMenu
        context_menu = QMenu()

        if index.isValid():
            # Actions for when clicking on an item
            context_menu.addAction("Copy", self.copy_selected)
            context_menu.addAction("Cut", self.move_selected)
            context_menu.addAction("Delete", self.delete_selected)
            context_menu.addAction("Rename", self.rename_selected)
            context_menu.addSeparator()

        # These actions are always available
        context_menu.addAction("Paste", self.paste_selected)
        context_menu.addAction("Refresh", self.refresh)
        context_menu.addSeparator()

        # Actions for when clicking on an empty space
        context_menu.addAction(
            "New Folder", lambda: self.create_new_folder())
        context_menu.addAction(
            "New File", lambda: self.create_new_file())

        context_menu.exec(self.content_view.viewport().mapToGlobal(position))
