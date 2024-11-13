# detector.py

import cv2
import torch
import numpy as np
from ultralytics import YOLO
from config import YOLO_CONFIG
from database import DatabaseManager

class YOLODetector:
    def __init__(self, model_size='s'):
        try:
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
        results = self.model(frame)
        if results:
            detections = results[0].boxes.data.cpu().numpy()
            self.update_database(detections)
            return detections
        else:
            return []

    def draw_detections(self, frame, detections):
        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection
            label = f'{self.classes[int(cls)]} {conf:.2f}'
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return frame

    def update_database(self, detections):
        for detection in detections:
            _, _, _, _, _, cls = detection
            class_name = self.classes[int(cls)]
            self.db_manager.update_detection_count(class_name)