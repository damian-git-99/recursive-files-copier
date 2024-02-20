from PyQt6.QtCore import QObject, QThread, pyqtSignal
import shutil
import os

class Worker(QThread):
  finished = pyqtSignal()
  progress_changed = pyqtSignal(int)
  not_files_found = pyqtSignal()
  copy_canceled = pyqtSignal()

  def __init__(self, source: str, to: str):
    super().__init__()
    self.source = source
    self.to = to
    self.cancel = False
  
  def run(self):
    progress = 0
    self.progress_changed.emit(progress)
    total = self.count_images()
    print('Total Files Founded: '+str(total))

    if total == 0:
      self.not_files_found.emit()
      return

    for root, dirs, files in os.walk(self.source):
      for file in files:
        if self.cancel:
          self.copy_canceled.emit()
          return
        if self.should_handle_file(file):
            src_path = os.path.join(root, file)
            dest_path = os.path.join(self.to, file)
            if os.path.exists(dest_path):
                dest_path = self._get_unique_filename(dest_path)
            shutil.copyfile(src_path, dest_path)
            progress += 1
            self.progress_changed.emit(int(progress / total * 100))      
    if not self.cancel:
        self.finished.emit()
  
  def should_handle_file(self, file):
    return file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))

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
        if self.should_handle_file(file):
          count += 1
    return count
  
  def cancelCopy(self):
    self.cancel = True