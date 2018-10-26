import sys
from cx_Freeze import setup,Executable
import google

build_exe_options = {
    "packages":["numpy","flask","tensorflow","matplotlib","requests","blockchain",
        "data","client","nn","miner","google","tkinter","ssl","os","glob","pickle"],
    "excludes":[]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="miner",
    version="1.0",
    description="Miner",
    options={"build_exe":build_exe_options},
    executables=[
        Executable("miner.py",base=base),
        Executable("client.py",base=base),
        Executable("make_graph.py",base=base)
        ])
