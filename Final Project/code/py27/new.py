import numpy as np
import cv2
import signal
import socket
import struct
import sys
sys.path.append(r"D:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy  

# Pepper IP address and port
ip = '192.168.245.2'
port = 9559

# IP and port of external computer
server_ip = "" 

video_proxy = ALProxy("ALVideoDevice", ip, port)

# Subscribe to Pepper camera 
sub_name = "myCam"
camera_index = 0

video_proxy.subscribeCameras(sub_name)
video_proxy.setResolution(sub_name, 2)
video_proxy.setFrameRate(sub_name, 30)
video_proxy.setColorSpace(sub_name, 11)

# Method to close on command
def cleanup(signal, frame):
    print("\nStopping video stream...")
    video_proxy.unsubscribe(sub_name)  # Unsubscribe from camera
    sock.close()  # Close socket
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

# Set up socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Streaming video from robot...")

try:
    while True:
        frame = video_proxy.getDirectRawImageRemote(sub_name)

        if frame is None:
            continue

        width = frame[0]
        height = frame[1]
        raw_image = frame[6]

        frame = np.frombuffer(raw_image, dtype=np.uint8).reshape((height, width, 3))
        frame = cv2.resize(frame, (640, 480))

        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

        # Send frame
        sock.sendto(struct.pack("L", len(buffer)) + buffer.tobytes(), (server_ip, 8089))

        # Release frame to prevent memory buildup
        video_proxy.releaseDirectRawImage(sub_name)

except Exception as e:
    print("Error:", e)
    cleanup(None, None)

