import cv2
import numpy as np
import socket 
import threading
import struct
from view_object_rec import process_frame


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 8089))

latest_frame = None
lock = threading.Lock()

def get_frames():
    global latest_frame
    while True:
        try:
            data, addr = sock.recvfrom(65536)
            size = struct.unpack("L", data[:4])[0]
            frame_data = data[4:size+4]

            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)

            with lock:
                latest_frame = frame  
        except Exception as e:
            print(f"Error receiving frame: {e}")

def process_frames():
    global latest_frame
    while True:
        with lock:
            if latest_frame is not None:
                frame = latest_frame.copy()  

        if frame is not None:
            process_frame(frame)  

# Start threads for receiving and processing frames
receive_thread = threading.Thread(target=get_frames, daemon=True)
receive_thread.start()

process_thread = threading.Thread(target=process_frames, daemon=True)
process_thread.start()

print("Receiving and processing video...")

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

sock.close()
cv2.destroyAllWindows()
