# Recursive Files Copier

A GUI application built with PyQt that recursively scans a folder to copy all images and videos, exploring all subfolders within the main directory.

# Run

`pip install -r requirements.txt`
`python main.py`

# Create Executable Windows

`pip install cx-Freeze`
`python setup.py build`

# Create Executable Linux

`pip install pyinstaller`
`pyinstaller --onefile --windowed --add-data="main.ui:." main.py`
