import socket
import cv2
import numpy as np
import pickle
import struct
import mediapipe as mp

class ObjectDetector:
    def __init__(self):
        self.model_path = 'efficientdet_lite0.tflite'

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

    def start_video_stream(self):
        server_ip = '192.168.x.x'  # Pepper's IP
        server_port = 12345 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((server_ip, server_port))
        sock.listen(5)

        print("Waiting for connection...")
        client_socket, client_address = sock.accept()
        print(f"Connection established with {client_address}")

        while True:
            # Receive frame from Pepper
            frame_data = b""
            while len(frame_data) < struct.calcsize("L"):
                frame_data += client_socket.recv(4096)
            frame_size = struct.unpack("L", frame_data[:struct.calcsize("L")])[0]
            frame_data = frame_data[struct.calcsize("L"):]

            while len(frame_data) < frame_size:
                frame_data += client_socket.recv(4096)

            # Apply object recognition
            frame = pickle.loads(frame_data)
            processed_frame = self.detect_objects(frame)

            # Display frame
            cv2.imshow('Object Detection', processed_frame)

            if cv2.waitKey(5) & 0xFF == 27:
                break

        client_socket.close()

# Run the video stream
detector = ObjectDetector()
detector.start_video_stream()
