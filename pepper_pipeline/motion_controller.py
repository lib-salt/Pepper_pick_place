import math
from utils import logger
import time

class MotionController:
    def __init__(self, motion_proxy, awareness_proxy=None, face_proxy=None, autoLife_proxy=None, navigation_proxy=None):
        # Initialise motion control 
        self.motion_proxy = motion_proxy
        self.awareness_proxy = awareness_proxy
        self.face_proxy = face_proxy
        self.autoLife_proxy = autoLife_proxy
        self.navigation_proxy = navigation_proxy

        # Disable robot awareness features
        self._disable_awareness()

    def _disable_awareness(self):
        # Disable robot awareness features

        if self.face_proxy:
            self.face_proxy.clearDatabase()
            self.face_proxy.setTrackingEnabled(False)
            self.face_proxy.enableRecognition(False)
            logger.info("People tracking off")
        
        if self.awareness_proxy:
            self.awareness_proxy.pauseAwareness()
            self.awareness_proxy.setEnabled(False)
            self.awareness_proxy.setStimulusDetectionEnabled("People", False)
            self.motion_proxy.setStiffnesses("Body", 1.0)
            logger.info("Awareness off")
            self.tilt_head()

        # Disable arm collision protection
        if self.motion_proxy:
            self.motion_proxy.setExternalCollisionProtectionEnabled("Arms", False)
            
    def cleanup(self):
    # Clean up motion resources
        try:
            self.motion_proxy.stopMove()
            self.autoLife_proxy.setState("solitary")
            self.motion_proxy.setExternalCollisionProtectionEnabled("Arms", True)
            if self.face_proxy:    
                self.face_proxy.setTrackingEnabled(True)
            if self.awareness_proxy:
                self.awareness_proxy.setEnabled(True)
                self.awareness_proxy.setStimulusDetectionEnabled("People", True)
                self.awareness_proxy.resumeAwareness()
            logger.info("Motion resources cleaned up")

        except Exception as e:
            logger.error("Error during motion cleanup: {}".format(e))

    def is_moving(self):
        # Check if Pepper is moving
        try:
            status = self.motion_proxy.getMoveStatus()
            return status[0] == "moving"
        
        except Exception as e:
            logger.error("Error checking move status: {}".format(e))
            return False
        
    def reach_for_object(self):
       
        # Enable stiffness for the right arm and hip
        self.motion_proxy.setStiffnesses("RArm", 1.0)
        self.motion_proxy.setStiffnesses("Hip", 1.0)
        self.motion_proxy.setStiffnesses("Head", 0.8)  
        
        # Joint names 
        names = [
            'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 
            'RWristYaw', 'RHand', 'HipPitch', 'HipRoll', 'HeadPitch', 'HeadYaw'
        ]
        
        # Times for each keyframe 
        times = [
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],  # RShoulderPitch
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],  # RShoulderRoll
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],  # RElbowYaw
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],  # RElbowRoll
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],  # RWristYaw
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],  # RHand
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],  # HipPitch
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],  # HipRoll
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],  # HeadPitch
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]   # HeadYaw
        ]
        
        keys = [
            # RShoulderPitch 
            [1.4, 0.5, 0.2, -0.12, -0.2, -0.12, 0.1, 0.4],
            
            # RShoulderRoll 
            [-0.15, -0.2, -0.15, -0.1, -0.08, -0.08, -0.1, -0.15],
            
            # RElbowYaw 
            [1.5, 1.5, 1.3, 1.1, 1.0, 1.0, 1.2, 1.5],
            
            # RElbowRoll 
            [0.3, 0.5, 0.6, 0.5, 0.4, 0.45, 0.6, 0.5],
            
            # RWristYaw 
            [0.0, 0.2, 0.3, 0.4, 0.6, 0.6, 0.4, 0.2],
            
            # RHand 
            [0.6, 0.8, 0.9, 0.8, 0.0, 0.0, 0.0, 0.0],
            
            # HipPitch 
            [-0.05, -0.1, -0.25, -0.5, -0.65, -0.62, -0.3, -0.1],
            
            # HipRoll 
            [0.0, -0.02, -0.03, -0.04, -0.04, -0.03, -0.02, 0.0],
            
            # HeadPitch 
            [0.0, -0.1, -0.2, -0.3, -0.35, -0.35, -0.2, 0.0],
            
            # HeadYaw 
            [0.0, 0.1, 0.15, 0.2, 0.2, 0.2, 0.1, 0.0]
        ]
        
        try:
            # Add a slight weight shift before movement starts
            self.motion_proxy.setAngles("HipRoll", 0.02, 0.1)
            time.sleep(0.5)
            
            # Execute the main movement sequence
            logger.info("Starting arm grab sequence")
            self.motion_proxy.angleInterpolation(names, keys, times, True)
            
            # Subtle "success" movement 
            self.motion_proxy.setAngles("RShoulderPitch", 0.3, 0.2)
            time.sleep(0.5)
            
            logger.info("Completed arm grab sequence")
              
            return True
            
        except Exception as e:
            logger.error("Error executing arm movement: {}".format(e))
            return False

    def tilt_head(self, angle=0.3, speed= 0.2):
        # Tilt Pepper's head to look down
        try:
            self.motion_proxy.setAngles("HeadPitch", angle, speed)
            self.motion_proxy.setAngles("HeadYaw", 0.0, speed)
            logger.debug("Tilted head to angle: {}".format(angle))
        
        except Exception as e:
            logger.error("Error tilting head: {}".format(e))

    def move_to_position(self, x, y, theta=0.0, speed=0.5):
        # Move Pepper to position
        try:
            # Safe movements list
            MIN_X, MAX_X = -1.0, 4.0
            MIN_Y, MAX_Y = -1.0, 1.0
            MIN_THETA, MAX_THETA = -math.pi, math.pi

            # Check if movement is within safe range
            if not (MIN_X <= x <= MAX_X) or not (MIN_Y <= y <= MAX_Y) or not (MIN_THETA <= theta <= MAX_THETA):
                logger.warning("Movement out of range: x={}, y={}, theta={}".format(x, y, theta))
                return False

            # Get ready to move
            self.motion_proxy.moveInit()            
            logger.info("Moving to: x={}, y={}, theta={}".format(x, y, theta))
            movement = self.navigation_proxy.navigateTo(x, y)

            if movement:
                logger.info("Navigation Successful!")
                time.sleep(1) # Make sure movement is complete

                # Get current robot positition 
                final_position = self.motion_proxy.getRobotPosition(True)
                current_theta = final_position[2]

                # Calculate rotation to face the object
                new_theta = theta - current_theta

                # Normalise theta into radians
                if new_theta > math.pi:
                    new_theta -= 2 * math.pi
                elif new_theta < -math.pi:
                    new_theta += 2 * math.pi

                self.motion_proxy.moveTo(0, 0, new_theta)

            else:
                logger.info("Navigation failed")
            return movement
        
        except Exception as e:
            logger.error("Error moving to position: {}".format(e))
            return False
        
    def stop_if_close(self, distance, stop_threshold=0.03):
        # Stop movement if closer than threshold
        try:
            if distance <= stop_threshold:
                self.motion_proxy.stopMove()
                logger.info("Object is {}m away, stopping".format(distance))
                return True
            return False
        
        except Exception as e:
            logger.error("Error checking distance: {}".format(e))
            return False

    def get_robot_position(self):
        return self.motion_proxy.getRobotPosition(True)

    # Non-implemented methods but potential to add further improvements
    def move_increment(self):
        # Move forward by 10cm
        self.motion_proxy.moveTo(0.1, 0, 0, _async=True)
        self.motion_proxy.waitUntilMoveIsFinished()
    
    def search_with_head(self, search_angles=None, pause_duration=1.0):
        # Move Pepper's head to scan the environment
        if search_angles is None:
            search_angles = [
                (-0.8, 0.1),  # Far left, slightly down
                (-0.4, 0.1),  # Left, slightly down
                (0.0, 0.1),   # Center, slightly down
                (0.4, 0.1),   # Right, slightly down
                (0.8, 0.1),   # Far right, slightly down
                (0.6, 0.3),   # Right, more down
                (0.0, 0.3),   # Center, more down
                (-0.6, 0.3),  # Left, more down
            ]

        for yaw, pitch in search_angles:
            try:
                # Set head angles
                self.motion_proxy.setAngles(["HeadYaw", "HeadPitch"], [yaw, pitch], 0.2)
                logger.info("Searching - Head at yaw={}, pitch={}".format(yaw, pitch))
                return yaw, pitch
                    
            except Exception as e:
                logger.error("Error during search motion: {}".format(e))
                
        return None, None
