import cv2
import datetime
from .bbox import BBox
from .category import Category
from app.logger import get_logger
logger = get_logger(__name__)
from app.config.config import Config
cfg = Config()

class Tracker:
    def __init__(self, obj_id, bbox, category, frame, max_time_gap=cfg.get("tracker.max_time_gap")):
        self.obj_id: int = obj_id
        self.bbox: BBox = bbox
        self.category: Category = category
        self.last_seen = datetime.datetime.now()
        self.max_time_gap = max_time_gap
        self.tracker = cv2.TrackerCSRT_create()
        self.tracker.init(frame, bbox.to_tuple())

    def update(self, frame):
        success, bbox = self.tracker.update(frame)
        if success:
            self.bbox = BBox(*bbox)
            self.last_seen = datetime.datetime.now()
        return success

    def is_active(self):
        return (datetime.datetime.now() - self.last_seen).seconds <= self.max_time_gap

class OpenCVTracker:
    def __init__(self):
        self.trackers = {}
        self.next_id = 1

    def add_tracker(self, frame, bbox, category):
        tracker = Tracker(self.next_id, bbox, category, frame)
        self.trackers[self.next_id] = tracker
        self.next_id += 1
        return tracker.obj_id

    def update_trackers(self, frame):
        active_trackers = {}
        for obj_id, tracker in self.trackers.items():
            success = tracker.update(frame)
            if success and tracker.is_active():
                active_trackers[obj_id] = tracker
                # logger.info(f"Tracker {obj_id} updated: {tracker.bbox.to_tuple()}")
            elif not success:
                logger.warning(f"Tracker {obj_id} failed to update.")
            elif not tracker.is_active():
                self.remove_tracker(obj_id)
                logger.info(f"Tracker {obj_id} inactive and removed.")

        self.trackers = {obj_id: tracker for obj_id, tracker in active_trackers.items()}
        return active_trackers

    def remove_tracker(self, obj_id):
        if obj_id in self.trackers:
            del self.trackers[obj_id]
    
    def get_all_bboxes(self, frame):
        bboxes = {}
        for obj_id, tracker in self.trackers.items():
            if tracker.update(frame):
                bboxes[obj_id] = tracker
        return bboxes

    def match_detections_to_trackers(self, detections, iou_threshold=cfg.get("detection.iou_threshold")):
        matched = []
        unmatched_detections = []
        unmatched_trackers = list(self.trackers.keys())

        for detection in detections:
            best_match = None
            best_iou = 0

            for tracker_id in unmatched_trackers:
                tracker = self.trackers[tracker_id]
                iou = detection.bbox.compute_iou(tracker.bbox)
                if iou > best_iou and iou >= iou_threshold:
                    best_match = tracker_id
                    best_iou = iou

            if best_match is not None:
                matched.append((best_match, detection))
                unmatched_trackers.remove(best_match)
            else:
                unmatched_detections.append(detection)

        return matched, unmatched_detections, unmatched_trackers


def update_trackers_with_yolo(frame, detections, tracker):
    matched, unmatched_detections, unmatched_trackers = tracker.match_detections_to_trackers(detections)

    for tracker_id, detection in matched:
        tracker.trackers[tracker_id].bbox = detection.bbox
        tracker.trackers[tracker_id].last_seen = datetime.datetime.now()

    for detection in unmatched_detections:
        tracker.add_tracker(frame, detection.bbox, detection.category)

    for tracker_id in unmatched_trackers:
        tracker.remove_tracker(tracker_id)
        logger.info(f"Tracker {tracker_id} removed due to no match.")

    return tracker.trackers
