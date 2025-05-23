import os
import cv2
import logging
from ultralytics import YOLO

# Disable YOLOv8 logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Load YOLOv8 model
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "yolov8n.pt")
model = YOLO(model_path)

# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Run YOLOv8 detection
    results = model(frame)

    # Draw bounding boxes
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get bounding box coordinates
            confidence = float(box.conf[0])  # Get confidence score
            object_cat = result.names[int(box.cls[0])]  # Get object category

            # Only show allowed objects
            if object_cat in {'bottle', 'cup', 'remote'}:
                score_percent = int(confidence * 100)
                label = f"{object_cat} {score_percent}%"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Display frame
    cv2.imshow('YOLOv8 Object Detection', frame)

    # Break on 'Esc' key
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
