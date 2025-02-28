import numpy as np
import cv2
import signal
import socket
import struct
import sys
sys.path.append(r"C:\Users\25276034\OneDrive - Edge Hill University\pynaoqi-python2.7-2.5.5.5-win32-vs2013\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
#sys.path.append(r"D:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy  

# Pepper IP address and port
ip = '192.168.245.40'
port = 9559

# IP and port of external computer
server_ip = "127.0.0.1" 

# Subscribe to Pepper camera 
video_proxy = ALProxy("ALVideoDevice", ip, port)
resolution = 1  
color_space = 11
fps = 30
name = "pepper_camera"
cam_name = video_proxy.subscribeCamera(name, 0, resolution, color_space, fps)
if not cam_name:
    print("Error: Failed to subscribe to Pepper's camera.")
else:
    print("Camera subscription successful: ", cam_name)

# Method to close on command
def cleanup(signal, frame):
    print("\nStopping video stream...")
    video_proxy.unsubscribe(cam_name)  
    print("\nUnsubscribing from camera and shutting down...")
    sock.close()  
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# Set up socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Streaming video from robot...")

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
            sock.sendto(struct.pack("L", len(buffer)) + buffer.tobytes(), (server_ip, 8089))

            # Release the frame to prevent memory buildup
            video_proxy.releaseImage(cam_name)

        continue

except Exception as e:
    print("Error:", e)
    cleanup(None, None)

