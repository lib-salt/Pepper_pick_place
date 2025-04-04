# **Pepper as a Domestic Helper**

The main aim of the project is to test the feasability of Pepper as a domestic helper.
---

## **Environment Setup**
### Anaconda environments
For the NAOqi libraries to work, it is necessary to have a 2.7 Python enviroment that runs in 32-bit, alongside a Python 3 environment.
- Download miniconda for the 32 bit environment from the archives found here: https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86.exe
- Download regular anaconda
- Setup python 2.7 environment:
    * Create and activate conda environment
        ```
        conda create --name myenv python==2.7
        conda activate myenv
        ```
    * Pip installations
        ```
        pip install matplotlib && numpy==1.16.6 && opencv-python==4.2.0.32
        ```
- Setup python 3.12 environment:
    * Create and activate conda environment
        ```
        conda create --name myenv2 python==3.12
        conda activate myenv2
        ```
    * Pip installations
        ```
        pip install matplotlib && numpy && opencv-python && mediapipe && pillow && torch && ultralytics
        ```

### NAOqi SDK
The NAOqi python SDK is available from:  
https://aldebaran.com/en/support/kb/nao6/downloads/nao6-software-downloads/  
- Once downloaded unzip the file in the desired location.
- Copy the path to the lib folder within this directory
- Locate the config.py in pepper_pipeline folder
- Replace the NAOQI_PATH with your path

Further documentation and guidance:  
http://doc.aldebaran.com/2-8/dev/python/install_guide.html  

---
## Running from terminal

---
## Running from .bat file