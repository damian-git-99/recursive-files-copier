# Recursive Files Copier

A GUI application built with PyQt that recursively scans a folder to copy all images of a specific type, exploring all subfolders within the main directory.

# Run

`pip install -r requirements.txt`
`python main.py`

# Create Executable

`pip install pyinstaller`

### Windows `python -m PyInstaller --onefile --windowed --add-data "main.ui;."  .\main.py`

### Windows with nuitka: `python -m nuitka  --mingw64 --windows-disable-console --include-data-file=main.ui=main.ui --enable-plugin=pyqt6 --follow-imports --standalone --remove-output --output-dir=dist .\main.py`

### Linux `pyinstaller --onefile --windowed --add-data="main.ui:." main.py `
