import numpy as np
import cv2
import signal
import socket
import struct
import threading
import sys
import time
sys.path.append(r"E:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
# sys.path.append(r"C:\Users\25276034\OneDrive - Edge Hill University\pynaoqi-python2.7-2.5.5.5-win32-vs2013\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
# sys.path.append(r"D:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy, ALBroker  
from pepper_control import *

# Pepper IP address and port
ip = '192.168.245.47'
port = 9559

# Setup Pepper proxies
broker = ALBroker("pythonBroker", "0.0.0.0", 0, ip, port)
motion_proxy = ALProxy("ALMotion", ip, port)
video_proxy = ALProxy("ALVideoDevice", ip, port)
# autonomous_life_proxy = ALProxy("ALAutonomousLife", ip, port)
# autonomous_life_proxy.setState("disabled")
# print("Autonomous life disabled.")

# Subscribe to Pepper camera 
resolution = 1  
color_space = 11
fps = 30
name = "pepper_camera"
cam_name = video_proxy.subscribeCamera(name, 0, resolution, color_space, fps)
if not cam_name:
    print("Error: Failed to subscribe to Pepper's camera.")
else:
    print("Camera subscription successful: ", cam_name)

# IP and port of external computer
server_ip = "127.0.0.1" 

# Socket set up
video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Stream video feed
print("Streaming video from robot...")
location_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Listen for object location
location_sock.bind((server_ip, 9090))

# Method to close cleanly on command
def cleanup(signal, frame):
    print("\nStopping video stream...")
    video_proxy.unsubscribe(cam_name)  
    print("\nUnsubscribing from camera and shutting down...")
    video_sock.close()
    location_sock.close() 
    motion_proxy.stopMove()
    time.sleep(0.5)
    # autonomous_life_proxy.setState("solitary") 
    broker.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# Fuction to get video feed from Pepper
def get_feed():
    try:
        while True:
            # Get the frame from the robot
            new_frame = video_proxy.getImageRemote(cam_name)

            if new_frame is not None:
                # Extract width, height, and raw image data
                width = new_frame[0]
                height = new_frame[1]
                raw_image = new_frame[6]
                image_np = np.frombuffer(raw_image, dtype=np.uint8).reshape((height, width, 3))
                image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    
                # Encode as JPEG
                _, buffer = cv2.imencode('.jpg', image_rgb, [cv2.IMWRITE_JPEG_QUALITY, 60])

                # Send frame
                video_sock.sendto(struct.pack("L", len(buffer)) + buffer.tobytes(), (server_ip, 8089))

                # Release the frame to prevent memory buildup
                video_proxy.releaseImage(cam_name)

            continue

    except Exception as e:
        print("Error:", e)
        cleanup(None, None)


# Move toward object
def move_towards():
    try:
        while True:
            # Receive data (this should be the angle)
            data, _ = location_sock.recvfrom(1024)
            if data:
                angle = float(data.decode())
                print("Received angle: ", angle)  # Debugging line to print received angle
                move_towards_object(motion_proxy, angle)
                move_arm(motion_proxy, angle)
            else:
                print("No data received.")
    except Exception as e:
            print("Error receiving data: ", e)
            time.sleep(0.1)

# Threads 
video_thread = threading.Thread(target=get_feed)
location_thread = threading.Thread(target=move_towards)

video_thread.setDaemon(True)
location_thread.setDaemon(True)

video_thread.start()
location_thread.start()

while True:
    try:
        time.sleep(1)  
    except KeyboardInterrupt:
        cleanup(None, None)
