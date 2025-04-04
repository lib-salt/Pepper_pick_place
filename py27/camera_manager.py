import numpy as np
import cv2
import struct
import socket
import time
import threading
from config import *
from utils import logger

class CameraManager:
    def __init__(self, video_proxy):
        # Initialise camera manager
        self.video_proxy = video_proxy
        self.depth_cam = None
        self.image_cam = None
        self.video_sock = None
        self.initialised = False
        self.shutting_down = False

    def initialise(self):
        # Initialise camera subscriptions and socket
        try:
            self.depth_cam = self.video_proxy.subscribeCamera(
                "pepper_depth_camera",
                DEPTH_CAM_ID,
                DEPTH_CAM_RES,
                DEPTH_CAM_COLOUR,
                DEPTH_CAM_FPS
            )

            self.image_cam = self.video_proxy.subscribeCamera(
                "pepper_image_camera",
                TOP_CAM_ID,
                TOP_CAM_RES,
                TOP_CAM_COLOUR,
                TOP_CAM_FPS
            )

            if not self.image_cam:
                logger.error("Failed to subscribe to Pepper's top camera.")
                return False
            
            logger.info("Camera subscription successful")

            # Setup socket for video stream
            self.video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            logger.info("Streaming video socket initialised")

            self.initialised = True
            return True
        
        except Exception as e:
            logger.error("Camera initialisation error: {}".format(e))
            return False
        
    def cleanup(self):
        # Unsubscribe from cameras and close sockets
        self.shutting_down = True
        try:
            if self.image_cam:
                self.video_proxy.unsubscribe(self.image_cam)
            if self.depth_cam:
                self.video_proxy.unsubscribe(self.depth_cam)
            if self.video_sock:
                self.video_sock.close()
            logger.info("Unsubscribed from Cameras")

        except Exception as e:
            logger.error("Error during camera cleanup: {}".format(e))

    def get_video_frame(self):
        # Get frame from top camera
        if not self.initialised or not self.image_cam:
            logger.error("Camera not initialised")
            return None
        
        try:
            frame = self.video_proxy.getImageRemote(self.image_cam)

            if frame is None:
                if not self.shutting_down:
                    logger.warning("Received empty frame from camera")
                return None
            
            width = frame[0]
            height = frame[1]
            raw_image = frame[6]

            image_np = np.frombuffer(raw_image, dtype=np.uint8).reshape((height, width, 3))
            image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

            # Release the image to prevent memory buildup
            self.video_proxy.releaseImage(self.image_cam)

            return image_rgb
        
        except Exception as e:
            logger.error("Error getting video frame: {}".format(e))
            return None
        
    def get_depth_image(self):
        # Get depth Image
        if not self.initialised or not self.depth_cam:
            logger.error("Camera not initialised or depth camera not available")
            return None
        
        try:
            depth_frame = self.video_proxy.getImageRemote(self.depth_cam)

            if depth_frame is None:
                logger.warning("Recieved empty depth frame")
                return None
            
            width = depth_frame[0]
            height = depth_frame[1]
            raw_depth_image = depth_frame[6]

            depth_image = np.frombuffer(raw_depth_image, dtype=np.uint16).reshape(height, width)

            # Apply box filter to reduce noise
            depth_smoothed = cv2.boxFilter(depth_image, -1, (5, 5))

            # Switch back to top camera for video feed
            self.video_proxy.setActiveCamera(0)

            return depth_smoothed, width, height
        
        except Exception as e:
            logger.error("Error getting depth image: {}".format(e))
            return None
        
    def stream_video(self, server_ip, port):
        # Stream video to socket server
        if not self.initialised or not self.video_sock:
            logger.error("Camera not initialised or socket not availaible")
            return
        
        try:
            while not self.shutting_down:
                frame = self.get_video_frame()

                if frame is not None:
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])

                    # Send frame
                    self.video_sock.sendto(
                        struct.pack("L", len(buffer)) + buffer.tobytes(),
                        (server_ip, port)
                    )

                    # Small delay to avoid overload
                    time.sleep(0.003)

        except Exception as e:
            logger.error("Error streaming video: {}".format(e))

    def start_video_stream(self, server_ip, port):
        # Start video streaming in a separate thread
        stream_thread = threading.Thread(
            target=self.stream_video,
            args=(server_ip, port),
        )
        stream_thread.setDaemon(True)
        stream_thread.start()
        return stream_thread
