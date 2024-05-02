from PyQt6.QtCore import QObject, pyqtSignal
import random
import string
import os
import platform
from .worker import Worker
from .file_options import FileOptions, image_extensions, video_extensions


class FileCopy(QObject):
    progress_changed = pyqtSignal(int)
    not_files_found = pyqtSignal()
    copy_finished = pyqtSignal()
    copy_canceled = pyqtSignal()
    show_message = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.copy_finished.connect(self.copy_finished_func)
        self.worker = None

    def start_copy(self, source, file_options: FileOptions):
        self.file_options = file_options
        self.source = source

        if self.is_copying_files():
            return

        absolute_path_files = self.__find_files_to_copy()

        if not absolute_path_files:
            self.not_files_found.emit()
            return

        to_folder_path = self.__create_folder(self.source)

        if to_folder_path is None:
            return

        self.to_folder_path = to_folder_path

        self.show_message.emit(
            {
                "type_message": "Info",
                "message": f"All content will be copied to the folder: {to_folder_path}",
            }
        )

        self.worker = Worker(absolute_path_files, to_folder_path)
        self.worker.progress_changed.connect(self.progress_changed)
        self.worker.finished.connect(self.copy_finished)
        self.worker.copy_canceled.connect(self.copy_canceled)
        self.worker.start()

    def cancel_copy(self):
        if self.is_copying_files():
            self.worker.cancel_copy()

    def copy_finished_func(self):
        self.worker = None
        self.__open_folder(self.to_folder_path)

    def __open_folder(self, folder_path):
        operating_system = platform.system()
        if operating_system == "Windows":
            os.startfile(folder_path)
        elif operating_system == "Linux":
            os.system('xdg-open "{}"'.format(folder_path))
        else:
            print("Unsupported operating system.")

    def __create_folder(self, source_folder_path: str):
        folder_name = "folder_" + self.__generate_unique_name()
        folder_path = os.path.join(source_folder_path, "..", folder_name)
        try:
            os.makedirs(folder_path)
            normalized_path = os.path.normpath(folder_path)
            return normalized_path
        except OSError as e:
            self.show_message.emit(
                {"type_message": "error", "message": f"Could not create folder: {e}"}
            )
            return None

    def __generate_unique_name(self, length=5):
        characters = string.ascii_letters + string.digits
        unique_name = "".join(random.choice(characters) for _ in range(length))
        return unique_name

    def is_copying_files(self):
        return self.worker is not None

    def __find_files_to_copy(self) -> list:
        """
        finds and returns a list of absolute file paths in the source directory that should be copied.

        Returns:
            list: A list of absolute file paths that should be copied.
        """
        files_to_copy = []
        for root, _, files in os.walk(self.source):
            for file in files:
                if self.__should_handle_file(file):
                    abs_path = os.path.join(root, file)
                    files_to_copy.append(abs_path)
        return files_to_copy

    def __should_handle_file(self, filename: str):
        file_extensions: tuple
        match self.file_options:
            case FileOptions.IMAGES:
                file_extensions = image_extensions
            case FileOptions.VIDEOS:
                file_extensions = video_extensions
            case FileOptions.IMAGES_VIDEOS:
                file_extensions = image_extensions + video_extensions
        return filename.lower().endswith(file_extensions)
