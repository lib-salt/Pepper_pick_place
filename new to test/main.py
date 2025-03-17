import sys
import time
import signal
import threading
from config import *
from utils import logger
import utils

from naoqi import ALBroker, ALProxy
from pepper_camera import PepperCamera
from motion import PepperMotion
from vision import ObjectTracker

def setup_signal_handlers(robot_app):
    # Setup signal handlers for cleanup
    def cleanup_handler(sig, frame):
        logger.info("Shutdown signal received, cleaning up ...")
        robot_app.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)

class PepperRobot:
    # Main class for Pepper robot application
    def __init__(self):
        # Initialises Pepper robot application
        self.broker = None
        self.motion_proxy = None
        self.video_proxy = None
        self.tracker_proxy = None
        self.awareness_proxy = None
        self.speech_proxy = None
        
        self.camera = None
        self.motion = None
        self.tracker = None
        
        self.threads = []

    def initialise(self):
        # initialises all components
        try: 
             # Set up broker and proxies
            self.broker = ALBroker("pythonBroker", "0.0.0.0", 0, ROBOT_IP, ROBOT_PORT)
            self.motion_proxy = ALProxy("ALMotion", ROBOT_IP, ROBOT_PORT)
            self.video_proxy = ALProxy("ALVideoDevice", ROBOT_IP, ROBOT_PORT)
            self.tracker_proxy = ALProxy("ALTracker", ROBOT_IP, ROBOT_PORT)
            self.awareness_proxy = ALProxy("ALBasicAwareness", ROBOT_IP, ROBOT_PORT)
            self.speech_proxy = ALProxy("ALTextToSpeech", ROBOT_IP, ROBOT_PORT)
            
            logger.info("NAOqi proxies initialized successfully")
            
            # Initialize camera module
            self.camera = PepperCamera(self.video_proxy)
            if not self.camera.initialize():
                logger.error("Failed to initialize camera module")
                return False
            
            # Initialize motion module
            self.motion = PepperMotion(
                self.motion_proxy,
                self.speech_proxy,
                self.tracker_proxy,
                self.awareness_proxy
            )
            
            # Initialize object tracker
            self.tracker = ObjectTracker(self.camera, self.motion)
            if not self.tracker.initialize(SERVER_IP, LOCATION_PORT):
                logger.error("Failed to initialize object tracker")
                return False
            
            logger.info("All modules initialised successfully")
            return True
            
        except Exception as e:
            logger.error("Initialisation error: {}".format(e))
            return False
        
    def start(self):
        # Start all threads and main operation
        if not hasattr(self, 'camera') or not hasattr(self, 'tracker'):
            logger.error("Modules not initialized")
            return False
        
        try:
            # Create threads
            video_thread = threading.Thread(
                target=self.camera.stream_video,
                args=(SERVER_IP, VIDEO_PORT)
            )
            video_thread.setDaemon(True)
            
            tracker_thread = threading.Thread(
                target=self.tracker.track_and_move
            )
            tracker_thread.setDaemon(True)
            
            # Start threads
            video_thread.start()
            tracker_thread.start()
            
            # Store threads for cleanup
            self.threads = [video_thread, tracker_thread]
            
            logger.info("All threads started successfully")
            return True
            
        except Exception as e:
            logger.error("Error starting threads: {}".format(e))
            return False
        
    def cleanup(self):
        # Clean up all resources
        try:
            if hasattr(self, 'tracker') and self.tracker:
                self.tracker.cleanup()
                
            if hasattr(self, 'camera') and self.camera:
                self.camera.cleanup()
                
            if hasattr(self, 'motion') and self.motion:
                self.motion.cleanup()
            
            if hasattr(self, 'broker') and self.broker:
                time.sleep(0.5)  # Allow time for other operations to complete
                self.broker.shutdown()
                
            logger.info("All resources cleaned up successfully")
            
        except Exception as e:
            logger.error("Error during cleanup: {}".format(e))

def main():
    # Main function to run application
    logger.info("Starting Pepper robot application")

    # Initialise robot
    robot = PepperRobot()
    setup_signal_handlers(robot)

    if not robot.initialise():
        logger.error("Failed to initialise Pepper robot")
        return
    
    if not robot.start():
        logger.error("Failed to initialise Pepper robot application")
        robot.cleanup()
        return
    
    # Keep main thread alive
    logger.info("Pepper robot application running")
    try:
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        robot.cleanup()

if __name__ == "__main__":
    main()