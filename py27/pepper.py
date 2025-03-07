import numpy as np
import cv2
import signal
import socket
import struct
import threading
import sys
import time
sys.path.append(r"E:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy, ALBroker  
# from pepper_control import *

# Pepper IP address and port
ip = '192.168.244.116'
port = 9559

# Setup Pepper proxies
broker = ALBroker("pythonBroker", "0.0.0.0", 0, ip, port)
motion_proxy = ALProxy("ALMotion", ip, port)
video_proxy = ALProxy("ALVideoDevice", ip, port)

# Subscribe to Pepper cameras 
depth_cam = video_proxy.subscribeCamera("pepper_depth_camera", 2, 1, 19, 20)
image_cam = video_proxy.subscribeCamera("pepper_image_camera", 0, 1, 11, 30)

if not depth_cam or not image_cam:
    print("Error: Failed to subscribe to Pepper's camera.")
else:
    print("Camera subscription successful: pepper_depth_camera, pepper_image_camera")

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
    video_proxy.unsubscribe(image_cam)  
    video_proxy.unsubscribe(depth_cam)  
    print("\nUnsubscribing from camera and shutting down...")
    video_sock.close()
    location_sock.close() 
    motion_proxy.stopMove()
    time.sleep(0.5)
    broker.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)



# Fuction to get video feed from Pepper
def get_feed():
    try:
        while True:
            # Get the frame from the robot
            new_frame = video_proxy.getImageRemote(image_cam)

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
                video_proxy.releaseImage(image_cam)

            continue

    except Exception as e:
        print("Error:", e)
        cleanup(None, None)

def get_depth(x, y):
    video_proxy.setResolution(depth_cam, 1)
    current_resolution = video_proxy.getResolution(depth_cam)
    print("Current Resolution:", current_resolution)
    deth_frame = video_proxy.getImageRemote(depth_cam)

    if deth_frame is not None: 
        width = deth_frame[0]
        height = deth_frame[1]
        print("Received depth image resolution: {}x{}".format(width, height))
        raw_depth_image = deth_frame[6] 

        expected_size = width * height * 3 * 4  # 3 floats per voxel, 4 bytes per float
        if len(raw_depth_image) != expected_size:
            print("Error: Raw XYZ data size", len(raw_depth_image), "doesn't match expected size", expected_size)
            return None
        
        xyz_data = np.frombuffer(raw_depth_image, dtype=np.float32).reshape((height, width, 3))

        x_int = int(x)
        y_int = int(y)

        if x_int < 0 or x_int >= width or y_int < 0 or y_int >= height:
            print("Error: ({}, {}) is out of bounds. Image size: {}x{}".format(x_int, y_int, width, height))
            return None

        depth = xyz_data[y_int, x_int, 2]  # z corresponds to the depth value
        return depth
    else:
        print("Error: Failed to get XYZ image.")
        return None

# Move toward object
def move_towards():
    try:
        while True:
            # Receive co-ordinate data
            data, _ = location_sock.recvfrom(1024)
            if data:
                coords = data.decode().split(',')
                x_cen = float(coords[0])
                y_cen = float(coords[1])

                depth = get_depth(x_cen, y_cen)
                print("Co-ordinates: ", x_cen, y_cen, depth)

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
