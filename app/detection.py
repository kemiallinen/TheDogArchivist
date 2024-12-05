import torch
import os
import yolov5
from app.base.detection import Detection
from app.base.tracker import compute_iou
from app.logger import get_logger
logger = get_logger(__name__)


def load_model(model_path="./static/models/yolov5n.pt"):
    model = None
    try:
        if os.path.isfile(model_path):
            model = yolov5.load(model_path)
            logger.info(f"Model loaded from {model_path}")
        else:
            model = torch.hub.load("ultralytics/yolov5", "yolov5n")
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            torch.save(model, model_path)
            logger.info(f"Model downloaded and saved to {model_path}")
        model.eval()
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise RuntimeError(f"Model could not be loaded: {e}")
    return model

def detect_objects(model, frame, target_classes):
    try:
        results = model(frame)
        detections_df = results.pandas().xyxy[0]
        filtered_detections = detections_df[detections_df['name'].isin(target_classes)]

        detections = [
            Detection.from_row(row) for _, row in filtered_detections.iterrows()
        ]
        logger.info(f"Detected {len(detections)} objects matching target classes.")
        return detections
    except Exception as e:
        logger.error(f"Error detecting objects: {e}")
        return []
    
def filter_duplicate_detections(detections, iou_threshold=0.5):
    unique_detections = []
    for i, detection in enumerate(detections):
        is_duplicate = any(
            compute_iou(detection.bbox.to_tuple(), other.bbox.to_tuple()) > iou_threshold
            for other in unique_detections
        )
        if not is_duplicate:
            unique_detections.append(detection)
    return unique_detections
