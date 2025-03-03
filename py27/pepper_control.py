import math
import sys
sys.path.append(r"C:\Users\25276034\OneDrive - Edge Hill University\pynaoqi-python2.7-2.5.5.5-win32-vs2013\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
#sys.path.append(r"D:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy  

def move_towards_object(motion_proxy, angle):
    try:
        turn_radians = math.radians(angle)

        # Rotate Pepper to object
        motion_proxy.moveTo(0, 0, turn_radians)

        # Move a fixed distance
        motion_proxy.moveTo(0.5, 0, 0)

    except Exception as e:
        print("Error while moving Pepper: ", e)