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
