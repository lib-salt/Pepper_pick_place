import cv2
import numpy as np
import mediapipe as mp

# Path to mediapipe model
model_path = r'c:\Users\25276034\OneDrive - Edge Hill University\Year 3\Final Project\code\efficientdet_lite0.tflite'

# Set up mediapipe model
BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
objectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Objects to detect
ALLOWED_OBJECTS = {'bottle', 'spoon', 'remote'}

options = objectDetectorOptions(
    base_options = BaseOptions(model_asset_path=model_path),
    running_mode = VisionRunningMode.IMAGE,
    max_results=5,
    score_threshold=0.5,
)

detector = ObjectDetector.create_from_options(options)

def process_frame(frame_data):
    try:
        # Decode the frame received from server
        np_frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
        if frame is None:
            print("Error: Frame decoding failed.")
            return
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        for detection in result.detections:
            category = detection.categories[0].category_name
            if category in ALLOWED_OBJECTS:
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

        cv2.imshow('Pepper Camera Feed', frame)
        cv2.waitKey(1) 

    except Exception as e:
        print(f"Error processing frame: {e}")





