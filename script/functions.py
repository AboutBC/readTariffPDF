import subprocess
import sys
import importlib.util

def install_packages(packages):
    for package in packages:
        print(package)
        spec = importlib.util.find_spec(package)
        if spec is None:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])