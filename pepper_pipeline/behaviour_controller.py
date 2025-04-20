import time
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
        self.target_positions = []
        self.actual_positions = []

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

        # Start position for mapping
        initial_pos = {
            'x': 0,
            'y': 0,
            'theta': 0,
        }
        self.actual_positions.append(initial_pos)
        
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

                if depth is None:
                    logger.warning("Could not get depth data, skipping")
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
                self._update_map(self.detected_objects, self.actual_positions)

                # Move towards object
                x = position["x"] - 0.10 # Add distance buffer to lift arm
                y = position["y"] + 0.15 # Additional movement to line up right arm
                theta = position["theta"]

                # Calculate target position relative to the current position
                start_pos = self.motion_controller.get_robot_position()
                target_position = {
                    'x': x,
                    'y': y,
                    'theta': theta,
                }
                self.target_positions.append(target_position)

                self._update_map(self.detected_objects, self.actual_positions, self.target_positions)

                # Move to object
                success = self.motion_controller.move_to_position(x, y, theta)

                if success:
                    # Wait for movement to comeplete
                    time.sleep(2)

                    # Get the new position of the robot
                    new_pos = self.motion_controller.get_robot_position()
                    # Position of robot for 2D map 
                    map_pos = [new - old for new, old in zip(new_pos, start_pos)]

                    actual_position = {
                    'x': map_pos[0],
                    'y': map_pos[1],
                    'theta': map_pos[2],
                    }
                    self.actual_positions.append(actual_position)

                    # Update map with robot positions
                    self._update_map(self.detected_objects, self.actual_positions, self.target_positions)

                    # Announce reaching object position
                    self.speech_manager.announce_reaching_object(category)

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

    def _update_map(self, detected_objects, actual_positions=None, target_positions=None):
        if detected_objects:
            robot_map = PepperRobotMap()
            robot_map.update_map(detected_objects, actual_positions, target_positions)
            map_filepath = robot_map.save()
