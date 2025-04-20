import cv2
from ultralytics import YOLO
import os
import logging

logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Load the YOLOv8 model
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "yolov8n.pt")
model = YOLO(model_path)

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
                object_cat = result.names[int(box.cls[0])]  # Get label

                # Only process allowed objects
                if object_cat in ALLOWED_OBJECTS and confidence > 0.5:
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Draw confidence label
                    score_percent = int(confidence * 100)
                    label = f"{object_cat} {score_percent}%"
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Calculate object center
                    x_cen = (x1 + x2) // 2
                    y_cen = (y1 + y2) // 2
                    object_center = (x_cen, y_cen)
                    obj = label

        # Display the frame with bounding boxes
        cv2.imshow('YOLOv8 Object Detection', frame)
        cv2.waitKey(1) 

        return object_center, obj

    except Exception as e:
        print(f"Error processing frame: {e}")
        return None
