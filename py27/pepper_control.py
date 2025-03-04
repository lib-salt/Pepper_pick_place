import math
import time
import sys
sys.path.append(r"C:\Users\25276034\OneDrive - Edge Hill University\pynaoqi-python2.7-2.5.5.5-win32-vs2013\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
#sys.path.append(r"D:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy  

# Check if Pepper is actively moving
def is_moving(motion_proxy):
    status = motion_proxy.getMoveStatus()
    return status[0] == "moving"

def move_towards_object(motion_proxy, angle):
    try:
        turn_radians = math.radians(angle)

        # Turn Pepper head to focus on the object
        motion_proxy.setAngles(["HeadYaw"], [turn_radians], 0.1)

        # Rotate Pepper to object
        motion_proxy.moveTo(0, 0, turn_radians)

        # Move a fixed distance
        motion_proxy.moveTo(0.5, 0, 0)

        while is_moving(motion_proxy):
            time.sleep(0.1)  # Wait for Pepper to finish moving

        
        print("Movement completed, ready for new command.")

    except Exception as e:
        print("Error while moving Pepper: ", e)

def move_arm(motion_proxy, height_angle):
    try:
        motion_proxy.setAngles("RShoulderPitch", height_angle, 0.5)
        
    except Exception as e:
        print("Error while moving right arm: ", e)
