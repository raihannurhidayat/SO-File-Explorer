from PySide6.QtCore import QSortFilterProxyModel, Qt, QDir
from PySide6.QtWidgets import QFileSystemModel


class FileSortProxyModel(QSortFilterProxyModel):
    def lessThan(self, left_index, right_index):
        source_model = self.sourceModel()
        left_info = source_model.fileInfo(left_index)
        right_info = source_model.fileInfo(right_index)

        # Urutkan folder pertama
        if left_info.isDir() != right_info.isDir():
            return left_info.isDir()

        # Sorting berdasarkan kolom
        if self.sortColumn() == 0:  # Nama
            return left_info.fileName().lower() < right_info.fileName().lower()
        elif self.sortColumn() == 3:  # Tanggal modifikasi
            return left_info.lastModified() < right_info.lastModified()

        return super().lessThan(left_index, right_index)
