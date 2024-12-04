import torch
import os
import yolov5

def load_model(model_path="./static/models/yolov5s.pt"):
    model = None
    if os.path.isfile(model_path):
        model = yolov5.load(model_path)
    else:
        model = torch.hub.load("ultralytics/yolov5", "yolov5s")
        os.rename("yolov5s.pt", "./static/models/yolov5s.pt")

    model.eval()
    return model

def detect_objects(model, frame, target_classes):
    results = model(frame)
    detections = results.pandas().xyxy[0]
    return detections[detections['name'].isin(target_classes)]