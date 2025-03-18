import numpy as np
import cv2
import struct
import logging
import socket
import threading
from config import *
from utils import logger

class PepperCamera:
    def __init__(self, video_proxy, motion_proxy): # Memory proxy?

        # Initialise Proxies
        self.video_proxy = video_proxy
        self.motion_proxy = motion_proxy
        # self.memory_proxy = memory_proxy

        # Initialise cameras for Pepper
        self.depth_cam = None
        self.image_cam = None
        self.video_sock = None
        self.initialised = False

         # Camera parameters
        self.focal_length_mm = 1.756  # mm
        self.image_width = 320  # pixels (top camera)
        self.image_height = 240  # pixels (top camera)
        self.sensor_width_mm = 0.448  # mm
        self.sensor_height_mm = 0.336  # mm
        
        # Focal length in pixels
        self.f_x = self.focal_length_mm * self.image_width / self.sensor_width_mm
        self.f_y = self.f_x  # Assuming square pixels
        self.c_x = self.image_width / 2
        self.c_y = self.image_height / 2

        self.shutting_down = False

        # Load calibration data
        try: 
            from utils import load_calibration_data
            self.calibration_data = load_calibration_data(CALIBRATION_FILE)
            if self.calibration_data:
                self.R = self.calibration_data['R']
                self.T = self.calibration_data['T']
                self.camera_matrix_top = self.calibration_data['camera_matrix_top']
                self.camera_matrix_depth = self.calibration_data['camera_matrix_depth']
                logger.info("Calibration data loaded successfully")
            else:
                logger.warning("Error loading calibration data")
        except Exception as e:
            logger.error("Error while loading calibration data: {}".format(e))
            self.calibration_data = None
    
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
                "pepper_image_cam",
                TOP_CAM_ID,
                TOP_CAM_RES,
                TOP_CAM_COLOUR,
                TOP_CAM_FPS
            )

            if not self.image_cam:
                logger.error("Failed to subscribe to Pepper's top camera.")

            logger.info("Camera subscription successful")

            # Setup up socket for video streaming
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
            logger.info("Unsubscribes from Cameras")
        except Exception as e:
            logger.error("Error during camera cleanup: {}".format(e))

    def get_video_frame(self):
        # get frame from top camera
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

            # Release the frame to prevent memory buildup
            self.video_proxy.releaseImage(self.image_cam)

            return image_rgb
        
        except Exception as e:
            logger.error("Error getting video frame: {}".format(e))
            return None
        
    def get_depth_image(self): # x, y
        # Get depth data for a specific pixel coordinate
        if not self.initialised or not self.depth_cam:
            logger.error("Camera not initialised or depth camera not available")
            return None
        
        try:
            depth_frame = self.video_proxy.getImageRemote(self.depth_cam)

            if depth_frame is None:
                logger.warning("Received empty depth frame")
                return None
            
            width = depth_frame[0]
            height = depth_frame[1]
            raw_depth_image = depth_frame[6]

            depth_image = np.frombuffer(raw_depth_image, dtype=np.uint16).reshape((height, width))

            # Switch back to top camera for video feed
            self.video_proxy.setActiveCamera(0)

            return depth_image, width, height
        
        except Exception as e:
            logger.error("Error getting depth data: {}".format(e))
            return None
        
    def stream_video(self, server_ip, port):
        # Stream video to socket server
        if not self.initialised or not self.video_sock:
            logger.error("Camera not initialised or socket not available")
            return
        
        try:
            while True:
                frame = self.get_video_frame()

                if frame is not None:
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])

                    # Send frame 
                    self.video_sock.sendto(
                        struct.pack("L", len(buffer)) + buffer.tobytes(),
                        (server_ip, port)
                    )

        except Exception as e:
            logger.error("Error streaming video: {}".format(e))
        
    def map_pixel_to_depth(self, x_top, y_top):
        # Map top camera coordinates to depth camera coordinates
        if not self.calibration_data:
            logger.warning("No calibration data available")
            return int(x_top), int(y_top)
        
        try:
            top_coords = np.array([x_top, y_top, 1.0]) # Homogenous coordinates
            transformed = np.dot(self.camera_matrix_top, top_coords)
            depth_x, depth_y = transformed[0] / transformed[2], transformed[1] / transformed[2]
            return depth_x, depth_y
        
        except Exception as e:
            logger.error("Error mapping coordinates: {}".format(e))
            return int(x_top), int(y_top)
        
    def get_depth_at_pixel(self, depth_x, depth_y):
        try:
            # Get depth iamge
            depth_result = self.get_depth_image()

            if depth_result is None:
                logger.error("Failed to get depth image")
                return None
            
            depth_image, width, height = depth_result

            depth_x = int(depth_x)
            depth_y = int(depth_y)

            # Get depth from3x3 pixel region
            region_size = 3 
            x_start = max(0, depth_x - region_size//2)
            x_end = min(width, depth_x + region_size//2 + 1)
            y_start = max(0, depth_y - region_size//2)
            y_end = min(height, depth_y + region_size//2 + 1)

            depth_region = depth_image[y_start:y_end, x_start:x_end]

            # Filter zero values and get median depth
            valid_depths = depth_region[depth_region > 0]
            if len(valid_depths) == 0:
                print("No valid depth data found")
                # return None
                pass
                
            depth = np.median(valid_depths) / 1000

            if depth is not None:
                logger.info("Object is {}m away".format(depth))

            return depth
        
        except Exception as e:
            logger.error("Failed to get depth: {}".format(e))
            return None
        

    def transform_point_with_homogeneous_matrix(self, point, transform_matrix):
        try:
            # Convert point to homogeneous coordinates
            homogeneous_point = np.append(point, 1.0)
            
            # Apply transformation
            transform_matrix = np.array(transform_matrix).reshape(4, 4)
            transformed_point = np.dot(transform_matrix, homogeneous_point)
            
            # Convert back to 3D
            return transformed_point[:3]
        
        except Exception as e:
            logger.error("Error transforming point with homogeneous matrix: {}".format(e))
            return None

    def get_3d_position(self, x_cen, y_cen):
        try:
            logger.debug("Received pixel coordinates: x_cen={}, y_cen={}".format(x_cen, y_cen))

            # Convert 2D ray into 3D
            angular_position = self.video_proxy.getAngularPositionFromImagePosition(TOP_CAM_ID, [x_cen, y_cen])

            # Transform top cam coords to depth cam coords
            depth_x, depth_y = self.map_pixel_to_depth(x_cen, y_cen)
            depth = self.get_depth_at_pixel(depth_x, depth_y)

            if depth is not None:
                # The math here: point = [depth * tan(angular_y), depth * tan(angular_x), depth]
                camera_point = [
                    depth * np.tan(angular_position[1]),  # X in camera frame
                    depth * np.tan(angular_position[0]),  # Y in camera frame
                    depth                                  # Z in camera frame
                ]

                camera_transform = self.motion_proxy.getTransform("CameraTop", 2, 0)
                robot_point = self.transform_point_with_homogeneous_matrix(camera_point, camera_transform)

                # Calculate robot frame coordinates
                x_forward = robot_point[0]   # Forward distance
                y_lateral = robot_point[1]   # Lateral distance 
                theta = np.arctan2(y_lateral, x_forward)  # Angle
                
                return depth, {
                    "x": x_forward,
                    "y": y_lateral,
                    "z": robot_point[2],     # Height
                    "theta": theta           # Angle
                }
            
            else:
                return None
    
        except Exception as e:
            logger.error("Error calculating 3D position: {}".format(e))
        return None
