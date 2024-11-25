from PyQt6.QtCore import QThread, pyqtSignal
import os
import shutil
import zipfile


class Worker(QThread):
    finished = pyqtSignal()
    progress_changed = pyqtSignal(int)
    not_files_found = pyqtSignal()
    copy_canceled = pyqtSignal()

    def __init__(self, absolute_path_files: list, to: str, compress_after_copy: bool):
        super().__init__()
        self.to = to
        self.cancel = False
        self.absolute_path_files = absolute_path_files
        self.compress_after_copy = compress_after_copy

    def run(self):
        progress = 0
        self.progress_changed.emit(progress)
        total = len(self.absolute_path_files)

        if self.compress_after_copy:
            # Crear un archivo ZIP para comprimir los archivos
            zip_filename = os.path.join(self.to, "compressed_files.zip")
            with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file in self.absolute_path_files:
                    if self.cancel:
                        self.copy_canceled.emit()
                        return

                    filename = os.path.basename(file)
                    zipf.write(file, filename)  # Comprimir el archivo en el archivo ZIP
                    progress += 1
                    self.progress_changed.emit(int(progress / total * 100))
        else:
            for file in self.absolute_path_files:
                if self.cancel:
                    self.copy_canceled.emit()
                    return

                filename = os.path.basename(file)
                dest_path = os.path.join(self.to, filename)
                if os.path.exists(dest_path):
                    dest_path = self.__get_unique_filename(dest_path)

                shutil.copyfile(file, dest_path)
                progress += 1
                self.progress_changed.emit(int(progress / total * 100))

        if not self.cancel:
            self.finished.emit()

    def __get_unique_filename(self, filename):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(f"{name}_{counter}{ext}"):
            counter += 1
        return f"{name}_{counter}{ext}"

    def cancel_copy(self):
        self.cancel = True
