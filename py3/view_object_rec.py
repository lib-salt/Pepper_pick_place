import cv2
import numpy as np
import mediapipe as mp
import matplotlib as plt

# Path to mediapipe model
model_path = r"C:\Users\25276034.EDGEHILL\OneDrive - Edge Hill University\Year 3\Final Project\code\py3\efficientdet_lite0.tflite"

# Set up mediapipe model
BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
objectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Objects to detect
ALLOWED_OBJECTS = {'bottle', 'cup', 'remote'}

options = objectDetectorOptions(
    base_options = BaseOptions(model_asset_path=model_path),
    running_mode = VisionRunningMode.IMAGE,
    max_results=5,
    score_threshold=0.5,
)

detector = ObjectDetector.create_from_options(options)

def process_frame(frame):
    try:
        if frame is None:
            print("Error: Received empty frame.")
            return None
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        object_center = None

        for detection in result.detections:
            category = detection.categories[0].category_name

            if category in ALLOWED_OBJECTS:
                bbox = detection.bounding_box
                x, y, w, h = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, category, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Calculate object center
                x_cen = x + w // 2
                y_cen = y + h // 2
                object_center = (x_cen, y_cen)

        cv2.imshow('Pepper Camera Feed', frame)
        cv2.waitKey(1) 

        return object_center
