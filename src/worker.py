from PyQt6.QtCore import QThread, pyqtSignal
import shutil
import os
from .file_options import FileOptions, image_extensions, video_extensions


class Worker(QThread):
    finished = pyqtSignal()
    progress_changed = pyqtSignal(int)
    not_files_found = pyqtSignal()
    copy_canceled = pyqtSignal()

    def __init__(self, source: str, to: str, file_option: FileOptions):
        super().__init__()
        self.source = source
        self.to = to
        self.cancel = False
        self.file_options = file_option

    def run(self):
        progress = 0
        self.progress_changed.emit(progress)
        total = self.count_images()
        print("Total Files Founded: " + str(total))

        if total == 0:
            self.not_files_found.emit()
            return

        for root, dirs, files in os.walk(self.source):
            for file in files:
                if self.cancel:
                    self.copy_canceled.emit()
                    return
                if self._should_handle_file(file):
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(self.to, file)
                    if os.path.exists(dest_path):
                        dest_path = self._get_unique_filename(dest_path)
                    shutil.copyfile(src_path, dest_path)
                    progress += 1
                    self.progress_changed.emit(int(progress / total * 100))
        if not self.cancel:
            self.finished.emit()

    def _should_handle_file(self, filename: str):
        file_extensions: tuple
        match self.file_options:
            case FileOptions.IMAGES:
                file_extensions = image_extensions
            case FileOptions.VIDEOS:
                file_extensions = video_extensions
            case FileOptions.IMAGES_VIDEOS:
                file_extensions = image_extensions + video_extensions
        return filename.lower().endswith(file_extensions)

    def _get_unique_filename(self, filename):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(f"{name}_{counter}{ext}"):
            counter += 1
        return f"{name}_{counter}{ext}"

    def count_images(self):
        count = 0
        for root, _, files in os.walk(self.source):
            for file in files:
                if self._should_handle_file(file):
                    count += 1
        return count

    def cancelCopy(self):
        self.cancel = True
