import os
from .main_window import MainWindow
from .file_copy import FileCopy


class MainController:

    def __init__(self, view: MainWindow, file_model: FileCopy):
        self.view = view
        self.file_model = file_model
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

            if not source_folder_path:
                return

            self.view.show_progressBar()
            self.view.selectButtonSetEnabled(False)
            to_folder_path = self.file_model.start_copy(source_folder_path, file_option)
            if to_folder_path is not None:
                normalized_path = os.path.normpath(to_folder_path)
                self.view.show_message(
                    "Info",
                    f"All content will be copied to the folder: {normalized_path}",
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
