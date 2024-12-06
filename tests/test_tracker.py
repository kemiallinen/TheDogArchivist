import unittest
from unittest.mock import MagicMock, patch
import datetime
import numpy as np
from app.base.tracker import OpenCVTracker, update_trackers_with_yolo
from app.base.bbox import BBox
from app.base.category import Category
from app.base.detection import Detection


class TestTracker(unittest.TestCase):

    def setUp(self):
        # Mock frame (black image)
        self.mock_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.tracker = OpenCVTracker()

    def test_add_tracker(self):
        bbox = BBox(100, 100, 50, 50)
        category = Category("dog")
        tracker_id = self.tracker.add_tracker(self.mock_frame, bbox, category)

        self.assertEqual(len(self.tracker.trackers), 1)
        self.assertIn(tracker_id, self.tracker.trackers)
        self.assertEqual(self.tracker.trackers[tracker_id].bbox, bbox)
        self.assertEqual(self.tracker.trackers[tracker_id].category, category)

    def test_update_trackers(self):
        bbox = BBox(100, 100, 50, 50)
        category = Category("dog")
        self.tracker.add_tracker(self.mock_frame, bbox, category)

        # Simulate update
        updated_trackers = self.tracker.update_trackers(self.mock_frame)
        self.assertEqual(len(updated_trackers), 1)

    def test_remove_inactive_tracker(self):
        bbox = BBox(100, 100, 50, 50)
        category = Category("dog")
        tracker_id = self.tracker.add_tracker(self.mock_frame, bbox, category)

        # Manually set `last_seen` to simulate inactivity
        self.tracker.trackers[tracker_id].last_seen -= datetime.timedelta(seconds=30)
        self.tracker.update_trackers(self.mock_frame)

        self.assertNotIn(tracker_id, self.tracker.trackers)

    def test_match_detections_to_trackers(self):
        # Add tracker
        bbox_tracker = BBox(100, 100, 50, 50)
        category_tracker = Category("dog")
        self.tracker.add_tracker(self.mock_frame, bbox_tracker, category_tracker)

        # Create detection
        bbox_detection = BBox(110, 110, 50, 50)
        category_detection = Category("dog")
        confidence_detection = 0.5
        detections = [Detection(bbox=bbox_detection, category=category_detection, confidence=confidence_detection)]

        # Match detections
        matched, unmatched_detections, unmatched_trackers = self.tracker.match_detections_to_trackers(detections)

        self.assertEqual(len(matched), 1)
        self.assertEqual(len(unmatched_detections), 0)
        self.assertEqual(len(unmatched_trackers), 0)

    def test_update_trackers_with_yolo(self):
        # Add tracker
        bbox_tracker = BBox(100, 100, 50, 50)
        category_tracker = Category("dog")
        tracker_id = self.tracker.add_tracker(self.mock_frame, bbox_tracker, category_tracker)

        # Create detections
        bbox_detection = BBox(110, 110, 50, 50)
        category_detection = Category("dog")
        confidence_detection = 0.5
        detections = [Detection(bbox=bbox_detection, category=category_detection, confidence=confidence_detection)]

        # Update trackers with YOLO detections
        trackers = update_trackers_with_yolo(self.mock_frame, detections, self.tracker)

        self.assertIn(tracker_id, trackers)
        self.assertEqual(trackers[tracker_id].bbox, bbox_detection)
