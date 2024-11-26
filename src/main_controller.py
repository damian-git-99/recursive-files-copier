from .main_window import MainWindow
from .file_copy import FileCopy, CopyOptions, FileType
import re


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
        self.file_model.show_message.connect(self.show_message_view)

    def start_copy(self):
        try:
            source_folder_path = self.view.get_source_folder_path()
            file_type = self.view.get_filetype()
            custom_file_types = self.view.get_custom_file_types()
            compress_after_copy = self.view.compressCheckBox.isChecked()
            pattern = r"^(\.[a-zA-Z0-9]+)(\s(\.[a-zA-Z0-9]+))*$"

            if (
                file_type == FileType.CUSTOM
                and not custom_file_types
                or not re.match(pattern, custom_file_types)
            ):
                self.view.show_message(
                    "Alert",
                    "Please enter the file extensions to copy (separated by spaces)",
                )
                return

            if not source_folder_path:
                return

            copy_options = CopyOptions(
                source_folder_path,
                file_type,
                compress_after_copy,
                self.convert_file_type_to_list(custom_file_types),
            )
            self.view.show_progressBar()
            self.view.selectButtonSetEnabled(False)
            self.file_model.start_copy(copy_options)
        except Exception as e:
            self.view.show_message("Error", str(e))

    def cancel_copy(self):
        try:
            if not self.file_model.is_copying_files():
                return
            response = self.view.show_alert()
            if response:
                self.file_model.cancel_copy()
        except Exception as e:
            self.view.show_message("Error", str(e))

    def show_message_view(self, dict):
        type_message = dict["type_message"]
        message = dict["message"]
        self.view.show_message(type_message, message)

    def convert_file_type_to_list(self, text: str):
        return text.split(" ")
