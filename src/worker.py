from PyQt6.QtCore import QThread, pyqtSignal
import os
import shutil


class Worker(QThread):
    finished = pyqtSignal()
    progress_changed = pyqtSignal(int)
    not_files_found = pyqtSignal()
    copy_canceled = pyqtSignal()

    def __init__(self, files: list, to: str):
        super().__init__()
        self.to = to
        self.cancel = False
        self.files = files

    def run(self):
        progress = 0
        self.progress_changed.emit(progress)
        total = len(self.files)

        for file in self.files:
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
