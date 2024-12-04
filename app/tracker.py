import cv2
import datetime

class OpenCVTracker:
    def __init__(self):
        self.trackers = {}
        self.next_id = 1
        self.max_time_gap = 10  # max time in seconds

    def add_tracker(self, frame, bbox):
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, bbox)
        obj_id = self.next_id
        self.trackers[obj_id] = (tracker, datetime.datetime.now())
        self.next_id += 1
        return obj_id

    def update_trackers(self, frame):
        updated_trackers = {}
        for obj_id, (tracker, last_seen) in self.trackers.items():
            success, bbox = tracker.update(frame)
            if success:
                updated_trackers[obj_id] = (tracker, datetime.datetime.now())
            elif (datetime.datetime.now() - last_seen).seconds < self.max_time_gap:
                updated_trackers[obj_id] = (tracker, last_seen)

        self.trackers = updated_trackers
        return {obj_id: bbox for obj_id, (tracker, _) in self.trackers.items()}


def detect_and_track_objects(frame, detections, tracker):
    bboxes = []
    for _, row in detections.iterrows():
        if row['name'] == 'dog':
            xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            bbox = (xmin, ymin, xmax - xmin, ymax - ymin)
            bboxes.append(bbox)

    tracked_bboxes = tracker.update_trackers(frame)
    for bbox in bboxes:
        if not is_bbox_tracked(bbox, tracked_bboxes):
            tracker.add_tracker(frame, bbox)

    return tracked_bboxes


def is_bbox_tracked(bbox, tracked_bboxes, iou_threshold=0.5):
    def compute_iou(box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[0] + box1[2], box2[0] + box2[2])
        y2 = min(box1[1] + box1[3], box2[1] + box2[3])
        inter_area = max(0, x2 - x1) * max(0, y2 - y1)
        box1_area = box1[2] * box1[3]
        box2_area = box2[2] * box2[3]
        iou = inter_area / float(box1_area + box2_area - inter_area)
        return iou

    for _, tracked_bbox in tracked_bboxes.items():
        if compute_iou(bbox, tracked_bbox) > iou_threshold:
            return True
    return False
