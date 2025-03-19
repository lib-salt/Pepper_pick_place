@echo off
REM Switch to the external drive
E:

REM Start the Python 2.7 script in a new process
echo Starting main.py in Python 2.7 environment...
start "Python27_Script" cmd /c "call E:\miniconda\Scripts\conda init cmd.exe && E:\miniconda\Scripts\activate.bat activate E:\miniconda\envs\py27 && python "C:\Users\libby\OneDrive - Edge Hill University\Year 3\Final Project\code\py27\main.py""

REM Start the Python 3 script 
echo Starting stream.py in Pepper environment...
E:\anaconda\Scripts\conda init cmd.exe && E:\anaconda\Scripts\activate.bat activate E:\anaconda\envs\pepper_env && python "C:\Users\libby\OneDrive - Edge Hill University\Year 3\Final Project\code\py3\stream.py""

echo running code
