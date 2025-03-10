from PyQt6.QtCore import QObject, pyqtSignal
import random
import string
import os
import platform
from .copy_thread import CopyThread
from .file_options import FileType, CopyOptions, image_extensions, video_extensions


class FileCopy(QObject):
    progress_changed = pyqtSignal(int)
    not_files_found = pyqtSignal()
    copy_finished = pyqtSignal()
    copy_canceled = pyqtSignal()
    show_message = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.copy_finished.connect(self._copy_finished_func)
        self.copy_thread = None

    def start_copy(self, copy_options: CopyOptions):
        self.file_type = copy_options.file_type
        self.source = copy_options.source
        self.compress_after_copy = copy_options.compress_after_copy
        self.custom_file_types = copy_options.custom_file_types

        if self.is_copying_files():
            return

        to_folder_path = self._create_folder(self.source)

        if to_folder_path is None:
            return

        self.to_folder_path = to_folder_path
        absolute_path_files = self._find_files_to_copy(self.source, to_folder_path)

        if not absolute_path_files:
            # the folder that was created is deleted
            os.rmdir(to_folder_path)
            self.not_files_found.emit()
            return

        self._start_thread_copy(to_folder_path, absolute_path_files)

    def cancel_copy(self):
        if self.is_copying_files():
            self.copy_thread.cancel_copy()

    def is_copying_files(self):
        return self.copy_thread is not None

    def _copy_finished_func(self):
        self.copy_thread = None
        self._open_folder(self.to_folder_path)

    def _start_thread_copy(self, to_folder_path, absolute_path_files):
        self.show_message.emit(
            {
                "type_message": "Info",
                "message": f"All content will be copied to the folder: {to_folder_path}",
            }
        )
        self.copy_thread = CopyThread(
            absolute_path_files, to_folder_path, self.compress_after_copy
        )
        self.copy_thread.progress_changed.connect(self.progress_changed)
        self.copy_thread.finished.connect(self.copy_finished)
        self.copy_thread.copy_canceled.connect(self._cancel_copy_emit)
        self.copy_thread.start()

    def _cancel_copy_emit(self):
        self.copy_thread.quit()
        self.copy_thread.wait()
        self.copy_thread = None
        self.copy_canceled.emit()

    def _open_folder(self, folder_path):
        operating_system = platform.system()
        if operating_system == "Windows":
            os.startfile(folder_path)
        elif operating_system == "Linux":
            os.system('xdg-open "{}"'.format(folder_path))
        else:
            print("Unsupported operating system.")

    def _create_folder(self, source_folder_path: str):
        folder_name = "folder_" + self._generate_unique_name()
        folder_path = os.path.join(source_folder_path, folder_name)
        os.makedirs(folder_path)
        return folder_path

    def _generate_unique_name(self, length=5):
        characters = string.ascii_letters + string.digits
        unique_name = "".join(random.choice(characters) for _ in range(length))
        return unique_name

    def _find_files_to_copy(self, source_folder_path: str, to_folder_path: str) -> list:
        """
        finds and returns a list of absolute file paths in the source directory that should be copied.

        Returns:
            list: A list of absolute file paths that should be copied.
        """
        files_to_copy = []
        for root, _, files in os.walk(source_folder_path):
            if root == to_folder_path:
                # avoid the folder that was created
                continue
            for file in files:
                if self._should_handle_file(file):
                    abs_path = os.path.join(root, file)
                    files_to_copy.append(abs_path)
        return files_to_copy

    def _should_handle_file(self, filename: str):
        file_extensions: tuple
        match self.file_type:
            case FileType.IMAGES:
                file_extensions = image_extensions
            case FileType.VIDEOS:
                file_extensions = video_extensions
            case FileType.IMAGES_VIDEOS:
                file_extensions = image_extensions + video_extensions
            case FileType.CUSTOM:
                file_extensions = self.custom_file_types
        return any(filename.lower().endswith(ext) for ext in file_extensions)
