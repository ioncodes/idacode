HOST = "127.0.0.1"
PORT = 7065
DEBUG_PORT = 7066
ALLOW_UNSAFE_ORIGIN = False
LOGGING = True

# Heuristically detect the python executable path
PYTHON = ""
import sys
import os
import platform
for path in sys.path:
    if platform.system() == "Windows":
        path = path.replace("/", "\\")

    split = path.split(os.sep)
    if split[-1].endswith(".zip"):
        path = os.path.dirname(path)
        if platform.system() == "Windows":
            python_executable = os.path.join(path, "python.exe")
        else:
            python_executable = os.path.join(path, "..", "bin", "python3")
        python_executable = os.path.abspath(python_executable)

        if os.path.exists(python_executable):
            print("[IDACode] Detected python executable: " + python_executable)
            PYTHON = python_executable
            break
if len(PYTHON) == 0 or not os.path.exists(PYTHON):
    raise FileNotFoundError("[IDACode] Could not find python executable, report an issue!")
