import os
import subprocess
import sys
import platform
import urllib.request
import zipfile


def is_ffmpeg_setup():
    """
    Check if FFmpeg is available in the system PATH and ready to use.
    Returns:
        bool: True if FFmpeg is set up and accessible, False otherwise.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def is_ffmpeg_installed(ffmpeg_bin):
    """
    Check if FFmpeg is installed in the specified directory.
    Args:
        ffmpeg_bin (str): Path to the FFmpeg bin directory.
    Returns:
        bool: True if FFmpeg is installed, False otherwise.
    """
    ffmpeg_exe = os.path.join(ffmpeg_bin, "ffmpeg.exe")
    return os.path.exists(ffmpeg_bin) and os.path.exists(ffmpeg_exe)


def validate_ffmpeg_directory(ffmpeg_dir):
    """
    Validate the extracted FFmpeg directory structure.
    Args:
        ffmpeg_dir (str): Path to the extracted FFmpeg directory.
    Returns:
        str: Path to the FFmpeg bin directory if valid, None otherwise.
    """
    extracted_dirs = [d for d in os.listdir(ffmpeg_dir) if os.path.isdir(os.path.join(ffmpeg_dir, d))]
    if not extracted_dirs:
        print("Error: No directories found after extracting FFmpeg.")
        return None
    target_dir = extracted_dirs[0]
    ffmpeg_bin = os.path.join(ffmpeg_dir, target_dir, "bin")
    if not os.path.exists(ffmpeg_bin):
        print(f"Error: The 'bin' directory is missing in the extracted FFmpeg files at {ffmpeg_bin}.")
        return None
    ffmpeg_exe = os.path.join(ffmpeg_bin, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_exe):
        print(f"Error: ffmpeg.exe not found in the expected location: {ffmpeg_exe}.")
        return None
    return ffmpeg_bin


def add_to_path_if_needed(ffmpeg_bin):
    """
    Add FFmpeg's bin directory to the current process's PATH if not already present.
    Args:
        ffmpeg_bin (str): Path to the FFmpeg bin directory.
    """
    if ffmpeg_bin not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + ffmpeg_bin
        print(f"Added {ffmpeg_bin} to the current process's PATH.")


def download_and_extract_ffmpeg(ffmpeg_url, ffmpeg_dir):
    """
    Download and extract FFmpeg from the given URL.
    Args:
        ffmpeg_url (str): URL to download the FFmpeg ZIP file.
        ffmpeg_dir (str): Directory to extract FFmpeg.
    Returns:
        str: Path to the FFmpeg bin directory if successful, None otherwise.
    """
    ffmpeg_zip = "ffmpeg.zip"
    print("Downloading FFmpeg...")
    try:
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return None

    print("Extracting FFmpeg...")
    try:
        with zipfile.ZipFile(ffmpeg_zip, "r") as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
    except zipfile.BadZipFile:
        print("Error: The downloaded file is not a valid ZIP file.")
        return None

    return validate_ffmpeg_directory(ffmpeg_dir)


def download_and_install_ffmpeg():
    """
    Download and install FFmpeg automatically using a ZIP file.
    This function is currently implemented for Windows only.
    It downloads the FFmpeg ZIP file, extracts it, and appends the bin directory to the system PATH.
    """
    if platform.system() != "Windows":
        print("FFmpeg installation is not yet automated for this OS.")
        sys.exit(1)

    # Define constants
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    ffmpeg_dir = "ffmpeg"

    # Check if FFmpeg is already downloaded and extracted
    if os.path.exists(ffmpeg_dir):
        ffmpeg_bin = validate_ffmpeg_directory(ffmpeg_dir)
        if ffmpeg_bin and is_ffmpeg_installed(ffmpeg_bin):
            print("FFmpeg is already downloaded and installed locally.")
            add_to_path_if_needed(ffmpeg_bin)
            if is_ffmpeg_setup():
                print("FFmpeg is ready to use!")
                return
        else:
            print("Existing FFmpeg installation is incomplete. Reinstalling...")

    # Download and extract FFmpeg
    ffmpeg_bin = download_and_extract_ffmpeg(ffmpeg_url, ffmpeg_dir)
    if not ffmpeg_bin:
        print("FFmpeg installation failed.")
        sys.exit(1)

    # Add FFmpeg to PATH and verify installation
    add_to_path_if_needed(ffmpeg_bin)
    if is_ffmpeg_setup():
        print("FFmpeg installed successfully!")
    else:
        print("FFmpeg installation failed after extraction.")
        sys.exit(1)


def ensure_ffmpeg():
    """
    Ensure FFmpeg is installed; if not, download and install it.
    This function checks if FFmpeg is available in the system PATH and attempts to install it if not found.
    """
    if is_ffmpeg_setup():
        print("FFmpeg is already set up and accessible.")
    else:
        print("FFmpeg not found! Attempting to install...")
        download_and_install_ffmpeg()


if __name__ == "__main__":
    ensure_ffmpeg()