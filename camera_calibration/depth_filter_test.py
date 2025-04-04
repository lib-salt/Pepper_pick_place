import numpy as np
import cv2
import signal
import socket
import struct
import threading
import sys
import time
import math
sys.path.append(r"E:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy, ALBroker  


# Pepper IP address and port
ip = '192.168.244.207'
port = 9559

# Setup Pepper proxies
broker = ALBroker("pythonBroker", "0.0.0.0", 0, ip, port)
video_proxy = ALProxy("ALVideoDevice", ip, port)

# Subscribe to Pepper cameras 
depth_cam = video_proxy.subscribeCamera("pepper_depth_camera", 2, 10, 17, 15) 

# if not depth_cam or not image_cam:
if not depth_cam:
    print("Error: Failed to subscribe to Pepper's camera.")
else:
    print("Camera subscription successful: pepper_depth_camera")


# Method to close cleanly on command
def cleanup(signal, frame):
    print("\nStopping video stream...")
    video_proxy.unsubscribe(depth_cam) 
    print("\nUnsubscribing from camera and shutting down...")
    time.sleep(0.5)
    broker.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def smooth_image(depth_image):
    depth_smoothed = cv2.GaussianBlur(depth_image, (5, 5), 0)

    depth_smoothed = cv2.boxFilter(depth_image, -1, (5, 5))

    # depth_normalised = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
    # depth_normalised = np.uint8(depth_normalised)
    # depth_mean = cv2.fastNlMeansDenoising(depth_normalised, None, 10, 7, 21)
    # depth_smoothed = cv2.GaussianBlur(depth_mean, (5, 5), 0)

    # depth_smoothed = cv2.medianBlur(depth_smoothed, 5)

    # depth_normalised = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
    # depth_normalised = np.uint8(depth_normalised)
    # depth_smoothed = cv2.bilateralFilter(depth_normalised, 9, 75, 75)
    
    return depth_smoothed

def visulaise_depth_image(depth_image):
    # Normalise for better visulisation
    depth_normalised = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)

    depth_normalised = np.uint8(depth_normalised)

    # Display the image
    cv2.imshow("Depth Image", depth_normalised)
    cv2.waitKey(1)

# Fuction to get video feed from Pepper
def get_feed():
    try:
        while True:
            # Get the frame from the robot
            new_frame = video_proxy.getImageRemote(depth_cam)

            if new_frame is not None:
                # Extract width, height, and raw image data
                width = new_frame[0]
                height = new_frame[1]
                raw_image = new_frame[6]
                depth_image = np.frombuffer(raw_image, dtype=np.uint16).reshape((height, width))
  
                # Smooth the depth image to reduce noise
                depth_smoothed = smooth_image(depth_image)
                visulaise_depth_image(depth_smoothed)

                # Release the frame to prevent memory buildup
                video_proxy.releaseImage(depth_cam)

            continue

    except Exception as e:
        print("Error: ", e)
        cleanup(None, None)

feed_thread = threading.Thread(target=get_feed)
feed_thread.daemon = True
feed_thread.start()

while True:
    try:
        time.sleep(1)  
    except KeyboardInterrupt:
        cleanup(None, None)

