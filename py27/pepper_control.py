import math
import time
import sys
import numpy as np
sys.path.append(r"E:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib")
from naoqi import ALProxy  

# Check if Pepper is actively moving
def is_moving(motion_proxy):
    status = motion_proxy.getMoveStatus()
    return status[0] == "moving"

def move_towards_object(motion_proxy, horizontal_angle, height_angle, distance):
    try:
        turn_radians = math.radians(horizontal_angle)

        # Turn Pepper head to focus on the object
        motion_proxy.setAngles(["HeadYaw"], [turn_radians], 0.1)

        # Rotate Pepper to object
        motion_proxy.moveTo(0, 0, turn_radians)
        # Move right arm
        motion_proxy.setAngles("RShoulderPitch", height_angle, 0.5)
        motion_proxy.moveTo(distance, 0, 0)

        while is_moving(motion_proxy):
            time.sleep(0.1)  # Wait for Pepper to finish moving
        
        print("Movement completed, ready for new command.")

    except Exception as e:
        print("Error while moving Pepper: ", e)

def move_arm(motion_proxy, height_angle):
    try:
        # Limit movement to Pepper's joint range
        height_angle = max(-1.5, min(1.5, height_angle))  # Shoulder pitch should stay within (-1.5 to 1.5 rad)
        
        motion_proxy.setAngles("RShoulderPitch", abs(height_angle), 0.5)
    
    except Exception as e:
        print("Error while moving right arm: ", e)

# Camera calibration
calibration_data = np.load('camera_transformation.npz')
R = calibration_data['R']  # Rotation matrix (3x3)
T = calibration_data['T']  # Translation vector (3x1)
camera_matrix_top = calibration_data['camera_matrix_top']  
camera_matrix_depth = calibration_data['camera_matrix_left'] 
dist_coeffs_top = calibration_data['dist_coeffs_top']
dist_coeffs_left = calibration_data['dist_coeffs_left']

focal_length_mm = 1.756  # mm, estimated
image_width = 320  # pixels (for the top camera)
image_height = 240  # pixels (for the top camera)

# Sensor dimensions
sensor_width_mm = 0.448  # mm (calculated earlier)
sensor_height_mm = 0.336  # mm (calculated earlier)

# Focal length in pixels (based on resolution)
f_x = focal_length_mm * image_width / sensor_width_mm  # in pixels
f_y = f_x  # Assuming square pixels, so f_x = f_y
c_x = image_width / 2  # optical center x-coordinate
c_y = image_height / 2 

def pixel_to_normalized_coords(x, y, camera_matrix):
    # Normalize the pixel coordinates using the camera intrinsic matrix
    inv_K = np.linalg.inv(camera_matrix)
    pixel_coords = np.array([x, y, 1]).reshape(3, 1)  # Homogeneous coordinates
    normalized_coords = np.dot(inv_K, pixel_coords)
    return normalized_coords

# Function to map top camera pixel coordinates to depth camera coordinates
def map_top_to_depth_camera(x_top, y_top):
    # Convert top camera pixel coordinates to normalized coordinates
    normalized_top = pixel_to_normalized_coords(x_top, y_top, camera_matrix_top)

    # Apply the transformation from top camera to depth camera
    # 1. Apply the rotation matrix (R) and translation vector (T) to the normalized coordinates
    normalized_depth = np.dot(R, normalized_top) + T

    # 2. Convert back to pixel coordinates in the depth camera
    # Use the depth camera intrinsic matrix to convert back to pixel coordinates
    pixel_coords_depth = np.dot(camera_matrix_depth, normalized_depth)

    # Return the pixel coordinates in the depth camera image
    x_depth, y_depth = pixel_coords_depth[0] / pixel_coords_depth[2], pixel_coords_depth[1] / pixel_coords_depth[2]
    
    return int(x_depth), int(y_depth)

def pixel_to_3d(x, y, depth):
    X = (x - c_x) * depth / f_x
    Y = (y - c_y) * depth / f_y
    Z = depth # Depth from the depth map
    
    return X, Y, Z

def close_stop(Z, motion_proxy, stop_distance=0.2):
    if Z <= stop_distance:
        motion_proxy.stopMove()
        print("Object is ", Z, "m away")
        return True
    return False

def track_object(x, y, motion_proxy):
    pan_angle = (x - c_x) * 0.003  
    tilt_angle = (y - c_y) * 0.003
    motion_proxy.setAngles(["HeadYaw", "HeadPitch"], [pan_angle, tilt_angle], 0.2)

def get_transform(motion_proxy):
    # Get co-ordinates in robot frame
    transform = motion_proxy.getTransform("CameraTop", 1, True)
    return transform

def transform_to_frame(camera_coords, motion_proxy):
    transform = get_transform(motion_proxy)

    rotation_matrix = np.array(transform[0])
    translation_vector = np.array(transform[1])

    camera_coords_np = np.array(camera_coords)
    transformed_coords = np.dot(rotation_matrix, camera_coords_np) + translation_vector
    return transformed_coords

def move_towards_object(robot_coords, motion_proxy):
    x, y, z = robot_coords
    x = x - 0.1 # 10cm away
    motion_proxy.moveTo(x, y, z)

