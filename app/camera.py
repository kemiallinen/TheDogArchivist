from picamera2 import Picamera2
from app.config.config import Config

cfg = Config()

def initialize_camera():
    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={
            "size": cfg.get("camera.resolution"),
            "format": "RGB888"
            },
        controls={"FrameRate": cfg.get("camera.frame_rate")})
    picam2.configure(config)
    picam2.start()
    return picam2
