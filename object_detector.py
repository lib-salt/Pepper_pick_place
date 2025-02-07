import cv2
import numpy as np
import socket
import struct
import pickle
from naoqi import ALProxy

server_ip = '192.168.x.x'  
server_port = 12345 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, server_port))

def get_video_feed(ip_address):
    port = 9559
    try:
        # Create a proxy to ALVideoDevice
        video_service = ALProxy("ALVideoDevice", ip_address, port)

        resolution = 2 
        color_space = 11  
        fps = 30
        name = "pepper_camera"
        cam_name = video_service.subscribeCamera(name, 0, resolution, color_space, fps)

        while True:
            # Get image remotely
            frame = video_service.getImageRemote(cam_name)
            if frame is not None:
                image_width = frame[0]
                image_height = frame[1]
                array = frame[6]
                image_np = cv2.cvtColor(np.fromstring(array, dtype=np.uint8).reshape((image_height, image_width, 3)), cv2.COLOR_BGR2RGB)

                # Send the frame to the laptop
                frame_data = pickle.dumps(image_np)
                sock.sendall(struct.pack("L", len(frame_data)) + frame_data)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cam_name' in locals():
            video_service.unsubscribe(cam_name)
        sock.close()

# Start sending frames
get_video_feed('192.168.x.x')  

