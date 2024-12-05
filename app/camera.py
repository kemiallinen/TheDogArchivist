from picamera2 import Picamera2

# CAMERA_SIZE = (1280, 720)
CAMERA_SIZE = (640, 480)

def initialize_camera():
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": CAMERA_SIZE, "format": "RGB888"}, controls={"FrameRate": 30})
    picam2.configure(config)
    picam2.start()
    return picam2
