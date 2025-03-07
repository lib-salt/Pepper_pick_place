import cv2
import numpy as np
import socket 
import threading
import struct
import time
import signal
from view_object_rec import process_frame

stop_event = threading.Event()

# Socket for live video feed
video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
video_sock.bind(('127.0.0.1', 8089))

# socket to send object loaction
location_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

latest_frame = None
lock = threading.Lock()

def get_frames():
    global latest_frame
    while True:
        try:
            data, _ = video_sock.recvfrom(65536)
            size = struct.unpack("L", data[:4])[0]
            frame_data = data[4:size+4]

            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)

            if frame is None or frame.size == 0:
                print("Error: Received empty frame.")
                continue

            with lock:
                latest_frame = frame  

        except Exception as e:
            print(f"Error receiving frame: {e}")

def process_frames():
    global latest_frame
    while not stop_event.is_set():
        frame = None
        with lock:
            if latest_frame is not None:
                frame = latest_frame.copy()
            else:
                print("No frame available for processing.")
                time.sleep(0.1)
                continue  

        object_center = process_frame(frame) 

        if object_center:
            x_cen, y_cen = object_center
            send_object_location(x_cen, y_cen)

        if frame is not None:
            try:
                process_frame(frame)
            except Exception as e:
                print(f"Error in process_frame: {e}") 


def send_object_location(x_cen, y_cen):
    try:
        data =  f"{x_cen},{y_cen}".encode() 
        location_sock.sendto(data, ("127.0.0.1", 9090))
    except Exception as e:
        print(f"Error sending object location: {e}")
 

# Start threads for receiving and processing frames
receive_thread = threading.Thread(target=get_frames, daemon=True)
receive_thread.start()

process_thread = threading.Thread(target=process_frames, daemon=True)
process_thread.start()

print("Receiving and processing video...")

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        print("Exiting... (q key pressed)")
        stop_event.set()  
        break

    if stop_event.is_set():
        break


receive_thread.join()
process_thread.join()

video_sock.close()
location_sock.close()
cv2.destroyAllWindows()
