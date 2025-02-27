import socket
import cv2
import queue
import numpy as np
import pickle
import struct
import threading
import mediapipe as mp

class ObjectDetector:
    def __init__(self):
        self.model_path = r'c:\Users\25276034\OneDrive - Edge Hill University\Year 3\Final Project\code\efficientdet_lite0.tflite'

        self.BaseOptions = mp.tasks.BaseOptions
        self.ObjectDetector = mp.tasks.vision.ObjectDetector
        self.ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
        self.VisionRunningMode = mp.tasks.vision.RunningMode

        self.ALLOWED_OBJECTS = {'bottle', 'spoon', 'remote'}

        self.options = self.ObjectDetectorOptions(
            base_options=self.BaseOptions(model_asset_path=self.model_path),
            running_mode=self.VisionRunningMode.IMAGE,
            max_results=5,
            score_threshold=0.5,
        )

        self.detector = self.ObjectDetector.create_from_options(self.options)


    def detect_objects(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        result = self.detector.detect(mp_image)

        # Draw rotated bounding box
        for detection in result.detections:
            category = detection.categories[0].category_name
            if category in self.ALLOWED_OBJECTS:
                bbox = detection.bounding_box
                x, y, w, h = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)

                center = (x + w // 2, y + h // 2)
                size = (w, h)
                angle = 0

                rotated_rect = ((center[0], center[1]), (size[0], size[1]), angle)
                box = cv2.boxPoints(rotated_rect)
                box = np.int0(box)

                # Draw bounding box and label
                cv2.polylines(frame, [box], isClosed=True, color=(0, 255, 0), thickness=2)
                label = detection.categories[0].category_name
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return frame

    def process_and_display(self, frame):
        # Process the frame with object detection
        processed_frame = self.detect_objects(frame)
        
        # Display frame (object detection result)
        cv2.imshow('Object Detection', processed_frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            return False
        return True
    
class FrameProcessor(threading.Thread):
    def __init__(self, frame_queue, detector):
        threading.Thread.__init__(self)
        self.frame_queue = frame_queue
        self.detector = detector

    def run(self):
        while True:
            # Get the next frame from the queue
            frame = self.frame_queue.get()

            if frame is None:
                break  # Exit condition

            # Process and display the frame
            if not self.detector.process_and_display(frame):
                break

        cv2.destroyAllWindows()

class videoReceiver(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        self.frame_queue = queue.Queue()  # Queue to hold frames for processing

    def run(self):
        try:
            while True:
                # Receive the frame size first
                frame_data = b""
                while len(frame_data) < struct.calcsize("L"):
                    frame_data += self.sock.recv(4096)

                if len(frame_data) >= struct.calcsize("L"):
                    frame_size = struct.unpack("L", frame_data[:struct.calcsize("L")])[0]
                    frame_data = frame_data[struct.calcsize("L"):]

                    while len(frame_data) < frame_size:
                        frame_data += self.sock.recv(4096)

                    # Deserialize the frame and add it to the queue
                    frame = pickle.loads(frame_data,encoding='latin1')
                    self.frame_queue.put(frame)

        except Exception as e:
            print("Error in VideoReceiver:", e)
        finally:
            self.sock.close()

def main():
    server_ip = '127.0.0.1'  # laptop IP
    server_port = 12345 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((server_ip, server_port))
    sock.listen(5)
    print("Waiting for connection...")

    client_socket, client_address = sock.accept()
    print(f"Connection established with {client_address}")

    detector = ObjectDetector()

    # Set up the frame processor to handle the received frames
    video_receiver = videoReceiver(client_socket)
    video_receiver.start()

    # Start the frame processor to handle the received frames
    frame_processor = FrameProcessor(video_receiver.frame_queue, detector)
    frame_processor.start()

    # Join threads to make sure the program waits for them to finish
    video_receiver.join()
    frame_processor.join()

if __name__ == "__main__":
    main()
