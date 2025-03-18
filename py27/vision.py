import socket 
import threading
import logging
import math
import time
from utils import logger

class ObjectTracker:
    def __init__(self, pepper_camera, pepper_motion, navigation_proxy=None):
        # Initialise object tracker
        self.navigation_proxy = navigation_proxy
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
        old_cat = None
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

                logger.info("Detected {0} at coordinates ({1}, {2})".format(category, x_cen, y_cen))

                # Get 3D position
                depth, position = self.camera.get_3d_position(x_cen, y_cen)

                if position is None:
                    logger.warning("Could not get position data, skipping")
                    continue

                logger.info("3D Coordinates: X={0}, Y={1}, Z={2}".format(position["x"], position["y"], position["z"]))
                
                # Announce detection
                if old_cat != category:
                    old_cat = category
                    text = "I have found a {0}".format(category)
                    self.motion.say_object(text)
                
                # Check if object is too close
                if self.motion.stop_if_close((position["x"])):
                    continue

                # Move towards object
                x = depth - 0.4
                # x = (position["x"] / 100) - 0.2  # Convert to meters and apply offset
                y = position["y"] / 100  # Convert to meters
                z = position["theta"]  # Angle to turn
                    
                logger.info("Moving: x={0}, y={1}, z={2}".format(x, y, z))
                move = self.motion.motion_proxy.moveTo(x, y, z)
                # move = self.navigation_proxy.navigateTo(x, y)

                if move:
                    logger.info("Successfully reached object")
                else:
                    logger.error("Failed to reach object")
                    
                # Tilt head down to keep object in view
                self.motion.tilt_head(0.3, 0.2)
                time.sleep(1)
                
        except Exception as e:
            logger.error("Error in object tracking: {}".format(e))