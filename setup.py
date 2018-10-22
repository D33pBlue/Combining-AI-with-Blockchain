import sys
from cx_Freeze import setup,Executable

build_exe_options = {
    "packages":["os","flask","tensorflow","matplotlib","requests"],
    "excludes":[]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="miner",
    version="1.0",
    description="Miner",
    options={"build_exe":build_exe_options},
    executables=[Executable("miner.py",base=base)])
