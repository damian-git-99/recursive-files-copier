# Recursive Files Copier

A GUI application built with PyQt that recursively scans a folder to copy all images and videos, exploring all subfolders within the main directory.

# Run

`pip install -r requirements.txt`
`python main.py`

# Create Executable

`pip install cx-Freeze`
`python setup.py build`

# Create executable with PyInstaller

`pip install pyinstaller`
`python -m PyInstaller --onefile --windowed --add-data "./src/:./src" main.py`

# Execute Tests

`python -m pytest -v -s`
