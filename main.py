from PyQt6.QtWidgets import QApplication
import sys
from src import MainController, MainWindow
from src.file_copy import FileCopy

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    file_model = FileCopy()
    controller = MainController(window, file_model)
    sys.exit(app.exec())
