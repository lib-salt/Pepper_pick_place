import numpy as np
import math
from utils import logger
from config import TOP_CAM_ID, CALIBRATION_FILE

class SpatialMapper:
    def __init__(self, video_proxy, motion_proxy):
        self.video_proxy = video_proxy
        self.motion_proxy = motion_proxy

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
                self.calibration_data = None
        except Exception as e:
            logger.error("Error while loading calibration data: {}".format(e))
            self.calibration_data = None

    def map_pixel_to_depth(self, x_top, y_top):
        # Map top camera coordinates to depth camera coordinates
        if not self.calibration_data:
            logger.warning("No calibration data available")
            return int(x_top), int(y_top)
        
        try:
            top_coords = np.array([x_top, y_top, 1.0]) # Homogenous coordinates
            transformed = np.dot(self.camera_matrix_top, top_coords)
            depth_x, depth_y = transformed[0] / transformed[2], transformed[1] / transformed[2]
            return int(depth_x), int(depth_y)
        
        except Exception as e:
            logger.error("Error mapping coordinates: {}".format(e))
            return int(x_top), int(y_top)
        
    def get_depth_at_pixel(self, depth_x, depth_y, depth_image, width, height):
        # Get depth at given pixel location
        try:
            depth_x = int(depth_x)
            depth_y = int(depth_y)

            # Get depth from 3x3 pixel region
            region_size = 3
            x_start = max(0, depth_x - region_size//2)
            x_end = min(width, depth_x + region_size//2 + 1)
            y_start = max(0, depth_y - region_size//2)
            y_end = min(height, depth_y + region_size//2 + 1)

            depth_region = depth_image[y_start:y_end, x_start:x_end]

            # Filter zero values and get median depth
            valid_depths = depth_region[depth_region > 0]
            if len(valid_depths) == 0:
                logger.warning("No valid depth data found")
                return None
            
            depth = np.median(valid_depths) / 1000 # Convert from mm to m

            if depth is not None:
                logger.info("Object is {}m away".format(depth))

            return depth
        
        except Exception as e:
            logger.error("Failed to get depth: {}".format(e))

    def get_3d_position(self, x_cen, y_cen, camera_manager):
        try:
            logger.debug("Received pixel coordinates: x_cen={}, y_cen={}".format(x_cen, y_cen))

            # Normalise coordinates between 0 and 1
            norm_x = x_cen / 320 # Image width
            norm_y = y_cen / 240 # Image height
            # norm_x = x_cen / self.image_width
            # norm_y = y_cen / self.image_height

            # Convert 2D array into 3D
            angular_position = self.video_proxy.getAngularPositionFromImagePosition(TOP_CAM_ID, [norm_x, norm_y])

            # Transform top cam coords into depth cam coords
            depth_x, depth_y = self.map_pixel_to_depth(x_cen, y_cen)

            # Get depth image
            depth_result = camera_manager.get_depth_image()
            if depth_result is None:
                logger.error("Failed to get depth image")
                return None, None
            
            depth_image, width, height = depth_result
            depth = self.get_depth_at_pixel(depth_x, depth_y, depth_image, width, height)

            if depth is not None:
                # Calculate position in robot frame
                x_forward = depth * math.cos(angular_position[1])
                y_lateral = depth * math.sin(angular_position[0])
                theta = angular_position[0]

                return depth, {
                    "x": x_forward,
                    "y": y_lateral,
                    "theta": theta
                }
            else:
                return None, None
            
        except Exception as e:
            logger.error("Error calculating 3D position: {}".format(e))
