import os
import argparse
import sys
import multiprocessing as mp
import warnings
import importlib.util
import config
import ffmpeg_installer
from ffmpeg_installer import ensure_ffmpeg
import subprocess

# Suppress Python deprecation warnings.
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Set TensorFlow environment variables.
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# Set TF_CPP_MIN_LOG_LEVEL:
# '0' => all messages, '1' => hide INFO, '2' => hide INFO & WARNING, '3' => hide INFO, WARNING & ERROR
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

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
            module_name = {"tf-keras": "tf_keras", "opencv-python": "cv2"}.get(pkg_name, pkg_name)
            if importlib.util.find_spec(module_name) is None:
                print(f"Installing missing package: {package}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            else:
                print(f"Package '{package}' is already installed.")
        # Ensure FFmpeg is installed.
        ffmpeg_installer.ensure_ffmpeg()
    except FileNotFoundError:
        print(f"Error: '{requirements_path}' not found.")
        sys.exit(1)

# Run dependency installation only if this is the main process.
if mp.current_process().name == "MainProcess":
    install_dependencies(config.REQUIREMENTS_PATH)

from analysis import run_analysis
from visualisation import run_visualisation

def main():
    """
    Main function to run the Video Emotion Analysis and Visualisation Tool.
    Looks at command-line arguments to decide whether to run analysis, visualisation, or both.
    """
    parser = argparse.ArgumentParser(
        description="Video Emotion Analysis and Visualisation Tool"
    )
    
    # Command to choose analysis or visualisation.
    parser.add_argument("command", nargs="?", choices=["analysis", "visualisation"], default=None,
                        help="Specify whether to run 'analysis', 'visualisation', or leave empty to run both.")
    
    # Sampling rate argument for analysis.
    parser.add_argument("--sampling_rate", type=int, default=config.SAMPLING_RATE,
                        help="Analyze every n-th frame (default is as set in config.py).")
    
    # Optional argument for visualisation: specify a particular CSV file (sheet).
    parser.add_argument("--sheet", type=str, default="",
                        help="Optional: specify the analysis CSV file to process (e.g. 'Entrepreneur_emotional_analysis.csv').")
    
    args = parser.parse_args()

    # Default behavior: Run both analysis and visualisation if no command is provided.
    if args.command is None:
        print("No command specified. Running both analysis and visualisation...")
        
        # Step 1: Run analysis
        print(f"Starting analysis with a sampling rate of every {args.sampling_rate} frame(s)...")
        run_analysis(frame_sampling_rate=args.sampling_rate)
        
        # Step 2: Run visualisation
        print("Starting visualisation after analysis...")
        run_visualisation(sheet=args.sheet)
    
    # Handle individual commands
    elif args.command == "analysis":
        print(f"Starting analysis with a sampling rate of every {args.sampling_rate} frame(s)...")
        run_analysis(frame_sampling_rate=args.sampling_rate)
    
    elif args.command == "visualisation":
        print("Starting visualisation...")
        # Pass the sheet parameter to the visualisation routine.
        run_visualisation(sheet=args.sheet)


if __name__ == '__main__':
    main()