from PyQt6.QtWidgets import QApplication
import sys
from main_controller import MainController
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = MainController(window)
    sys.exit(app.exec())