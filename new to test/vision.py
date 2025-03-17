import socket 
import threading
import logging
import math
import time
from utils import logger

class ObjectTracker:
    def __init__(self, pepper_camera, pepper_motion):
        # Initialise object tracker
        self.camera = pepper_camera
        self.motion = pepper_motion
        self.location_sock = None
        self.running = False

    def initialise(self,server_ip, port):
        # Initialise object tracker socket
        try:
            self.location_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.location_sock.bind((server_ip, port))
            self.running = True
            logger.info("Object tracker initialised")
            return True
        
        except Exception as e:
            logger.error("Error initialising object tracker: {}".format(e))
            return False
        
    def cleanup(self):
        # Cleanup tracker resources
        try:
            self.running = False
            if self.location_sock:
                self.location_sock.close()
            logger.info("Object tracker cleaned up")

        except Exception as e:
            logger.error("Error during tracker cleanup: {}".format(e))

    def track_and_move(self):
        # Track objects and move towards them
        if not self.running or not self.location_sock:
            logger.error("Tracker not initialised")
            return
        
        try:
            while self.running:
                # Receive coordinate data
                data, _ = self.location_sock.recvfrom(1024)

                if not data:
                    logger.warning("No data received from object detector")
                    continue

                # Decode data from socket
                coords = data.decode().split(',')
                if len(coords) < 3:
                    logger.warning("Invalid data fromat received: ", data)
                    continue

                x_cen = float(coords[0])
                y_cen = float(coords[1])
                category = str(coords[2])

                logger.info("Detected ", category, "at coordinates (", x_cen, ", ", y_cen, ")")

                # Map to camera coordinates to depth camera
                x_depth, y_depth = self.camera.map_to_depth_camera(x_cen, y_cen)

                # Get depth
                depth = self.camera.get_depth_data(x_depth, y_depth)
                
                if depth is None:
                    logger.warning("Could not get depth data, skipping")
                    continue

                # Convert to 3D coordinates
                X, Y, Z = self.camera.pixel_to_3d(x_cen, y_cen, depth)
                logger.info("3D Coordinates: X=", X, " Y=", Y, " Z=", Z)
                
                # Announce detection
                text = str("I have found a " + category)
                self.motion.say(text)
                
                # Check if object is too close
                if self.motion.stop_if_close(Z):
                    continue
                
                # Transform to robot coordinates
                robot_coords = self.motion.transform_to_frame([X, Y, Z])
                
                if robot_coords is None:
                    logger.warning("Could not transform coordinates, skipping")
                    continue
                    
                logger.info("Robot Coordinates: ", robot_coords)

                # Move towards object
                # Using direct movement based on depth and center offset
                x = (depth / 100) - 0.2  # Convert to meters and apply offset
                y = x_cen / 100  # Convert to meters
                z = math.atan2(y_cen, x_cen)  # Calculate angle to turn
                
                logger.info("Moving: ", x, y, z)
                self.motion.motion_proxy.moveTo(x, y, z)
                
                # Tilt head down to keep object in view
                self.motion.tilt_head(0.3, 0.2)
                time.sleep(1)
                
        except Exception as e:
            logger.error("Error in object tracking: {}".format(e))