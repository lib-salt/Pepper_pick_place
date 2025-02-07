import cv2
import numpy as np
from object_detector import ObjectDetector
from naoqi import ALProxy 

# Connect to Pepper
ip_address = 192.168.x.x
port = 9559

def get_video_feed(ip_address):
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

                detector.detect_objects_in_frame(image_np)

            else:
                print("Failed to get frame")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Unsubscribe and cleanup
        if 'cam_name' in locals():
            video_service.unsubscribe(cam_name)


detector = ObjectDetector()
detector.detect_objects()