# Recursive Files Copier

A GUI application built with PyQt6 that recursively scans a folder to copy all images and videos, exploring all subfolders within the main directory.

## Features

- Recursively scan folders and subfolders
- Selectively copy files based on type (images, videos, or both)
- Support for custom file extensions
- Option to compress files after copying
- Progress tracking with a visual progress bar

## Installation and Usage

### Run

`pip install -r requirements.txt`
`python main.py`

### Create Executable

`pip install cx-Freeze`
`python setup.py build`

### Execute Tests

`python -m pytest -v -s`

## License

This application is licensed under the GNU General Public License v3.0 (GPL-3.0). This is compatible with PyQt6's GPL license.

See the LICENSE.md file for more details on licensing options.
