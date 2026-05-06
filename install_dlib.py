import sys
import platform
import urllib.request
import subprocess
import os

py_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
arch = "win_amd64" if platform.architecture()[0] == "64bit" else "win32"

wheel_name = f"dlib-19.24.2-{py_version}-{py_version}-{arch}.whl"

url = f"https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/{wheel_name}"

print(f"Downloading {wheel_name}...")
urllib.request.urlretrieve(url, wheel_name)

print("Installing dlib...")
subprocess.check_call([sys.executable, "-m", "pip", "install", wheel_name])

os.remove(wheel_name)

print("Done! dlib installed successfully.")
