import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from app.base.detection import Detection, detect_objects, filter_duplicate_detections, load_model
from app.base.bbox import BBox
from app.base.category import Category


class TestDetection(unittest.TestCase):
    def setUp(self):
        self.mock_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.mock_model = MagicMock()

    @patch("app.base.detection.torch.hub.load")
    @patch("app.base.detection.os.path.isfile")
    def test_load_model_existing_path(self, mock_isfile, mock_hub_load):
        mock_isfile.return_value = True
        mock_hub_load.return_value = MagicMock()

        model_path = "./static/models/yolov5n.pt"
        model = load_model(model_path)

        mock_isfile.assert_called_with(model_path)
        self.assertIsNotNone(model)

    @patch("app.base.detection.torch.hub.load")
    @patch("app.base.detection.os.path.isfile")
    @patch("app.base.detection.torch.save")
    def test_load_model_download_model(self, mock_save, mock_isfile, mock_hub_load):
        mock_isfile.return_value = False
        mock_hub_load.return_value = MagicMock()

        model_path = "./static/models/yolov5n.pt"
        model = load_model(model_path)

        mock_isfile.assert_called_with(model_path)
        mock_hub_load.assert_called_with("ultralytics/yolov5", "yolov5n")
        mock_save.assert_called()

    def test_detect_objects(self):
        mock_results = MagicMock()
        mock_results.pandas.return_value.xyxy = [
            pd.DataFrame([
                {"xmin": 50, "ymin": 50, "xmax": 100, "ymax": 100, "confidence": 0.9, "name": "dog"},
                {"xmin": 150, "ymin": 150, "xmax": 200, "ymax": 200, "confidence": 0.85, "name": "cat"}
            ])
        ]
        self.mock_model.return_value = mock_results

        target_classes = ["dog"]
        detections = detect_objects(self.mock_model, self.mock_frame, target_classes)

        self.assertEqual(len(detections), 1)
        self.assertIsInstance(detections[0], Detection)
        self.assertEqual(detections[0].category, Category("dog"))

    def test_filter_duplicate_detections(self):
        bbox1 = BBox(50, 50, 100, 100)
        bbox2 = BBox(55, 55, 100, 100)
        bbox3 = BBox(200, 200, 50, 50)

        detection1 = Detection(bbox1, Category("dog"), 0.9)
        detection2 = Detection(bbox2, Category("dog"), 0.85)
        detection3 = Detection(bbox3, Category("dog"), 0.95)

        detections = [detection1, detection2, detection3]
        unique_detections = filter_duplicate_detections(detections, iou_threshold=0.5)

        self.assertEqual(len(unique_detections), 2)
        self.assertIn(detection1, unique_detections)
        self.assertIn(detection3, unique_detections)

    def test_detection_from_row(self):
        row = {
            "xmin": 50,
            "ymin": 50,
            "xmax": 100,
            "ymax": 100,
            "confidence": 0.9,
            "name": "dog"
        }
        detection = Detection.from_row(row)

        self.assertEqual(detection.bbox, BBox(50, 50, 50, 50))
        self.assertEqual(detection.category, Category("dog"))
        self.assertEqual(detection.confidence, 0.9)

    def test_detection_to_tuple(self):
        bbox = BBox(50, 50, 100, 100)
        category = Category("dog")
        detection = Detection(bbox, category, 0.9)

        detection_tuple = detection.to_tuple()
        self.assertEqual(detection_tuple, (bbox.to_tuple(), category, 0.9))


if __name__ == "__main__":
    unittest.main()
