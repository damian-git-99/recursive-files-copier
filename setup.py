import sys
from cx_Freeze import setup, Executable

base = None

if sys.platform == "win32":
    base = "Win32GUI"  # Use this option to create a GUI executable on Windows

executables = [Executable("main.py", base=base)]

options = {
    "build_exe": {
        "packages": [],
        "include_files": ['./main.ui'],
        'excludes': ['tkinter']
    },
}

setup(
    name="YourAppName",
    version="1.0",
    description="Your application description",
    options=options,
    executables=executables
)