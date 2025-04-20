import os
import cv2
import numpy as np
import mediapipe as mp

# Load the model
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "efficientdet_lite0.tflite")

BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# List of objects to detect
ALLOWED_OBJECTS = {'bottle', 'cup', 'remote'} 

detections = []

# Set up Object Detector
options = ObjectDetectorOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    max_results=5,
    score_threshold=0.5,
)

# Open webcam
cap = cv2.VideoCapture(0)

with ObjectDetector.create_from_options(options) as detector:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

        result = detector.detect(mp_image)

        # Draw rotated bounding box
        for detection in result.detections:
            category = detection.categories[0].category_name
            if category in ALLOWED_OBJECTS:
                bbox = detection.bounding_box
                x, y, w, h = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Draw label text
                category_info = detection.categories[0]
                score_percent = int(category_info.score * 100)
                label = f"{category_info.category_name} {score_percent}%"
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Object Detection', frame)

        # Break on 'Esc' key
        if cv2.waitKey(5) & 0xFF == 27:
            break

# Release resources
cap.release()
cv2.destroyAllWindows()