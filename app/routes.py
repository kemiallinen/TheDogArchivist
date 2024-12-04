from flask import Blueprint, Response
from app.camera import initialize_camera
from app.detection import load_model, detect_objects
from app.tracker import OpenCVTracker, detect_and_track_objects
from app.logger import get_logger
import cv2
import time

main = Blueprint("main", __name__)
camera = initialize_camera()
model = load_model()
tracker = OpenCVTracker()
logger = get_logger(__name__)


@main.route("/")
def video_feed():
    logger.info("Starting video stream...")
    try:
        def generate_frames():
            while True:
                frame = camera.capture_array()
                detections = detect_objects(model, frame, ["dog", "person"])
                tracked_objects = detect_and_track_objects(frame, detections, tracker)

                for obj_id, bbox in tracked_objects.items():
                    x, y, w, h = [int(v) for v in bbox]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"ID {obj_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(0.03)

        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logger.error(f"Error while streaming: {e}")
        return Response(status=500)
