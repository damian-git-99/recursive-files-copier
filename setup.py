import sys
from cx_Freeze import setup, Executable

base = None

if sys.platform == "win32":
    base = "Win32GUI"  # Use this option to create a GUI executable on Windows

executables = [Executable("main.py", base=base)]

options = {
    "build_exe": {
        "packages": [],
        "include_files": [("./src/main.ui", "./src/main.ui")],
        "excludes": ["tkinter"],
    },
}

setup(
    name="RecursiveFilesCopier",
    version="1.0",
    description="A tool to copy files recursively based on file types",
    options=options,
    executables=executables,
)
