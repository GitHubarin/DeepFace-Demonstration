import os
import sys
import importlib.util
import subprocess
import warnings
import multiprocessing as mp
from ffmpeg_installer import ensure_ffmpeg

# Suppress Python deprecation warnings.
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set TensorFlow environment variables.
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # '3' hides INFO, WARNING & ERROR

# Define the requirements path locally.
REQUIREMENTS_PATH = "requirements.txt"

def install_dependencies(requirements_path):
    """
    Install the required dependencies listed in the requirements file.

    Args:
        requirements_path (str): Path to the requirements file.

    Raises:
        FileNotFoundError: If the requirements file is not found.
    """
    try:
        with open(requirements_path) as file:
            packages = [line.strip() for line in file if line.strip() and not line.startswith("#")]
        for package in packages:
            pkg_name = package.split("==")[0].strip()
            # Map package names to module names if they differ.
            module_name = {"tf-keras": "tf_keras", "opencv-python": "cv2"}.get(pkg_name, pkg_name)
            if importlib.util.find_spec(module_name) is None:
                print(f"Installing missing package: {package}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            else:
                print(f"Package '{package}' is already installed.")
        # Ensure FFmpeg is installed.
        ensure_ffmpeg()
    except FileNotFoundError:
        print(f"Error: '{requirements_path}' not found.")
        sys.exit(1)

if mp.current_process().name == "MainProcess":
    install_dependencies(REQUIREMENTS_PATH)

if __name__ == '__main__':
    print("Dependency installation completed.")
