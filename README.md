# **Pepper as a Domestic Helper**

The main aim of the project is to test the feasability of Pepper as a domestic helper.

---

## **Environment Setup**

### Anaconda Environments

To support the NAOqi libraries, you need both a Python 2.7 (32-bit) environment and a Python 3.12 environment. 

1. **Download 32-bit miniconda (for Python 2.7)**:  
    [Miniconda 32-bit](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86.exe)

2. **Download Anaconda (for Python 3)**:  
    [Anaconda Downloads](https://www.anaconda.com/download)

3. **Setup Python 2.7 environment**:
    ```
    conda create --name pepper27 python==2.7
    conda activate pepper27
    pip install matplotlib numpy==1.16.6 opencv-python==4.2.0.32
    ```

4. **Setup Python 3.12 environment**:
    ```
    conda create --name pepper3 python==3.12
    conda activate pepper3
    pip install matplotlib numpy opencv-python mediapipe pillow torch ultralytics
    ```

5. (optional) **Copy and paste your Python 2.7 environment** into your Anaconda `envs` folder if it's from a different Conda install path.

---

### NAOqi SDK

Download the NAOqi Python SDK:
https://aldebaran.com/en/support/kb/nao6/downloads/nao6-software-downloads/  

1. Unzip the SDK and locate the `lib` folder
2. In `pepper_pipeline/config.py`, update:
    ```
    ROBOT_IP = 'your.pepper.robot.ip'
    NAOQI_PATH = r"C:/path/to/naoqi-sdk/lib"
    ```
3. Save and close the file

[Full NAOqi SDK install guide](http://doc.aldebaran.com/2-8/dev/python/install_guide.html)

---

## Running from Terminal
Open **two terminals**:  
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

## Running via Python Wrapper (`run_all.py`)

To run both environments with one command:

1. Open `run_all.py` in the project root.
2. Change the following lines:
    ```
    env_1 = "Name of your Python 2.7 environment"
    env_2 = "Name of your Python 3 environment"
    ```
3. Run the script:
    ```
    python run_all.py
    ```
### Optional: Build `.exe` for One-Click Launch

```
pip install pyinstaller
pyinstaller --onefile run_all.py
```

Move the generated `run_all.exe` (from the `dist` folder) into your root directory.
You can now double-click it to start both processes.

---

## Object Recognition on Local Machine (No Robot)

To test object recognition via webcam:
```
python object_recognition_on_external_computer/object_recognition_YOLO.py
```

Or:

```
python object_recognition_on_external_computer/object_recognition_MediaPipe.py
```

---

## Camera Calibration
In `camera_calibration/calibration_feed.py`, update:
```
sys.path.append(r"C:/path/to/naoqi-sdk/lib")
ip = 'your.pepper.robot.ip'
```

Then run:
```
python camera_calibration/calibration_feed.py
``` 

When done:
```
camera_calibration/calibrate.py
```

This will generate the `.npz` calibration file.

---

## Test Filter Testing

In `camera_calibration/depth_filter_test.py`, update:
```
sys.path.append(r"C:/path/to/naoqi-sdk/lib")
ip = 'your.pepper.robot.ip'
```

Run the script:
```
python camera_calibration/depth_filter_test.py
```

Comment/uncomment the different smoothing techniques in the script before running to compare results.
