import numpy as np
import cv2
import signal
import sys
import time
sys.path.append(r"E:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy, ALBroker

ip = '192.168.244.198'
port = 9559
broker = ALBroker("pythonBroker", "0.0.0.0", 0, ip, port)
video_proxy = ALProxy("ALVideoDevice", ip, port)
awareness_proxy = ALProxy("ALBasicAwareness", ip, port)

awareness_proxy.pauseAwareness()

depth_cam = video_proxy.subscribeCamera("pepper_depth_camera", 3, 15, 11, 15)
image_cam = video_proxy.subscribeCamera("pepper_image_camera", 0, 1, 11, 30)

TOP_CAMERA = 0
LEFT_EYE_CAMERA = 3

# Top Camera Settings
RESOLUTION_TOP = 1    # 320x240
COLOR_SPACE = 11      # RGB
FPS_TOP = 30          # Frame rate

# Left Eye Camera Settings
RESOLUTION_LEFT = 15  # 256x256
FPS_LEFT = 15  

def cleanup(signal, frame):
    print("\nStopping video stream...")
    video_proxy.unsubscribe(image_cam)  
    video_proxy.unsubscribe(depth_cam) 
    print("\nUnsubscribing from camera and shutting down...")
    awareness_proxy.resumeAwareness()
    time.sleep(0.5)
    broker.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def capture_frame(video_proxy, camera_id, resolution, fps):
    subscriber_id = video_proxy.subscribeCamera("camera_subscriber", camera_id, resolution, COLOR_SPACE, fps)
    
    img = video_proxy.getImageRemote(subscriber_id)
    video_proxy.unsubscribe(subscriber_id)
    
    if img is None:
        print("Failed to capture image")
        return None
    
    width, height, array = img[0], img[1], np.frombuffer(img[6], dtype=np.uint8)
    frame = array.reshape((height, width, 3))  # Convert to OpenCV format
    
    return frame

# Prepare to collect calibration images
pattern_size = (6, 7)  # Adjust based on your checkerboard
image_count = 0
required_images = 10  # Number of images you want for calibration

# Capture images from both cameras
while image_count < required_images:
    try:
        frame_top = capture_frame(video_proxy, TOP_CAMERA, RESOLUTION_TOP, FPS_TOP)
        frame_stereo = capture_frame(video_proxy, LEFT_EYE_CAMERA, RESOLUTION_LEFT, FPS_LEFT)

        frame_left = frame_stereo[:, :frame_stereo.shape[1] // 2]

        # Convert to grayscale for corner detection
        gray_top = cv2.cvtColor(frame_top, cv2.COLOR_BGR2GRAY)
        gray_left = cv2.cvtColor(frame_left, cv2.COLOR_BGR2GRAY)

        # Find checkerboard corners
        found_top, corners_top = cv2.findChessboardCorners(gray_top, pattern_size, None)
        found_left, corners_left = cv2.findChessboardCorners(gray_left, pattern_size, None)

        if found_top and found_left:
            print("Checkerboard detected! Saving images ({}/{})".format(image_count + 1, required_images))

            cv2.imwrite("top_camera_{}.jpg".format(image_count + 1), frame_top)  # Save the plain image
            cv2.imwrite("left_eye_{}.jpg".format(image_count + 1), frame_left)  # Save the plain image

            image_count += 1

            cv2.putText(frame_top, "Checkerboard Detected (Top Camera)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame_left, "Checkerboard Detected (Left Eye)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the frames
        cv2.imshow("Top Camera", frame_top)
        cv2.imshow("Left Eye Camera", frame_left)

        key = cv2.waitKey(1)  # Use a small delay instead of 0 (non-blocking)

        if key == 27:  # ESC key to break the loop
            print("ESC key pressed. Exiting...")
            break

    except Exception as e:
        print("Error: ", e)
        cleanup(None, None)

# After capturing enough images, you can proceed with calibration
print("Calibration images captured successfully!")
