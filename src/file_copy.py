from PyQt6.QtCore import QObject, pyqtSignal
import random
import string
import os
from .worker import Worker
from .file_options import FileOptions


class FileCopy(QObject):
    progress_changed = pyqtSignal(int)
    not_files_found = pyqtSignal()
    copy_finished = pyqtSignal()
    copy_canceled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.copy_finished.connect(self.copy_finished_func)
        self.worker = None

    def start_copy(self, source_folder_path, to_folder_path, file_option: FileOptions):
        if self.is_copying_files():
            return
        self.worker = Worker(source_folder_path, to_folder_path, file_option)
        self.worker.progress_changed.connect(self.progress_changed)
        self.worker.not_files_found.connect(self.not_files_found)
        self.worker.finished.connect(self.copy_finished)
        self.worker.copy_canceled.connect(self.copy_canceled)
        self.worker.start()

    def cancel_copy(self):
        if self.is_copying_files():
            self.worker.cancelCopy()

    def copy_finished_func(self):
        self.worker = None

    def create_folder(self, source_folder_path: str):
        folder_name = "folder_" + self.generate_unique_name()
        folder_path = os.path.join(source_folder_path, "..", folder_name)
        os.makedirs(folder_path)
        return folder_path

    def generate_unique_name(self, length=5):
        characters = string.ascii_letters + string.digits
        unique_name = "".join(random.choice(characters) for _ in range(length))
        return unique_name

    def is_copying_files(self):
        """
        checks if a worker is currently copying files.
        """
        if self.worker is not None:
            return True
        else:
            return False
