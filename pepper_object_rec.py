import numpy as np
from object_detector import ObjectDetector

# Pepper IP address
ip_address = '192.168.x.x'

detector = ObjectDetector()

detector.start_video_stream(ip_address)
