from PyQt6.QtWidgets import QApplication
import sys
from src import MainController, MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = MainController(window)
    sys.exit(app.exec())