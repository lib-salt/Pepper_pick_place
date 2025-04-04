import socket
import logging
import time
from utils import logger

class NetworkListener:
    def __init__(self):
        # Initialise network listener
        self.location_sock = None
        self.running = False

    def initialise(self, server_ip, port):
        # Initialise object tracker socket
        try:
            self.location_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.location_sock.bind((server_ip, port))
            self.running = True
            logger.info("Network listener initialised on {}.{}".format(server_ip, port))
            return True
        
        except Exception as e:
            logger.error("Error initialising network listener: {}".format(e))

    def cleanup(self):
        # Cleanup network resources
        try:
            self.running = False
            if self.location_sock:
                self.location_sock.close()
            logger.info("Network listener cleaned up")

        except Exception as e:
            logger.error("Error during network listener cleanup: {}".format(e))

    def get_object_coords(self):
        try:
            if not self.running or not self.location_sock:
                logger.error("Network listener not initialised")
                return None, None, None
                       
            # Receive coordinate data
            data, _ = self.location_sock.recvfrom(1024)

            if not data:
                logger.warning("No data received from object detector")
                return None, None, None
            
            # Decode data from socket
            coords = data.decode().split(',')
            if len(coords) < 3:
                logger.warning("Invalid data format received: {}".format(data))
                return None, None, None
            
            x_cen = float(coords[0])
            y_cen = float(coords[1])
            category = str(coords[2])
            timestamp = float(coords[3])

            current_time = time.time()

            time_dif = current_time - timestamp

            # Check if co-ordinates are older than 2 seconds
            if time_dif > 2.0:
                logger.warning("No new object detected")
                return None, None, None

            logger.info("Detected {0} at coordinates ({1}, {2})".format(category, x_cen, y_cen))

            return x_cen, y_cen, category
        
        except Exception as e:
            logger.error("Failed to get coordinates: {}".format(e))
            return None, None, None
