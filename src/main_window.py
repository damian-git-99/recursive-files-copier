from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt6 import uic
import os
import sys
from .file_options import FileType


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # base_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        filename = "src/main.ui"
        absolute_path = os.path.join(base_dir, filename)
        uic.loadUi(absolute_path, self)
        self.progressBar.hide()
        self.customLineEdit.hide()
        self._init_Combo_box()
        self.show()

    def _init_Combo_box(self):
        self.comboBox.currentTextChanged.connect(self.on_combobox_changed)
        for file_type in FileType:
            self.comboBox.addItem(file_type.value)

    def on_combobox_changed(self, text):
        if text == "Custom":
            self.customLineEdit.show()
        else:
            self.customLineEdit.hide()

    def get_filetype(self):
        selected_value = self.comboBox.currentText()
        file_type = FileType(selected_value)
        return file_type

    def get_custom_file_types(self):
        return self.customLineEdit.text()

    def selectButtonSetEnabled(self, value: bool):
        self.selectFolderButton.setEnabled(value)

    def get_source_folder_path(self):
        return QFileDialog.getExistingDirectory(self, "Select Folder")

    def update_progressBar_progress(self, progress):
        self.progressBar.setValue(progress)

    def show_progressBar(self):
        self.progressBar.setValue(0)
        self.progressBar.show()

    def copy_finished(self):
        self.progressBar.setValue(100)
        self.selectFolderButton.setEnabled(True)
        self.show_message("Alert", "The files have finished copying")

    def copy_canceled(self):
        self.progressBar.setValue(0)
        self.selectFolderButton.setEnabled(True)
        self.show_message("Alert", "The process was canceled")

    def not_files(self):
        self.selectFolderButton.setEnabled(True)
        self.show_message("Alert", "No file found to copy")

    def show_message(self, type_message: str, message: str):
        QMessageBox.information(self, type_message, message)

    def show_alert(self):
        alert = QMessageBox()
        alert.setIcon(QMessageBox.Icon.Question)
        alert.setText("Are you sure?")
        alert.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        alert.setDefaultButton(QMessageBox.StandardButton.No)
        response = alert.exec()
        if response == QMessageBox.StandardButton.Yes:
            return True
        elif response == QMessageBox.StandardButton.No:
            return False
