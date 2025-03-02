from PyQt6.QtCore import QThread, pyqtSignal
import os
import shutil
import zipfile


class CopyThread(QThread):
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
        
        if self.compress_after_copy:
            self._compress_files()
        else:
            self._copy_files()

        if not self.cancel:
            self.finished.emit()

    def _compress_files(self):
        existing_files_in_zip = []
        total = len(self.absolute_path_files)
        progress = 0
        
        zip_filename = os.path.join(self.to, "compressed_files.zip")
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in self.absolute_path_files:
                if self.cancel:
                    self.copy_canceled.emit()
                    return

                filename = os.path.basename(file)
                unique_filename = self.__get_unique_filename_zip(existing_files_in_zip, filename)

                zipf.write(file, unique_filename)
                existing_files_in_zip.append(unique_filename)
                progress += 1
                self.progress_changed.emit(int(progress / total * 100))

    def _copy_files(self):
        total = len(self.absolute_path_files)
        progress = 0

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

    def __get_unique_filename(self, filename):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(f"{name}_{counter}{ext}"):
            counter += 1
        return f"{name}_{counter}{ext}"

    def __get_unique_filename_zip(self, existing_files, original_name):
        name, ext = os.path.splitext(original_name)
        counter = 1

        while f"{name}{ext}" in existing_files:
            name = f"{name}_{counter}"
            counter += 1

        return f"{name}{ext}"

    def cancel_copy(self):
        self.cancel = True
