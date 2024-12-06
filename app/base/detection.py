from .bbox import BBox
from .category import Category
import torch
import os
import yolov5
from app.logger import get_logger
logger = get_logger(__name__)
from app.config.config import Config
cfg = Config()


def load_model(model_path=cfg.get("detection.model_path")):
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
    
def filter_duplicate_detections(detections, iou_threshold=cfg.get("detection.iou_threshold")):
    unique_detections = []
    for i, detection in enumerate(detections):
        is_duplicate = any(detection.bbox.compute_iou(other.bbox) > iou_threshold for other in unique_detections)
        if not is_duplicate:
            unique_detections.append(detection)
    return unique_detections


class Detection:
    def __init__(self, bbox, category, confidence):
        self.bbox = bbox
        self.category = category
        self.confidence = confidence

    @staticmethod
    def from_row(row):
        bbox = BBox.from_detection(row)
        category = Category(row['name'])
        confidence = row['confidence']
        return Detection(bbox, category, confidence)

    def to_tuple(self):
        return (self.bbox.to_tuple(), self.category, self.confidence)
