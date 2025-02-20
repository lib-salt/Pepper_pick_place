import numpy as np
import cv2
import threading
import signal
import socket
import struct
import time 
import sys
sys.path.append(r"D:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy  

# Pepper IP address and port
ip = '192.168.245.2'
port = 9559

frame = None

def get_video_feed():
    global video_service, cam_name, frame

    try:
        # Create a proxy to ALVideoDevice
        video_service = ALProxy("ALVideoDevice", ip, port)
        resolution = 2  
        color_space = 11
        fps = 30
        name = "pepper_camera"
        cam_name = video_service.subscribeCamera(name, 0, resolution, color_space, fps)
        if not cam_name:
            print("Error: Failed to subscribe to Pepper's camera.")
            return
        
        print("Camera subscription successful: ", cam_name)

        while True:
            new_frame = video_service.getImageRemote(cam_name)
            if new_frame is not None:
                frame = new_frame
            else:
                print("Failed to get frame")
                video_service.unsubscribe(cam_name)
                cam_name = None 
            # time.sleep(0.1)

    except Exception as e:
        print("Error processing frame:", e)
        

    finally:
        if video_service and cam_name:
            video_service.unsubscribe(cam_name)
            
    
def stream_feed():
    global frame

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('127.0.0.1', 12345))

    while True:
        if frame is not None:
            try:
                # Process the frame
                image_width = frame[0]
                image_height = frame[1]
                array = frame[6]
                image_np = np.frombuffer(array, dtype=np.uint8).reshape((image_height, image_width, 3))
                image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

                # frame_data = pickle.dumps(image_rgb)
                # frame_size = len(frame_data)
                # sock.sendall(struct.pack("L", frame_size) + frame_data)

                _, buffer = cv2.imencode('.jpg', image_rgb)
                frame_data = buffer.tobytes()
                frame_size = struct.pack("!I", len(frame_data))
                sock.sendall(frame_size + frame_data)


            except Exception as e:
                print("Error sending frame: ", e)
        else:
            time.sleep(0.1)

if __name__ == '__main__':
    video_thread = threading.Thread(target=get_video_feed)
    video_thread.daemon = True
    video_thread.start()

    stream_feed()

def cleanup(signum, frame):
    global video_service, cam_name
    if video_service and cam_name:
        print("\nUnsubscribing from camera and shutting down...")
        video_service.unsubscribe(cam_name)
    exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)
