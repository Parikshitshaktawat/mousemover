from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might miss some required modules.
build_exe_options = {
    "packages": ["tkinter", "pyautogui", "pyclick"],
    "includes": ["pyclick.humancurve"],
    "excludes": [],
    "include_files": []
}

# Base setting for Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # This hides the console window.

# Define the setup for the application
setup(
    name="MouseMoverApp",
    version="1.0",
    description="An automatic mouse mover and clicker app",
    options={"build_exe": build_exe_options},
    executables=[Executable("MouseMover.py", base=base)]  # Replace "your_script.py" with the main script filename.
)
