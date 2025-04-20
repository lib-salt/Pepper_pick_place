import sys
import time
import signal
import threading
from config import *
from utils import logger

from naoqi import ALProxy
from camera_manager import CameraManager
from spatial_mapper import SpatialMapper
from speech_manager import SpeechManager
from motion_controller import MotionController
from network_listener import NetworkListener
from behaviour_controller import BehaviourController

controller = None

def signal_handler(dig, frame):
    # Handle termination signal gracefully
    logger.info("Shutdown signal rexeived, cleanig up ...")
    if controller:
        controller.cleanup()
    sys.exit(0)

def main():
    global controller

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Connect to robot
        logger.info("Connecting to Pepper at {}.{}".format(ROBOT_IP, ROBOT_PORT))

        # Initialise proxies
        video_proxy = ALProxy("ALVideoDevice", ROBOT_IP, ROBOT_PORT)
        motion_proxy = ALProxy("ALMotion", ROBOT_IP, ROBOT_PORT)
        speech_proxy = ALProxy("ALTextToSpeech", ROBOT_IP, ROBOT_PORT)
        awareness_proxy = ALProxy("ALBasicAwareness", ROBOT_IP, ROBOT_PORT)
        face_proxy = ALProxy("ALFaceDetection", ROBOT_IP, ROBOT_PORT)
        autoLife_proxy = ALProxy("ALAutonomousLife", ROBOT_IP, ROBOT_PORT)
        navigation_proxy = ALProxy("ALNavigation", ROBOT_IP, ROBOT_PORT)
        
        # Initialise components
        camera_manager = CameraManager(video_proxy)
        spatial_mapper = SpatialMapper(video_proxy, motion_proxy)
        speech_manager = SpeechManager(speech_proxy)
        motion_controller = MotionController(motion_proxy, awareness_proxy,
                                             face_proxy, autoLife_proxy, navigation_proxy)
        network_listener = NetworkListener()

        # Initialise behaviour controller
        controller = BehaviourController(
            camera_manager,
            spatial_mapper,
            motion_controller,
            speech_manager,
            network_listener
        )

        # Check initialisation
        logger.info("Initialising camera ...")
        if not camera_manager.initialise():
            logger.error("Failed to initialise camera, exiting")
            return
        
        logger.info("Initialising network listener ...")
        if not network_listener.initialise(SERVER_IP, LOCATION_PORT):
            logger.error("Failed to initialise network listener, exiting")
            return
        
        # Start video streaming
        logger.info("Starting video stream ...")
        video_thread = camera_manager.start_video_stream(SERVER_IP, VIDEO_PORT)

        # Start behaviour controller
        logger.info("Starting object tracking ...")
        controller.start()

        # Run tracking loop
        tracking_thread = threading.Thread(
            target=controller.run_object_tracking,
        )
        tracking_thread.setDaemon(True)
        tracking_thread.start()

        # Keep main thread alive
        logger.info("System running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)

    except Exception as e:
        logger.error("Error in main: {}".format(e))
    finally:
        # Cleanup
        if controller:
            controller.cleanup()

if __name__ == "__main__":
    main()
