from PyQt6.QtWidgets import QApplication
import sys
import os
from src import MainController, MainWindow
from src.file_copy import FileCopy

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller
            return sys._MEIPASS
        else:
            # cx_Freeze
            return os.path.dirname(sys.executable)
    else:
        # Running in development
        return os.path.dirname(os.path.abspath(__file__))

def main():
    app = QApplication(sys.argv)
    base_dir = get_base_dir()
    window = MainWindow(base_dir)
    file_model = FileCopy()
    controller = MainController(window, file_model)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
