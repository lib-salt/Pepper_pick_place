import numpy as np
import cv2

# Define the checkerboard pattern size
pattern_size = (6, 7)  # 6 rows, 7 columns
square_size = 0.02  # Size of each square in meters

# Prepare object points based on the checkerboard pattern size
object_points = np.zeros((np.prod(pattern_size), 3), dtype=np.float32)
object_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
object_points *= square_size

obj_points = []  # 3D points in real-world space
img_points_top = []  # 2D points in top camera image
img_points_left = []  # 2D points in left-eye camera image

# Number of images to use for calibration
num_images = 50  

# Loop through all the saved images
for i in range(1, num_images + 1):
    top_image = cv2.imread('top_camera_{}.jpg'.format(i))
    left_image = cv2.imread('left_eye_{}.jpg'.format(i))

    # Convert images to grayscale for corner extraction
    gray_top = cv2.cvtColor(top_image, cv2.COLOR_BGR2GRAY)
    gray_left = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)

    # Try to find checkerboard corners in both images
    found_top, corners_top = cv2.findChessboardCorners(gray_top, pattern_size, None)
    found_left, corners_left = cv2.findChessboardCorners(gray_left, pattern_size, None)

    # If both checkerboards are found, add the points to the lists
    if found_top and found_left:
        # Refine the corner locations 
        cv2.cornerSubPix(gray_top, corners_top, (11, 11), (-1, -1), 
                         criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1))
        cv2.cornerSubPix(gray_left, corners_left, (11, 11), (-1, -1), 
                         criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1))

        # Draw and save the corners 
        cv2.drawChessboardCorners(top_image, pattern_size, corners_top, found_top)
        cv2.drawChessboardCorners(left_image, pattern_size, corners_left, found_left)

        cv2.imwrite("top_camera_with_corners_refined_{}.jpg".format(i), top_image)
        cv2.imwrite("left_eye_with_corners_refined_{}.jpg".format(i), left_image)

        # Add the points to the lists for calibration
        obj_points.append(object_points)
        img_points_top.append(corners_top)
        img_points_left.append(corners_left)

        print("Checkerboard detected in image {}.".format(i))
    else:
        print("Checkerboard not detected in image {}. Skipping.".format(i))

# Camera calibration: Find intrinsic parameters and transformation 
ret, camera_matrix_top, dist_coeffs_top, camera_matrix_left, dist_coeffs_left, R, T, E, F = cv2.stereoCalibrate(
    obj_points, img_points_top, img_points_left, None, None, None, None, gray_top.shape[::-1],
    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1), flags=cv2.CALIB_FIX_INTRINSIC)

# Save the calibration results 
np.savez('camera_transformation.npz', 
         R=R, T=T, camera_matrix_top=camera_matrix_top, camera_matrix_left=camera_matrix_left,
         dist_coeffs_top=dist_coeffs_top, dist_coeffs_left=dist_coeffs_left)

print("Stereo Calibration Complete! Transformation saved.")
