# DeepFace Emotion Analysis & Visualization

This project uses DeepFace for emotion analysis on videos and generates both static plots and animations from the analysis. 

## Prerequisites

1. **Windows:**
	The entire script is designed for the Windows operating system.

2. **Anaconda 3:**
	It is highly recommended that you install [Anaconda 3](https://www.anaconda.com/products/distribution). 
	Anaconda provides a Python environment with many useful packages pre-installed and makes managing dependencies easier. 
	If you have intermediate knowledge with Python this is not necessary and you can run the script in the environment of your choice.

3. **Internet Connection:**
	The project automatically downloads required models (e.g., Python libraries or model weights) if they are not found on your system.

## Installation Steps


### 1. Install Anaconda 3
- Download and install [Anaconda 3](https://www.anaconda.com/products/distribution) following the instructions for your operating system.
- During installation, make sure to install the "Anaconda Prompt" to run your commands. Alternatively allow Anaconda to add itself to your PATH.
- If not directly installed, use the "Anaconda Navigator" to install "Anaconda Prompt".


### 2. Download the project folder
- Download the entire project folder and place it somewhere you remember.


### 3. Run Anaconda Prompt as an Administrator and navigate to the Project Folder
- You need to Change directory (cd) to the project folder. For example:
	cd C:\Users\your_username\Documents\Deepface_emotion_analysis
	Here "cd" stands for the command change directory, so that we navigate to the folder where the code and the videos to be analysed are located in.

- It is recommended to navigate to the folder using "Explorer" (Windows) and then copying the file path to ensure the correct file path.


### 4. Run the Analysis
- To run the analysis on your video files, place your video files (supported formats: .mp4, .avi, .mov, .mkv) into the videos folder
- The command to run the analysis is:
	python main.py analysis --sampling_rate n
	where n is the sampling rate, describing every n-th frame that shall be analysed.

- For example, to analyse every 1000th frame, type into the Anaconda Prompt:
	python main.py analysis --sampling_rate 1000
	This command will analyse every 1000th frame of each video in the videos folder.

- It is recommended to first try this out with one video and a high sampling rate to see how long the entire process takes.
- This high sampling rate is dependent on the length of the video. Orient it on the length of the entire video.
- Usually, videos have 30 frames per second, thus multiply the length in seconds by 30 to determine the number of frames.
- During our testing, analysing every frame of a video took over 100 times longer than analysing every 1000th. This is why we recommend running it overnight and with a capable machine.
- Once you are ready for the analysis of every frame run:
	python main.py analysis
	to create an analysis of every frame. 

- Alternatively, 
	python main.py analysis --sampling_rate 1
	also works because the default value for the sampling rate is 1.

The result of the analysis is:
- One .csv file of the analysis by DeepFace 


### 5. Run the visualisation
- After having finished the analysis, you can do the visualisation
- To run the visualization, use the command:
	"python main.py visualisation --sheet sheet_name"
	where sheet_name is the name of the CSV file to be visualised.
- If the name of the sheet has a space in it, put quotes around the name to ensure the correct sheet is analysed. For example:
	python main.py visualisation --sheet "Jury 1_emotional_analysis.csv"

- It is recommended to only visualise one CSV file at once.

The result of the visualisation is: 
- A static plot of the emotions that surpassed the defined threshhold in the config.py file of the chosen sheet.
- An animated plot showing a timeline and development of the emotions over time.
- The created segments that were combined into the final animated plot (Not important after visualisation is finished)
- The segments file, ensuring the segments were combined in the right order (Not important after visualisation is finished)


### Additional Commands
- If choosing to do both the analysis and visualisation, you can also just write:
	python main.py
	to run both the analysis and visualisation subsequently.

#################################################################################

**Note**: DeepFace is set up to test for seven emotions: happy, sad, angry, surprised, disgusted, fearful, and neutral. In the final outcome with our videos not all emotions were displayed. Reason being is that they were either not expressed or did not surpass the chosen 80% threshold.
FACS emotions are: joy, sadness, anger, surprise, fear, disgust, and contempt. Contempt as an emotion is not measured by DeepFace.

################################################################################

Special Thanks to:
Peter & David
