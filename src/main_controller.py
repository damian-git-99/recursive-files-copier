import os
from .main_window import MainWindow
from .file_copy import FileCopy


class MainController:

    def __init__(self, view: MainWindow):
        self.view = view
        self.file_model = FileCopy()
        self.view.selectFolderButton.clicked.connect(self.start_copy)
        self.view.cancelPushButton.clicked.connect(self.cancel_copy)
        self.file_model.progress_changed.connect(self.view.update_progressBar_progress)
        self.file_model.not_files_found.connect(self.view.not_files)
        self.file_model.copy_finished.connect(self.view.copy_finished)
        self.file_model.copy_canceled.connect(self.view.copy_canceled)

    def start_copy(self):
        try:
            source_folder_path = self.view.get_source_folder_path()
            file_option = self.view.get_filetype()
            if source_folder_path:
                to_folder_path = self.file_model.create_folder(source_folder_path)
                normalized_path = os.path.normpath(to_folder_path)
                self.view.show_message(
                    "Info",
                    f"All content will be copied to the folder: {normalized_path}",
                )
                self.view.show_progressBar()
                self.view.selectButtonSetEnabled(False)
                self.file_model.start_copy(
                    source_folder_path, to_folder_path, file_option
                )
        except Exception as e:
            self.view.show_message("Error", f"Error: {e}")
            print(f"Error: {e}")

    def cancel_copy(self):
        if not self.file_model.is_copying_files():
            return
        response = self.view.show_alert()
        if response:
            self.file_model.cancel_copy()
