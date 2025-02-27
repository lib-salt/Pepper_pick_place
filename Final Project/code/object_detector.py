import cv2
import numpy as np
import socket
import struct
import pickle
import threading
import sys
sys.path.append(r"D:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy

class videoStream(threading.Thread):
    def __init__(self, ip_address, server_ip, server_port):
        threading.Thread.__init__(self)
        self.server_ip = server_ip
        self.server_port = server_port
        self.ip_address = ip_address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.123

    def run(self):
        port = 9559
        try:
            # Create a proxy to ALVideoDevice
            video_service = ALProxy("ALVideoDevice", self.ip_address, port)
            resolution = 2  # You may increase this for better quality
            color_space = 11
            fps = 30
            name = "pepper_camera"
            cam_name = video_service.subscribeCamera(name, 0, resolution, color_space, fps)

            while True:
                frame = video_service.getImageRemote(cam_name)
                if frame is not None:
                    image_width = frame[0]
                    image_height = frame[1]
                    array = frame[6]

                    try:
                        image_np = np.frombuffer(array, dtype=np.uint8).reshape((image_height, image_width, 3))  # BGR format
                        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)  # Convert to RGB format

                        # Serialize and send the frame size first
                        frame_data = pickle.dumps(image_rgb)
                        frame_size = len(frame_data)
                        self.sock.sendall(struct.pack("L", frame_size) + frame_data)
                    except Exception as e:
                        print("Error processing frame: ", e)

        except Exception as e:
            print("Error in VideoStream: ", e)
        finally:
            video_service.unsubscribe(cam_name)
            self.sock.close()

if __name__ == "__main__":
    # Run the video sender
    video_sender = videoStream(ip_address="192.168.245.57", server_ip="127.0.0.1", server_port=12345)
    video_sender.start() 
    video_sender.join()


