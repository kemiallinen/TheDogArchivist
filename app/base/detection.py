from .bbox import BBox
from .category import Category

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
