from .main_window import MainWindow
from .file_copy import FileCopy, CopyOptions


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
        source_folder_path = self.view.get_source_folder_path()
        file_type = self.view.get_filetype()
        compress_after_copy = self.view.compressCheckBox.isChecked()

        if not source_folder_path:
            return

        copy_options = CopyOptions(source_folder_path, file_type, compress_after_copy)
        self.view.show_progressBar()
        self.view.selectButtonSetEnabled(False)
        self.file_model.start_copy(copy_options)

    def cancel_copy(self):
        if not self.file_model.is_copying_files():
            return
        response = self.view.show_alert()
        if response:
            self.file_model.cancel_copy()

    def show_message_view(self, dict):
        type_message = dict["type_message"]
        message = dict["message"]
        self.view.show_message(type_message, message)
