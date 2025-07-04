from flask import Blueprint, Response
from app.camera import initialize_camera
from app.base.detection import load_model, detect_objects, filter_duplicate_detections
from app.base.tracker import OpenCVTracker, update_trackers_with_yolo
from app.logger import get_logger
from app.config.config import Config
import cv2
import time

main = Blueprint("main", __name__)
camera = initialize_camera()
model = load_model()
tracker = OpenCVTracker()
logger = get_logger(__name__)
cfg = Config()


@main.route("/")
def video_feed():
    logger.info("Starting video stream...")
    try:
        def generate_frames():
            prev_time = time.time()
            frame_count = 0

            while True:
                frame = camera.capture_array()

                if frame_count % cfg.get("detection.detect_every_n_frames") == 0:
                    detections = detect_objects(model, frame, cfg.get("detection.classes"))
                    detections = filter_duplicate_detections(detections)
                    for detection in detections:
                        logger.info(f"Detections = {detection.to_tuple()}")
                    tracked_objects = update_trackers_with_yolo(frame, detections, tracker)
                else:
                    tracked_objects = tracker.update_trackers(frame)
                    
                for obj_id, tracker_obj in tracked_objects.items():
                    if not tracker_obj.bbox:
                        continue
                    
                    bbox = tracker_obj.bbox
                    category = tracker_obj.category

                    x, y, w, h = [int(v) for v in bbox.to_tuple()]

                    category_pl = category.to_plural()
                    if not category_pl:
                        continue

                    color = (0, 255, 0) if category == "dog" else (255, 0, 0)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"{category.capitalize()} ID {obj_id}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                current_time = time.time()
                elapsed_time = current_time - prev_time
                fps = 1 / elapsed_time if elapsed_time > 0 else 0
                prev_time = current_time

                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                frame_count += 1

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    except Exception as e:
        logger.error(f"Error while streaming: {e}")
        return Response(status=500)
