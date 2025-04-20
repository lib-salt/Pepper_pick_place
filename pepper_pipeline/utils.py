import sys
import numpy as np
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pepper_robot')

# Add NAOqi library to system path
from config import NAOQI_PATH
sys.path.append(NAOQI_PATH)

try:
    from naoqi import ALProxy, ALBroker
except ImportError:
    logger.error("Failed to import NAOqi. Check the path and installation.")
    sys.exit(1)

# Load camera claibration data from a file
def load_calibration_data(file_path):
    try:
        data = np.load(file_path)
        return {
            'R': data['R'],
            'T': data['T'],
            'camera_matrix_top': data['camera_matrix_top'],
            'camera_matrix_depth': data['camera_matrix_left'],
            'dist_coeffs_top': data['dist_coeffs_top'],
            'dist_coeffs_left': data['dist_coeffs_left']
        }
    except Exception as e:
        logger.error("Failed to load calibration data: {}".format(e))
        return None