import psutil

# Analysis and video input/output settings.
SAMPLING_RATE = 1 # Analyse every n-th frame. The input through the terminal with sampling_rate can override this.
REQUIREMENTS_PATH = "requirements.txt" #Infor where the requirements file is located.
VIDEO_PATH = "videos"              # Folder with the input video files to be analysed.
ANALYSIS_DIR = "analysis_sheets"   # Folder where analysis CSV/Excel files are saved.
PLOTS_DIR = "plots"
ANIMATIONS_DIR = "animations"             # Folder for all plot images and/or animations.

# Frame and plot settings.
FRAME_RATE = 30                    # Default frame rate (if not read from video).
CONFIDENCE_THRESHOLD = 80 # Chose confidence threshold for emotion detection. Please adjust this value according to your needs.
PLOT_WIDTH = 19.2                   # Width of the static plot (in inches).
PLOT_HEIGHT = 5.4                   # Height of the static plot (in inches).
CPU_CORES = psutil.cpu_count(logical=False)  # You can also use a fixed value.
POOL_SIZE = (CPU_CORES * 2) // 3 # We set the pool size to two thirds the number of CPU cores.
NUM_SEGMENTS = POOL_SIZE * 2 # Number of segments to divide the video into for parallel processing. This will eleviate the load on the CPU and especially the RAM.