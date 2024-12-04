from flask import Blueprint, Response
from app.camera import initialize_camera
from app.detection import load_model, detect_objects
from app.tracker import OpenCVTracker, detect_and_track_objects
import cv2
import time

main = Blueprint("main", __name__)
camera = initialize_camera()
model = load_model()
tracker = OpenCVTracker()

@main.route("/")
def video_feed():
    def generate_frames():
        while True:
            frame = camera.capture_array()
            detections = detect_objects(model, frame, ["dog", "person", "bird", "building"])
            tracked_objects = detect_and_track_objects(frame, detections, tracker)

            # Rysowanie bounding boxów
            for obj_id, bbox in tracked_objects.items():
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"ID {obj_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.03)

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
