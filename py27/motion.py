import numpy as np
import math
import time
import logging
from utils import logger

class PepperMotion:
    def __init__(self, motion_proxy, speech_proxy=None, tracker_proxy=None, autonomousLife_proxy=None):
        # Initialise motion control for Pepper
        self.motion_proxy = motion_proxy
        self.speech_proxy = speech_proxy
        self.tracker_proxy = tracker_proxy
        self.autonomousLife_proxy = autonomousLife_proxy

        # Initialises speech
        if self.speech_proxy:
            self.speech_proxy.setLanguage("English")

        # Pause awareness
        if self.autonomousLife_proxy:
            self.autonomousLife_proxy.setState("disabled")
            self.motion_proxy.wakeUp()
            self.tilt_head()
            logger.info("Autonomous life off")

    def cleanup(self):
        # Clean up motion resources
        try:
            self.motion_proxy.stopMove()
            if self.autonomousLife_proxy:
                self.autonomousLife_proxy.setState("solitary")
            logger.info("Motion resources cleaned up")

        except Exception as e:
            logger.error("Error during motion cleanup: {}".format(e))

    def is_moving(self):
        # Check if Pepper is currently moving
        try:
            status = self.motion_proxy.getMoveStatus()
            return status[0] == "moving"
        
        except Exception as e:
            logger.error("Error checking movement status{}".format(e))
            return False
        
    def move_arm(self, height_angle):
        # Move Peppers right arm
        try:
            height_angle = max(-1.5, min(1.5, height_angle))
            self.motion_proxy.setAngles("RShoulderPitch", abs(height_angle), 0.5)
            logger.debug("Moved arm to angle: ", height_angle)

        except Exception as e:
            logger.error("Error moving arm: {}".format(e))

    def track_object(self, x, y):
        # Track object using the head
        try:
            c_x, c_y = 160, 120 # assuming center of image
            pan_angle = (x - c_x) * 0.003
            tilt_angle = (y - c_y) * 0.003

            # Set head angles
            self.motion_proxy.setAngles(["HeadYaw", "HeadPitch"], [pan_angle, tilt_angle], 0.2)
            debug_message = str("Tracking object at (", x, ", ", y, ") pan=", 
                                pan_angle, ", tilt=", tilt_angle)
            logger.debug(debug_message)

        except Exception as e:
            logger.error("Error tracking object with head: {}".format(e))

    def tilt_head(self, angle=0.3, speed=0.2):
        # Tilt Pepper's head to look down
        try:
            self.motion_proxy.setAngles("HeadPitch", angle, speed)
            logger.debug("Tilted head to angle: ", angle)
        
        except Exception as e:
            logger.error("Error tilting head: {}".format(e))
    
    def get_transform(self):
        # Get transformation from camera frame to robot frame
        try:
            transform = self.motion_proxy.getTransform("CameraTop", 1, True)
            return transform
        
        except Exception as e:
            logger.error("Error getting transform: {}".format(e))
            return None
        
    def transform_to_frame(self, camera_coords):
        # Transform camera coordinates into robot frame
        try:
            transform = self.get_transform()
            if not transform:
                return None
            
            rotation_matrix = np.array(transform[0])
            translation_vector = np.array(transform[1])

            camera_coords_np = np.array(camera_coords)
            transformed_coords = np.dot(rotation_matrix, camera_coords_np) + translation_vector

            return transformed_coords
        
        except Exception as e:
            logger.error("Error transforming coordinates into robot frame: {}".format(e))
            return None
    
    def move_towards_object(self, coords, safety_margin=0.2):
        # Move towards object coordinates
        try:
            x, y, z = coords

            # Apply safety margin
            x = x - safety_margin

            logger.infor("Moving to coordinates: (", x, ", ", y, ", ", z, ")")
            self.motion_proxy.moveTo(x, y, z)

            return True
        
        except Exception as e:
            logger.error("Error moving towards object: ", )
            return False
        
    def stop_if_close(self, distance, stop_threshold=0.3):
        # Stop movement if object is closer than threshold
        try:
            if distance <= stop_threshold:
                self.motion_proxy.stopMove()
                logger.info("Object is {}m away, stopping".format(distance))
                return True
            return False
        
        except Exception as e:
            logger.error("Error checking distance: {}".format(e))
            return False
        
    def say_object(self, text):
        # Make Pepper speak
        if self.speech_proxy:
            try:
                self.speech_proxy.say(text)
                logger.debug("Pepper said: ", text)
            
            except Exception as e:
                logger.error("Error making Pepper talk: {}".format(e))