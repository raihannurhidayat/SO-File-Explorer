class FileManager(QMainWindow):
    #! NAVIGATION TOOLBAR
    navbar = QToolBar()
    navbar.setFloatable(False)
    navbar.setMovable(False)
    self.addToolBar(Qt.TopToolBarArea, navbar)
    self.addToolBarBreak(Qt.TopToolBarArea)

    # NAVIGATION ACTIONS
    self.back_action = QWidgetAction(self)
    self.back_action.setIconText("Back")
    self.back_action.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
    self.back_action.triggered.connect(self.go_back)
    self.back_action.setEnabled(False)
    navbar.addAction(self.back_action)

    self.forward_action = QWidgetAction(self)
    self.forward_action.setIconText("Forward")
    self.forward_action.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
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
    refresh_action.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
    refresh_action.triggered.connect(self.refresh)
    navbar.addAction(refresh_action)

    self.path_input = QLineEdit(self.current_path)
    self.path_input.returnPressed.connect(self.enter_path)
    navbar.addWidget(self.path_input)

    # RIBBON TOOLBAR
    ribbon = QToolBar("File Actions")
    ribbon.setFloatable(False)
    ribbon.setMovable(False)
    self.addToolBar(Qt.TopToolBarArea, ribbon)

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
    copy_btn.setIconText("📚 Copy")
    copy_btn.triggered.connect(self.copy_selected)

    move_btn = ribbon.addAction("Cut")
    move_btn.setIconText("✂️ Cut")
    move_btn.triggered.connect(self.move_selected)

    paste_btn = ribbon.addAction("Paste")
    paste_btn.setIconText("📋 Paste")
    paste_btn.triggered.connect(self.paste_selected)
    delete_btn = ribbon.addAction("Delete")
    delete_btn.setIconText("🗑️ Delete")
    delete_btn.triggered.connect(self.delete_selected)

    rename_btn = ribbon.addAction("Rename")
    rename_btn.setIconText("📝 Rename")
    rename_btn.triggered.connect(self.rename_selected)

    undo_btn = ribbon.addAction("Undo")
    undo_btn.setIconText("↻ Undo")
    undo_btn.triggered.connect(self.undo_action)

    redo_btn = ribbon.addAction("Redo")
    redo_btn.setIconText("↺ Redo")
    redo_btn.triggered.connect(self.redo_action)

    # FILE & FOLDER ACTIONS
    def get_selected_path(self):
        """Get selected path from the content view (primary) or sidebar (fallback)"""
        selected_indexes = self.content_view.selectedIndexes()
        if (
            selected_indexes
            and selected_indexes[0].isValid()
            and selected_indexes[0].column() == 0
        ):
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
        context_menu.addAction("New Folder", lambda: self.create_new_folder())
        context_menu.addAction("New File", lambda: self.create_new_file())

        context_menu.exec(self.content_view.viewport().mapToGlobal(position))
