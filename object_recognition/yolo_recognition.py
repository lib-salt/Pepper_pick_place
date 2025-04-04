import cv2
import torch
from ultralytics import YOLO
import sys
import os
import logging

os.environ['YOLO_VERBOSE'] = 'False'

logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Load the YOLOv8 model
model_path = r"C:\Users\25276034.EDGEHILL\OneDrive - Edge Hill University\Year 3\Final Project\code\yolov8n.pt"
model = YOLO(model_path, verbose=False)  # Load YOLOv8 model

model.verbose = False

# Objects to detect
ALLOWED_OBJECTS = {'bottle', 'cup', 'remote'}

def process_frame(frame):
    try:
        if frame is None:
            print("Error: Received empty frame.")
            return [], []

        # Run YOLOv8 detection on the frame
        results = model(frame)

        obj = None
        object_center = None

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get bounding box coordinates
                confidence = float(box.conf[0])  # Get confidence score
                label = result.names[int(box.cls[0])]  # Get label

                # Only process allowed objects
                if label in ALLOWED_OBJECTS and confidence > 0.5:
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Draw confidence label
                    cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Calculate object center
                    x_cen = (x1 + x2) // 2
                    y_cen = (y1 + y2) // 2
                    object_center = (x_cen, y_cen)
                    obj = label

        # Display the frame with bounding boxes
        cv2.imshow('YOLOv8 Object Detection', frame)
        cv2.waitKey(1)  # Needed for imshow to work

        return object_center, obj

    except Exception as e:
        print(f"Error processing frame: {e}")
        return None
