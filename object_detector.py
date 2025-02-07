import os
import cv2
import numpy as np
import mediapipe as mp
from naoqi import ALProxy 

class ObjectDetector():
    def __init__(self):
        # Load the model
        self.model_path = os.path.join(os.path.dirname(__file__), 'efficientdet_lite0.tflite') 

        # Set up mediapipe model options
        self.BaseOptions = mp.tasks.BaseOptions
        self.ObjectDetector = mp.tasks.vision.ObjectDetector
        self.ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
        self.VisionRunningMode = mp.tasks.vision.RunningMode

        # List of objects to detect
        self.ALLOWED_OBJECTS = {'bottle', 'spoon', 'remote'} 

        # Set up Object Detector
        self.options = self.ObjectDetectorOptions(
            base_options=self.BaseOptions(model_asset_path=self.model_path),
            running_mode=self.VisionRunningMode.IMAGE,
            max_results=5,
            score_threshold=0.5,
        )

    def detect_objects(self):
        # Open webcam
        cap = cv2.VideoCapture(0)

        with self.ObjectDetector.create_from_options(self.options) as detector:
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
                    if category in self.ALLOWED_OBJECTS:
                        bbox = detection.bounding_box
                        x, y, w, h = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)

                        center = (x + w // 2, y + h // 2)
                        size = (w, h)
                        angle = 0  
                        
                        rotated_rect = ((center[0], center[1]), (size[0], size[1]), angle)
                        box = cv2.boxPoints(rotated_rect)  
                        box =  np.int0(box)   

                        cv2.polylines(frame, [box], isClosed=True, color=(0, 255, 0), thickness=2)

                        # Draw label text
                        label = detection.categories[0].category_name
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Display the frame
                cv2.imshow('Object Detection', frame)

                # Break on 'Esc' key
                if cv2.waitKey(5) & 0xFF == 27:
                    break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()

    def get_video_feed(ip_address):
        port = 9559
        global frame_buffer
        try:
            # Create a proxy to ALVideoDevice
            video_service = ALProxy("ALVideoDevice", ip_address, port)

            resolution = 2  
            color_space = 11  
            fps = 30
            name = "pepper_camera"
            cam_name = video_service.subscribeCamera(name, 0, resolution, color_space, fps)

            while True:
                # Get image remotely
                frame = video_service.getImageRemote(cam_name)
                if frame is not None:
                    image_width = frame[0]
                    image_height = frame[1]
                    array = frame[6]
                    image_np = cv2.cvtColor(np.fromstring(array, dtype=np.uint8).reshape((image_height, image_width, 3)), cv2.COLOR_BGR2RGB)

                    detect_objects()

                else:
                    print("Failed to get frame")
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Unsubscribe and cleanup
            if 'cam_name' in locals():
                video_service.unsubscribe(cam_name)

