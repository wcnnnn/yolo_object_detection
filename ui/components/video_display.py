from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np

class VideoDisplay(QWidget):
    detection_signal = pyqtSignal(str, float, float, float)

    def __init__(self, model_manager, db_manager):
        super().__init__()
        self.model_manager = model_manager
        self.db_manager = db_manager
        self.is_detecting = False
        self.capture = None
        self.timer = None
        self.init_ui()
        self.setup_camera()
        self.start_preview()

    def init_ui(self):
        layout = QVBoxLayout()
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        layout.addWidget(self.video_label)
        self.setLayout(layout)

    def setup_camera(self):
        if self.capture is None:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                print("无法打开摄像头")
                return False
        if self.timer is None:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
        return True

    def start_preview(self):
        if self.setup_camera():
            self.timer.start(30)
            print("开始预览")

    def start_detection(self, interval):
        self.is_detecting = True
        print("开始检测，间隔：", interval)

    def stop_detection(self):
        self.is_detecting = False
        print("停止检测")

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            if self.is_detecting:
                results = self.model_manager.detect(frame)
                if results and len(results) > 0:
                    frame = self.draw_detections(frame, results)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.video_label.size(), Qt.KeepAspectRatio)
            self.video_label.setPixmap(scaled_pixmap)

    def draw_detections(self, frame, results):
        if results and len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = results[0].names[cls]

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                label = f"{class_name}: {conf:.2f}"
                cv2.putText(frame, label, (int(x1), int(y1)-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                center_x = (x1 + x2) / 2 / frame.shape[1]
                center_y = (y1 + y2) / 2 / frame.shape[0]
                self.detection_signal.emit(class_name, center_x, center_y, conf)

        return frame

    def closeEvent(self, event):
        if self.capture is not None:
            self.capture.release()
        super().closeEvent(event)