from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import QThread
import os
import sys
from worker import Worker
import random
import string

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filename = "main.ui"
        absolute_path = os.path.join(base_dir, filename)
        uic.loadUi(absolute_path, self)
        self.progressBar.hide()
        self.selectFolderButton.clicked.connect(self.startCopy)
        self.cancelPushButton.clicked.connect(self.cancelButton)
        self.worker = None
  
    def updateLabel(self, value: str):
        self.label.setText(str(value))

    def startCopy(self):
      if self.worker is not None: return # ya hay archivos copiandose
      # source folder
      self.source_folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
      # to_folder_path
      self.to_folder_path = self.create_folder(self.source_folder_path)
      if self.to_folder_path is None: return
      self.selectFolderButton.setEnabled(False)
      self.progressBar.show()
      # start copying
      self.worker = Worker(self.source_folder_path, self.to_folder_path)
      self.worker.progress_changed.connect(self.update_progress)
      self.worker.finished.connect(self.copy_finished)
      self.worker.start()

    def create_folder(self, source_folder_path: str):
      try:
        folder_name = 'folder_' + self.generate_unique_name()
        folder_path = os.path.join(source_folder_path, '..', folder_name )
        print(folder_path)
        os.makedirs(folder_path)
        QMessageBox.information(self, 'Alerta', f'Todo el contenido va a ser copiado a la carpeta llamada {folder_name}')
        return folder_path
      except OSError as e:
        QMessageBox.information(self, 'Error', f'Error: {e}')
        print(f'Error al crear la carpeta: {e}')
    
    def generate_unique_name(self,length=5):
      characters = string.ascii_letters + string.digits
      unique_name = ''.join(random.choice(characters) for _ in range(length))
      return unique_name

    def cancelButton(self):
      if self.worker is not None:
          self.worker.cancelCopy()
          self.worker = None
          self.progressBar.setValue(0)
          self.selectFolderButton.setEnabled(True)
          QMessageBox.information(self, 'Alert', 'Process was cancelled')

    def update_progress(self, progress):
        self.progressBar.setValue(progress)
    
    def copy_finished(self):
        self.progressBar.setValue(100)
        self.worker = None
        self.selectFolderButton.setEnabled(True)
        QMessageBox.information(self, 'Alert', 'The files have finished copying')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())