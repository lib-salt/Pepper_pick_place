# **Pepper as a Domestic Helper**

The main aim of the project is to test the feasability of Pepper as a domestic helper.
---

## **Environment Setup**
### Anaconda environments
For the NAOqi libraries to work, it is necessary to have a 2.7 Python enviroment that runs in 32-bit, alongside a Python 3 environment.
- Download miniconda for the 32 bit environment from the archives found here: https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86.exe
- Download regular anaconda (if not already installed)
- Setup python 2.7 environment:
    * Create and activate conda environment
        ```
        conda create --name pepper27 python==2.7
        conda activate pepper27
        ```
    * Pip installations
        ```
        pip install matplotlib numpy==1.16.6 opencv-python==4.2.0.32
        ```
- Setup python 3.12 environment:
    * Create and activate conda environment
        ```
        conda create --name pepper3 python==3.12
        conda activate pepper3
        ```
    * Pip installations
        ```
        pip install matplotlib numpy opencv-python mediapipe pillow torch ultralytics
        ```

- copy and paste your Python 2.7 environment into your Anaconda envs folder you can avoid entering the environment path when activating

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
conda_path = "Path to your own activate.bat for your 32 bit environment"
env_1 = "Full path to your Python 2.7 Conda environment"
env_2 = "Name of your Python 3 environment"
```
---
## object rec on computer
---
## Calibration and depth tester

