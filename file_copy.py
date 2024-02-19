from PyQt6.QtCore import QObject, pyqtSignal
from worker import Worker
import random
import string
import os

class FileCopy(QObject):
  progress_changed = pyqtSignal(int)
  not_files_found = pyqtSignal()
  copy_finished = pyqtSignal()
  
  def __init__(self):
    super().__init__()
    self.copy_finished.connect(self.copy_finished_func)
    self.worker = None

  def start_copy(self,source_folder_path, to_folder_path):
    if self.is_copying_files(): return
    self.worker = Worker(source_folder_path, to_folder_path)
    self.worker.progress_changed.connect(self.progress_changed)
    self.worker.not_files_found.connect(self.not_files_found)
    self.worker.finished.connect(self.copy_finished)
    self.worker.start()

  def cancel_copy(self):
    if self.is_copying_files() is False:
        self.worker.cancelCopy()
        self.worker = None
  
  def copy_finished_func(self):
    self.worker = None
  
  def create_folder(self, source_folder_path: str):
      folder_name = 'folder_' + self.generate_unique_name()
      folder_path = os.path.join(source_folder_path, '..', folder_name )
      os.makedirs(folder_path)
      return folder_path
    
  def generate_unique_name(self,length=5):
      characters = string.ascii_letters + string.digits
      unique_name = ''.join(random.choice(characters) for _ in range(length))
      return unique_name
  
  def is_copying_files(self):
    """
      checks if a worker is currently copying files.
    """
    if self.worker is not None: return True
    else: return False