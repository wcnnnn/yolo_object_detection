# detector.py

import cv2
import torch
import numpy as np
from ultralytics import YOLO
from config import YOLO_CONFIG
from database import DatabaseManager

class YOLODetector:
    def __init__(self, model_size='s', conf_threshold=0.5):
        try:
            self.model_size = model_size
            self.conf_threshold = conf_threshold
            self.model = YOLO(f'yolov8{model_size}.pt')
            self.classes = self.model.names
            self.db_manager = DatabaseManager()
            self.db_manager.create_table()
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def detect(self, frame):
        if self.model is None:
            raise RuntimeError("Model not loaded")
        results = self.model(frame, conf=self.conf_threshold)
        if results:
            detections = []
            for result in results[0].boxes.data.cpu().numpy():
                x1, y1, x2, y2, conf, cls = result
                if conf >= self.conf_threshold:
                    class_name = self.classes[int(cls)]
                    detections.append((class_name, float(conf), [float(x1), float(y1), float(x2), float(y2)]))
            self.update_database(detections)
            return detections
        else:
            return []
    def update_database(self, detections):
        for class_name, _, _ in detections:
            self.db_manager.update_detection_count(class_name)
    def draw_detections(self, frame, detections):
        for class_name, conf, box in detections:
            x1, y1, x2, y2 = box
            label = f'{class_name} {conf:.2f}'
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return frame

    def get_class_names(self):
        return self.classes