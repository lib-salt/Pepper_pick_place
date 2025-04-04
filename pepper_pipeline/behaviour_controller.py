import time
import math
from utils import logger
from robot_map import PepperRobotMap

class BehaviourController:
    def __init__(self, camera_manager, spatial_mapper, motion_controller, speech_manager, network_listener):
        self.camera_manager = camera_manager
        self.spatial_mapper = spatial_mapper
        self.motion_controller = motion_controller
        self.speech_manager = speech_manager
        self.network_listener = network_listener
        self.running = False
        self.detected_objects = []

    def start(self):
        self.running = True
        logger.info("Behaviour controller started")

    def stop(self):
        self.running = False
        logger.info("Behaviour controller stopped")

    def cleanup(self):
        self.stop()
        self.camera_manager.cleanup()
        self.motion_controller.cleanup()
        self.network_listener.cleanup()
        logger.info("Behavior controller cleaned up")

    def run_object_tracking(self):
        old_category = None
        
        while self.running:
            try:
                # Get object coordinates from network
                x_cen, y_cen, category = self.network_listener.get_object_coords()

                if x_cen is None:
                    logger.info("No object detected, skipping iteration")
                    continue

                # Get 3D position
                depth, position = self.spatial_mapper.get_3d_position(x_cen, y_cen, self.camera_manager)

                if position is None:
                    logger.warning("Could not get position data, skipping")
                    continue

                logger.info("Depth: {}".format(depth))
                logger.info("3D Coordinates: x={0}, y={1}, theta={2}".format(
                    position["x"], position["y"], position["theta"]
                ))

                # Announce detection if new object
                if old_category != category:
                    old_category = category
                    self.speech_manager.announce_object(category)

                # Check if the object is too close
                if self.motion_controller.stop_if_close(position["x"], stop_threshold=0.05):
                    continue

                # Store detected object
                obj = {
                    'x_forward': position.get('x', 0),
                    'y_lateral': position.get('y', 0),
                    'theta': position.get('theta', 0),
                    'category': category or 'unknown',
                    'depth': depth
                }
                self.detected_objects.append(obj)

                # Update map
                self._update_map(self.detected_objects)

                # Move towards object
                x = position["x"] - 0.18 # Add distance buffer to lift arm
                y = position["y"] + 0.15 # 20 (moveTo method) # Additional 10cm to line up right arm
                theta = position["theta"]

                # Move to object
                success = self.motion_controller.move_to_position(x, y, theta)

                if success:
                    # Wait for movement to comeplete
                    time.sleep(5)

                    # Tilt head to keep seeing object
                    self.motion_controller.tilt_head(0.3, 0.2)

                    # Grab object
                    self.motion_controller.reach_for_object()

                    # Reset for next detection
                    old_category = None

                    # Wait a moment before continuing
                    time.sleep(2)

            except Exception as e:
                logger.error("Error in object tracking loop: {}".format(e))

    def _update_map(self, detected_objects):
        if detected_objects:
            robot_map = PepperRobotMap()
            robot_map.update_map(detected_objects)
            map_filepath = robot_map.save()
