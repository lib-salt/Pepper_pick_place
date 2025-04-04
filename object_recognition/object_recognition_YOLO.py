import cv2
import torch
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO(r'c:\Users\Libby\OneDrive - Edge Hill University\Year 3\Final Project\code\yolov8n.pt')

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
            label = result.names[int(box.cls[0])]  # Get label

            # Only show allowed objects
            if label in {'bottle', 'cup', 'remote'}:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display frame
    cv2.imshow('YOLOv8 Object Detection', frame)

    # Break on 'Esc' key
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
