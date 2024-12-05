class BBox:
    def __init__(self, xmin, ymin, width, height):
        self.xmin = xmin
        self.ymin = ymin
        self.width = width
        self.height = height

    def to_tuple(self):
        return (self.xmin, self.ymin, self.width, self.height)

    @staticmethod
    def from_detection(detection):
        xmin = int(detection['xmin'])
        ymin = int(detection['ymin'])
        width = int(detection['xmax']) - xmin
        height = int(detection['ymax']) - ymin
        return BBox(xmin, ymin, width, height)

    def compute_iou(self, other):
        x1 = max(self.xmin, other.xmin)
        y1 = max(self.ymin, other.ymin)
        x2 = min(self.xmin + self.width, other.xmin + other.width)
        y2 = min(self.ymin + self.height, other.ymin + other.height)

        inter_area = max(0, x2 - x1) * max(0, y2 - y1)
        self_area = self.width * self.height
        other_area = other.width * other.height

        union_area = self_area + other_area - inter_area
        return inter_area / union_area if union_area > 0 else 0
