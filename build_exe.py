import subprocess
import os
import sys

def build():
    print("Starting SmokeDash Build Process...")
    
    # 1. Define PyInstaller command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--noconsole",
        # Add Style
        "--add-data", "style.qss;.",
        # Add Languages folder
        "--add-data", "languages;languages",
        # Use main.py as entry point
        "main.py",
        "--name", "SmokeDash_ERP",
        "--clean"
    ]
    
    # 2. Add hidden imports if necessary (qtawesome sometimes needs them)
    # cmd += ["--hidden-import", "qtawesome.QtDrawing"]
    
    # 3. Run PyInstaller
    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print("Executable located in: dist/SmokeDash_ERP.exe")
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"BUILD FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
