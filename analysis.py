import os
import cv2
import time
import psutil
import logging
import pandas as pd
import numpy as np
import multiprocessing as mp
from collections import Counter
from deepface import DeepFace
import subprocess
import config

# =============================================================================
# Environment Setup & Global Variables
# =============================================================================
# Global error counter
error_counter = Counter()

# Define directories relative to the current working directory.
BASE_DIR = os.getcwd()
VIDEO_DIR = os.path.join(BASE_DIR, "videos")  # Folder with video files
ANALYSIS_DIR = os.path.join(BASE_DIR, "analysis_sheets")  # Folder for CSV & Excel outputs
LOG_DIR = os.path.join(BASE_DIR, "logs")  # Folder for per-video log files

# Create directories if they don't exist.
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Build the DeepFace model (using OpenFace, adjust as you see fit).
emotion_model = DeepFace.build_model("OpenFace")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "analysis.log")),
        logging.StreamHandler()
    ]
)

# =============================================================================
# Helper Functions
# =============================================================================
def get_num_processes():
    """
    Function to determine the number of physical cores and based on them make a balanced decision on the
    number of simultaneous processes to run. Since we are assuming the machine running the code to also
    be able to do other lightweight work, we have halved the number of CPU cores for a less intense operation.
    Adjust as seen fit, e.g., by deleting the //2 at the end to stop the halving or just writing your
    preferred number of simultaneous processes after "return".
    Returns:
        int: The number of simultaneous processes to be initiated during multiprocessing.
    """
    processes = config.POOL_SIZE
    return processes if processes else 4


def analyse_video(video_path, frame_sampling_rate=1):
    """
    Wrapper function to process a single video file.
    It extracts the 'person' identifier from the video's filename,
    prepares the output CSV (and Excel) file path, and then calls
    analyse_video_internal with the correct parameters.
    Args:
        video_path (str): Full path to the video file.
        frame_sampling_rate (int): Analyse every n-th frame.
    Returns:
        DataFrame or None: The analysis DataFrame (with an added 'person' column) or None on failure.
    """
    # Extract the base name of the video (without extension) to use as the person identifier.
    person = os.path.splitext(os.path.basename(video_path))[0]
    # Construct the output CSV file path in the analysis folder.
    output_csv = os.path.join(ANALYSIS_DIR, f"{person}_emotional_analysis.csv")
    # Optionally, you might also want to create a per-video log file here if desired.
    return analyse_video_internal(video_path, output_csv, person, frame_sampling_rate)


def get_dominant_emotion(emo):
    """
    Return the dominant emotion if its confidence is ≥ 50, else a message that no dominant
    emotion has been detected.
    Args:
        emo (dict): The emotions determined by DeepFace.
    Returns:
        str: The dominant emotion or a message indicating no dominant emotion detected.
    """
    if not emo:
        return 'no emotion detected'
    dominant_emotion = max(emo, key=emo.get)
    if emo[dominant_emotion] >= 50:
        return dominant_emotion
    return 'no dominant emotion detected'


# Global variable for the preloaded model
global_model = None

def init_worker(backend_model):
    """Initialize each worker with a preloaded model."""
    global global_model
    global_model = backend_model


def analyse_emotion_multiproc(args):
    """
    Analyse a single frame using the preloaded DeepFace model.
    Args:
        args (tuple): Contains (frame, frame_number, backend).
    Returns:
        tuple: (analysis_dict, dominant_emotion, error message)
    """
    frame, frame_number, backend = args
    # Check for empty frame.
    if frame is None or frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
        return None, None, f'Invalid frame at frame number {frame_number}.'
    try:
        # Perform DeepFace analysis using the preloaded model.
        analysis = DeepFace.analyze(
            img_path=frame,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend=backend
        )
        emotions = analysis[0].get('emotion', {})
        dominant_emotion = max(emotions, key=emotions.get)
        conf = emotions.get(dominant_emotion, np.float32(0))
        # Attach frame_number for reference.
        analysis[0]['frame_number'] = frame_number
        if conf >= 50:
            return analysis[0], dominant_emotion, None
        else:
            return analysis[0], 'no dominant emotion detected', None
    except Exception as e:
        logging.error(f'Error analysing frame {frame_number} with backend {backend}: {e}')
        error_counter['first_backend_error'] += 1
        return None, None, f'No emotion detected in frame {frame_number} with {backend}'


# =============================================================================
# Video Analysis Functions
# =============================================================================
def analyse_video_internal(video_path, output_csv, person, frame_sampling_rate):
    """
    Processes one video file: opens the video, samples frames at the specified rate,
    runs DeepFace analysis on each selected frame using multiprocessing,
    builds a DataFrame with the results, and saves both CSV and Excel files.
    Logs detailed timing information.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"Error: Could not open video {video_path}.")
        return None

    # Record the start time for this video.
    start_time = time.time()
    logging.info(f"Started processing video {video_path} at {time.ctime(start_time)}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    tasks = []
    frame_number = 0
    total_frames = 0

    # Collect frames for analysis based on the sampling rate.
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        total_frames += 1
        if frame_number % frame_sampling_rate == 0:
            tasks.append((frame, frame_number, 'opencv'))
        frame_number += 1

        if frame_number % 1000 == 0:
            interim_time = time.time()
            logging.info(f"Read frame {frame_number} or input video after {interim_time - start_time:.2f} seconds")

    cap.release()
    logging.info(f"Video {video_path} has {total_frames} frames; sampling rate: {frame_sampling_rate}; {len(tasks)} frames to analyse.")

    # Use multiprocessing with progress tracking.
    num_processes = get_num_processes()
    logging.info(f"Using {num_processes} processes for processing.")

    manager = mp.Manager()
    progress_counter = manager.Value('i', 0)  # Shared progress counter
    lock = manager.Lock()  # Explicit lock for synchronization
    total_tasks = len(tasks)

    def update_progress(result):
        """Callback function to update progress."""
        nonlocal progress_counter
        with lock:  # Use the explicit lock
            progress_counter.value += 1
            current_progress = progress_counter.value
            if current_progress % max(1, total_tasks // 10) == 0:  # Log every 10%
                elapsed_time = time.time() - start_time
                logging.info(
                    f"Processed {current_progress}/{total_tasks} frames ({current_progress / total_tasks * 100:.1f}%), Elapsed Time: {elapsed_time:.1f}s"
                )

    # Start timing the analysis phase
    analysis_start_time = time.time()

    results = []
    analysed_frames = 0
    unsuccessful_retries = 0

    with mp.Pool(processes=num_processes, initializer=init_worker, initargs=(emotion_model,)) as pool:
        for res in pool.imap_unordered(analyse_emotion_multiproc, tasks):
            update_progress(res)  # Update progress
            analysis_dict, emotion, error = res
            if analysis_dict:
                results.append(analysis_dict)
                analysed_frames += 1
            elif error:
                logging.warning(error)
                unsuccessful_retries += 1

    # Record the end time for the analysis phase
    analysis_end_time = time.time()
    analysis_duration = analysis_end_time - analysis_start_time

    # Record the overall end time for this video
    end_time = time.time()
    duration = end_time - start_time

    logging.info(f"Finished processing video {video_path} at {time.ctime(end_time)}; Duration: {duration:.2f} seconds")
    logging.info(f"Analysis phase took {analysis_duration:.2f} seconds")

    # Build DataFrame and save results.
    if results:
        df = pd.DataFrame(results)
        if 'emotion' in df.columns:
            df.rename(columns={'emotion': 'raw_output'}, inplace=True)
        emotions_list = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        for emo in emotions_list:
            df[emo] = df['raw_output'].apply(lambda x: x.get(emo, 0))
        df['dominant_emotion'] = df['raw_output'].apply(get_dominant_emotion)

        # Base column ordering for individual files.
        columns_order = ['frame_number', 'dominant_emotion'] + emotions_list + ['face_confidence', 'region', 'raw_output']
        columns_order = [col for col in columns_order if col in df.columns]
        df = df[columns_order]

        # Add the person column.
        df['person'] = person

        # Sort by frame_number for individual file export.
        df.sort_values(by="frame_number", inplace=True)

        # Save as CSV.
        df.to_csv(output_csv, index=False)

        # Also save as Excel.
        excel_file = output_csv.replace('.csv', '.xlsx')
        df.to_excel(excel_file, index=False)

        # Log a summary.
        emotion_counts = {}
        if 'dominant_emotion' in df.columns:
            unique_emotions = df['dominant_emotion'].unique()
            for e in unique_emotions:
                emotion_counts[e] = df['dominant_emotion'].tolist().count(e)
        logging.info("Emotion analysis results:")
        for emo, count in emotion_counts.items():
            logging.info(f"{emo}: {count} frames")
        logging.info(f"Total frames: {total_frames}")
        logging.info(f"Frame count: {frame_count}")
        logging.info(f"Frame rate: {frame_rate} FPS")
        logging.info(f"Analysed frames: {analysed_frames}")
        logging.info(f"Unsuccessful retries: {unsuccessful_retries}")
        logging.info(f"First backend errors (using opencv): {error_counter['first_backend_error']}")
        logging.info("Analysis completed.")
        return df
    else:
        logging.error("No analysis results to process.")
        return None
    

def process_all_videos(frame_sampling_rate=1):
    """
    Searches the VIDEO_DIR for video files, processes each one with the specified sampling rate,
    and then creates combined output files (CSV and Excel) with an added 'person' column.
    Logs timestamps and total durations for each file and for the entire process.
    Args:
        frame_sampling_rate (int): Analyse every n-th frame.
    """
    overall_start = time.time()
    logging.info(f"Started processing all videos at {time.ctime(overall_start)}")

    video_files = [
        os.path.join(VIDEO_DIR, f)
        for f in os.listdir(VIDEO_DIR)
        if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
    ]

    if not video_files:
        message = f"No video files found in the folder: {VIDEO_DIR}"
        print(message)
        logging.info(message)
        return

    # Create a list of just the file names (without the full path)
    file_names = [os.path.basename(f) for f in video_files]
    message = f"Found {len(video_files)} video file(s): {file_names}"
    print(message)
    logging.info(message)

    combined_dfs = []
    for video in video_files:
        print(f"Processing {video}...")
        logging.info(f"Processing {video}...")
        # Call the wrapper function that correctly prepares the arguments
        df = analyse_video(video, frame_sampling_rate=frame_sampling_rate)
        if df is not None:
            combined_dfs.append(df)

    if combined_dfs:
        combined_df = pd.concat(combined_dfs, ignore_index=True)

        # Sort the combined DataFrame by person first and then by frame_number.
        combined_df.sort_values(by=["person", "frame_number"], inplace=True)

        # Define a standard ordering for the combined file columns.
        emotions_list = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        combined_columns = ["frame_number", "person", "dominant_emotion"] + emotions_list + ["face_confidence", "region", "raw_output"]

        # Only keep columns that are present.
        combined_columns = [col for col in combined_columns if col in combined_df.columns]
        combined_df = combined_df[combined_columns]

        combined_csv = os.path.join(ANALYSIS_DIR, "combined_emotional_analysis.csv")
        combined_excel = os.path.join(ANALYSIS_DIR, "combined_emotional_analysis.xlsx")
        combined_df.to_csv(combined_csv, index=False)
        combined_df.to_excel(combined_excel, index=False)

        message = f"Combined analysis saved to:\n  CSV: {combined_csv}\n  Excel: {combined_excel}"
        print(message)
        logging.info(message)
    else:
        message = "No analysis data to combine."
        print(message)
        logging.info(message)

    overall_end = time.time()
    overall_duration = overall_end - overall_start
    logging.info(
        f"Finished processing all videos with {get_num_processes()} Processes at {time.ctime(overall_end)}; Total duration: {overall_duration:.2f} seconds"
    )
    print(
        f"Total processing time with {get_num_processes()} Processes for all videos: {overall_duration:.2f} seconds (started at {time.ctime(overall_start)}, finished at {time.ctime(overall_end)})."
    )


def run_analysis(frame_sampling_rate=1):
    """
    Runs the analysis for all videos found in the 'videos' folder,
    using the specified sampling rate.
    Args:
        frame_sampling_rate (int): Analyse every n-th frame.
    """
    process_all_videos(frame_sampling_rate)


if __name__ == '__main__':
    run_analysis()