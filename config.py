import psutil

# Analysis and video input/output settings.
FRAME_STEP = 1 # Analyse every n-th frame. The input through the terminal with sampling_rate can override this.
REQUIREMENTS_PATH = "requirements.txt" #Infor where the requirements file is located.
VIDEO_PATH = "videos"              # Folder with the input video files to be analysed.
ANALYSIS_DIR = "analysis_sheets"   # Folder where analysis CSV/Excel files are saved.
CSV_DIR = "CSV"                    # Folder where the CSV files are saved.
EXCEL_DIR = "Excel"                # Folder where the Excel files are saved.
PLOTS_DIR = "plots"                # Folder where the Plots files are saved.
ANIMATIONS_DIR = "animations"             # Folder where the animation files and segments are saved.

# Threshholds
FACE_CONFIDENCE_THRESHOLD = 0.9   # Confidence threshold for face detection.
EMOTION_SCORE_THRESHOLD = 50     # Threshold for dominant emotion detection.
CONFIDENCE_THRESHOLD = 80 # Chose confidence threshold for emotion detection

# Thread and Segmentation settings
CPU_CORES = psutil.cpu_count(logical=False)  # You can also use a fixed value.
POOL_SIZE = (CPU_CORES * 2) // 3 # We set the pool size to two thirds the number of CPU cores.
NUM_SEGMENTS = POOL_SIZE * 2 # Number of segments to divide the video into for parallel processing. This will eleviate the load on the CPU and especially the RAM.

# Frame and plot settings.
FRAME_RATE = 30                    # Default frame rate (if not read from video).
PLOT_WIDTH = 19.2                   # Width of the static plot (in inches).
PLOT_HEIGHT = 5.4                   # Height of the static plot (in inches).
PLOT_DPI = 100                      # Pixels per inch (dots per inch)