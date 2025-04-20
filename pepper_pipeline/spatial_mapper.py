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
        
    def get_depth_at_pixel(self, depth_x, depth_y, depth_image, width, height, samples=5):
        # Get depth at given pixel location
        try:
            depth_x = int(depth_x)
            depth_y = int(depth_y)

            # Get depth from 3x3 pixel region
            region_size = 3

            anom_threshold = 1.0

            depth_samples = []
            
            for _ in range(samples):
                # Get depth from 3x3 pixel region
                x_start = max(0, depth_x - region_size//2)
                x_end = min(width, depth_x + region_size//2 + 1)
                y_start = max(0, depth_y - region_size//2)
                y_end = min(height, depth_y + region_size//2 + 1)

                depth_region = depth_image[y_start:y_end, x_start:x_end]

                # Filter zero values and get median depth
                valid_depths = depth_region[depth_region > 0]
                if len(valid_depths) > 0:
                    sample_depth = np.median(valid_depths) / 1000  # Convert from mm to m
                    depth_samples.append(sample_depth)
            
            if len(depth_samples) == 0:
                logger.warning("No valid depth data found in any sample")
                # return None, None, []
                return
            
            # Remove anomolies
            filtered_samples, removed_anomalies = self._filter_anomalies(depth_samples, anom_threshold)
            
            if len(filtered_samples) < max(2, samples // 2):
                logger.warning("Too many anomalies detected: {}/{} samples removed".format(len(removed_anomalies), len(depth_samples)))
            if len(filtered_samples) == 0:
                # return None, None, [], removed_anomalies
                return

            median_depth = np.median(depth_samples)
            std_deviation = np.std(depth_samples)

            logger.info("Object is {}m away (std: {}m, samples: {})".format(
                median_depth, std_deviation, len(depth_samples)))
            logger.debug("All depth samples: {}".format(depth_samples))

            if median_depth is not None:
                logger.info("Object is {}m away".format(median_depth))

            return median_depth
        
        except Exception as e:
            logger.error("Failed to get depth: {}".format(e))

    def get_3d_position(self, x_cen, y_cen, camera_manager):
        try:
            logger.debug("Received pixel coordinates: x_cen={}, y_cen={}".format(x_cen, y_cen))

            # Normalise coordinates between 0 and 1
            norm_x = x_cen / 320 # Image width
            norm_y = y_cen / 240 # Image height


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
                theta = math.atan2(y_lateral, x_forward)

                return depth, {
                    "x": x_forward,
                    "y": y_lateral,
                    "theta": theta
                }
            else:
                return None, None
            
        except Exception as e:
            logger.error("Error calculating 3D position: {}".format(e))

    def _filter_anomalies(self, samples, threshold=1.0):

        if len(samples) < 4:  # Not enough samples for reliable IQR
            return samples, []
        
        # Sort the samples
        sorted_samples = sorted(samples)
        
        # Calculate Q1 and Q3
        q1_idx = int(len(sorted_samples) * 0.25)
        q3_idx = int(len(sorted_samples) * 0.75)
        q1 = sorted_samples[q1_idx]
        q3 = sorted_samples[q3_idx]
        
        # Calculate IQR and boundaries
        iqr = q3 - q1
        lower_bound = q1 - (threshold * iqr)
        upper_bound = q3 + (threshold * iqr)
        
        # Filter samples
        filtered_samples = []
        removed_anomalies = []
        
        for sample in samples:
            if lower_bound <= sample <= upper_bound:
                filtered_samples.append(sample)
            else:
                removed_anomalies.append(sample)
        
        return filtered_samples, removed_anomalies