from PyQt6.QtCore import QObject, QThread, pyqtSignal
import shutil
import os

class Worker(QThread):
  finished = pyqtSignal()
  progress_changed = pyqtSignal(int)

  def __init__(self, source: str, to: str):
    super().__init__()
    self.source = source
    self.to = to
    self.cancel = False
  
  def run(self):
    total = sum(len(files) for _, _, files in os.walk(self.source))
    progress = 0
    self.progress_changed.emit(progress)
    # shutil.copytree(self.source, self.to, ignore=shutil.ignore_patterns('*'))
    for root, dirs, files in os.walk(self.source):
      for file in files:
        if self.cancel:
          return
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            src_path = os.path.join(root, file)
            dest_path = os.path.join(self.to, file)
            if os.path.exists(dest_path):
                dest_path = self._get_unique_filename(dest_path)
            shutil.copyfile(src_path, dest_path)
            progress += 1
            self.progress_changed.emit(int(progress / total * 100))
    if not self.cancel:
        self.finished.emit()
  
  def _get_unique_filename(self, filename):
    name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(f"{name}_{counter}{ext}"):
      counter += 1
    return f"{name}_{counter}{ext}"
  
  def cancelCopy(self):
    self.cancel = True