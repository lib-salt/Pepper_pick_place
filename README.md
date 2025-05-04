# **Pepper as a Domestic Helper**

The main aim of the project is to test the feasability of Pepper as a domestic helper.
---

## **Environment Setup**
### Anaconda environments
For the NAOqi libraries to work, it is necessary to have a 2.7 Python enviroment that runs in 32-bit, alongside a Python 3 environment.
- Download miniconda for the 32 bit environment from the archives found here: https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86.exe
- Download regular anaconda (if not already installed)
- Setup Python 2.7 environment:
    * Create and activate Conda environment
        ```
        conda create --name pepper27 python==2.7
        conda activate pepper27
        ```
    * Pip installations
        ```
        pip install matplotlib numpy==1.16.6 opencv-python==4.2.0.32
        ```
- Setup Python 3.12 environment:
    * Create and activate Conda environment
        ```
        conda create --name pepper3 python==3.12
        conda activate pepper3
        ```
    * Pip installations
        ```
        pip install matplotlib numpy opencv-python mediapipe pillow torch ultralytics
        ```

- Copy and paste your Python 2.7 environment into your Anaconda envs folder to avoid entering the full environment path when activating

### NAOqi SDK
The NAOqi python SDK is available from:  
https://aldebaran.com/en/support/kb/nao6/downloads/nao6-software-downloads/  
- Download the NAOqi Python SDK
- Unzip and find the lib folder path
- In `pepper_pipeline/config.py`, update the following lines:
    ```
    ROBOT_IP = 'your.pepper.robot.ip'
    NAOQI_PATH = r"C:/path/to/naoqi-sdk/lib"
    ```
- Save and close the file

Further documentation and guidance on the NAOqi SDK installation:  
http://doc.aldebaran.com/2-8/dev/python/install_guide.html

---
## Running from terminal
Open **two terminals**, and activate each environment:  
**Terminal 1 (Python 2.7)**
```
conda activate pepper27
python pepper_pipeline/main.py
```
**Terminal 2 (Python 3.12)**
```
conda activate pepper3
python object_recognition/stream.py
```

---
## Running from Python Wrapper (Create launcher)
To start the full system with a single command:
- Open `run_all.py` in the root folder:
- Update the following lines in the file:
    ```
    env_1 = "Name of your Python 2.7 environment"
    env_2 = "Name of your Python 3 environment"
    ```
- Save and close the file
- Run the file in terminal using:
    ```
    python run_all.py
    ```
- Or (optionally) compile it into an .exe to avoid terminal to run the code
    ```
    pip install pyinstaller
    pyinstaller --onefile run_all.py
    ```
- This will create two folders `dist` and `build`
- Move the `run_all.exe` from the `dist` folder into the root directory
- You can now double click this file for easy start up
---
## Using object recognition on computer
If you don't want to connect to a robot and solely test the object recognition using a webcam you can run:
```
python object_recogniton_on_external_computer/object_recognition_YOLO.py
```
Or alternatively:
```
python object_recogniton_on_external_computer/object_recognition_MediaPipe.py
```
Depending on which model you wish to run.

---
## Run camera calibration
To run the camera calibration on the Pepper robot change the following lines in `calibration_feed.py`:
```
sys.path.append(r"C:/path/to/naoqi-sdk/lib")
ip = 'your.robot.ip'
```
Save and close the file and run:
```
python camera_calibration/calibration_feed.py
``` 
Wait for it to finish and then run
```
camera_calibration/calibrate.py
```
To create the `.npz` file.

---
## Run camera calibration
To run test the
