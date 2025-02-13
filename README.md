*This README.md file was generated on 20250213 by Amarin Muelthaler*

General Information
------------------

# Demonstration of Algorithmic Facial Expression Analysis with DeepFace

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

4. **Storage Space:**
	The project requires less than 1.5 GB of storage space, but this is highly dependent on the video material being input


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

- It is recommended to navigate to the folder using "Explorer" (Windows) and then copying the folder path to ensure the correct file path.
- The copied path must lead to a folder, not a file for it to work. 


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

The output of the analysis is:
- One .csv file per video of the analysis by DeepFace
- One Excel-file per video of the analysis by DeepFace
- One combined file of all videos that were analysed both in the .csv format and the .xlsx (Excel sheet) format
	Since Python can handle .csv files significantly better than .xlsx files, both formats are created.


### 5. Run the visualisation
- After having finished the analysis, you can do the visualisation
- To run the visualization, use the command:
	"python main.py visualisation --sheet sheet_name"
	where sheet_name is the name of the CSV file to be visualised.
- If the name of the sheet has a space in it, put quotes around the name to ensure the correct sheet is analysed. For example:
	python main.py visualisation --sheet "Jury 1_emotional_analysis.csv"
- It is recommended to initially only visualise one CSV file at once.

The output of the visualisation is: 
- A static plot of the emotions that surpassed the defined threshhold in the config.py file of the chosen sheet.
- An animated plot showing a timeline and development of the emotions over time.
- The created segments that were combined into the final animated plot (Not important after visualisation is finished)
- The segments file, ensuring the segments were combined in the right order (Not important after visualisation is finished)


### 6. Additional Commands
- If choosing to do both the analysis and visualisation, you can also just write:
	python main.py
	to run both the analysis and visualisation subsequently.


### 7. Doing adjustments
Most customisation can be done within the "config.py" file. The following are the most important variables to adjust:
- SAMPLING_RATE (Default = 1): This variable describes every n-th frame to be analysed. Can also be customised within the terminal.
	Adjust to a high number for preliminary tests of the program. Adjust to a low number at least equal to 1 for a detailed analysis.
- CONFIDENCE_THRESHOLD (Default = 80): This variable describes which value the emotions should surpass to be included in the visualisation. Reason for choosing 80% is that when all emotions are visualised, the plots are very cluttered. 
	Reason for this is that when all emotions are visualised, the plots are very cluttered. 
- PLOT_WIDTH (Default = 19.2): This describes how wide the plot should be.
- PLOT_HEIGHT (Default = 5.4): This describes the height of the plot.
	The plot dimensions are chosen deliberately to cover half of a 1920 x 1080 screen, so the other half can be used to add the video analysed for parallel display of analysis and analysed object.
- CPU_CORES (Default value is dependent on your system's physical cores): This is the basis for how many processes are being conducted simultaneously. 
	A higher number means generally faster processing, as long as your hardware can handle it. Too high number will cause the processes to fail due to overload. It is not recommended to adjust this.
- POOL_SIZE (Default = (CPU_CORES * 2) // 3): This decides how many processes are executed simultaneously and is dependent on the previously defined CPU_CORES. 
	Adjust this to reduce the load on the computer significantly. Minimum would be POOL_SIZE = 1 but that will make the program rather slow.
- NUM_SEGMENTS (Default = POOL_SIZE * 2): This is done to segment the animation even further to render the animation in two batches.


### 8. While the code is running
This is a description of the processes being displayed in the Anaconda Prompt or your Terminal of choice if "python main.py" is being executed with no additional arguments.
1. The necessary libraries will be installed from the "requirements.txt" file. This needs a stable internet connection and about 1 GB of available disk space just for these libraries.
2. You will probably encounter the following warning:
	"WARNING:tensorflow:From C:\Users\amari\anaconda3\Lib\site-packages\tf_keras\src\losses.py:2976: The name tf.losses.sparse_softmax_cross_entropy is deprecated. Please use tf.compat.v1.losses.sparse_softmax_cross_entropy instead."
	This is a warning stemming from DeepFace's usage of a deprecated command from its tensorflow dependency. Maybe this will get fixed in the future. 
	This warning is expected to be raised every time DeepFace is called upon. When operating with multiple processes, the warning will apprear once for every process.
	Due to that after step 4 the warning will be printed once for every process (equivalent to POOL_SIZE).
3. The code will state how many video files have been found and list them
4. Then it will be stated with which video file the processing will beginn. 
5. In the next step, information of the reading of the video file will be communicated.
6. Then the number of detected frames is stated. That number should be equal/very similar to the seconds of your input video times the video's frame rate.
7. Next the processing of the individual frames by DeepFace is happening. The code is designed to notify the user every time the 10% mark of processing this singular video file has been surpassed.
8. At the end you will receive a brief recap on the emotions that have been analysed.
9. If applicable, the next video will be analysed, and steps 5-7 are repeated until all videos have been processed.
10. Afterwards the visualisation is initialised.
11. First the static plot of the current sheet is created.
11. Then the visualisation continues by segmenting the frames of the selected data into the number of segments previously defined (currently set to twice the number of Processes).
12. Then the framework for the visualisation is initialised.
13. You will be able to see the progress every 10%, however only one segment will be displayed so the most recent one to surpass the 10% mark is shown.
14. Once a segment is done, a message will appear stating that the segment is saved.
15. Once all segments have been saved, they will be automatically combined into one video.
16. Steps 11-15 will repeat for all available sheets, except the combined one, unless only one sheet has been specified.
17. Once all sheets have been visualised the visualisation is finished

If you execute only the analyisis, the process will stop after finishing with step 9.
If you execute only the visualisation, the process will start with step 10 and end with step 17

#################################################################################
**Note:** FACS emotions are: joy, sadness, anger, surprise, fear, disgust, and contempt. 
DeepFace is set up to test for seven emotions: happy, sad, angry, surprised, disgusted, fearful, and neutral. 
Thus contempt is an emotion not measured by DeepFace. 
In the final visualisation of our videos not all emotions were displayed.
Reason being is that they were either not expressed or did not surpass the chosen 80% threshold.
################################################################################


### Results
Processing time for the individual processes:

The analysis for three videos of 4 minutes and 30 seconds length took a bit more than 29 minutes (1755.84 seconds) in total.
Each video took about 8-10 minutes to be processed but the setup of the models and installation of dependencies was not taken into account

The visualisation of the datasheet of each each video took in total over 16 minutes (967.38 seconds).
Each data sheet took about 5-6 minutes to be processed.


### Specifications
These processing times were achieved with the following hardware:
CPU: Ryzen 9 9950X
RAM: 64 GB (2x 32GB) DDR5 working at 4800MT/s speed
GPU acceleration was not utilised and is thus is not taken into consideration.