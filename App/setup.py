import cx_Freeze
import sys
import os

os.environ['TCL_LIBRARY'] = r'C:\Users\Megan\AppData\Local\Programs\Python\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\Megan\AppData\Local\Programs\Python\Python36\tcl\tk8.6'

base = None

if sys.platform == 'win32':
    base = "Win32GUI"

include_files = [r"C:\Users\Megan\AppData\Local\Programs\Python\Python36\DLLs\tcl86t.dll",
                 r"C:\Users\Megan\AppData\Local\Programs\Python\Python36\DLLs\tk86t.dll",
                 "logo.ico",
                 "base.html"]

executables = [cx_Freeze.Executable("source.py", base=base, icon="logo.ico")]
packs = ["pkg_resources._vendor", "tkinter", "networkx", "numpy", "pandas", "asyncio"]
cx_Freeze.setup(
    name="UP Sankey Generator",
    options = {"build_exe": {"packages": packs,
                             "include_files": include_files}},
    version="1.0",
    description="UP Sankey Generator",
    executables=executables
)
