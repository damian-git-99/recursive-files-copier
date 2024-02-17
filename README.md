# Recursive Files Copier

A GUI application built with PyQt that recursively scans a folder to copy all images of a specific type, exploring all subfolders within the main directory.

# Run

`python main.py`

# Create Executable

`pip install pyinstaller`

### Windows `python -m PyInstaller --onefile --windowed --add-data "main.ui;."  .\main.py`

### Linux `pyinstaller --onefile --windowed --add-data="main.ui:." main.py `
