import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
from detector import YOLODetector
import threading
import queue
import time
from database import DatabaseManager

class ObjectDetectionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO实时物体识别")
        self.root.geometry("800x600")

        self.detector = YOLODetector(model_size='s')
        self.cap = cv2.VideoCapture(0)

        self.canvas = tk.Canvas(root, width=640, height=480)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        self.frame_queue = queue.Queue(maxsize=10)
        self.stop_event = threading.Event()
        self.detection_event = threading.Event()
        self.detection_event.set()  # 默认开始识别

        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.capture_thread.start()

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.start_button = tk.Button(self.control_frame, text="开始识别", command=self.start_detection)
        self.start_button.pack(side=tk.TOP, pady=10)

        self.stop_button = tk.Button(self.control_frame, text="停止识别", command=self.stop_detection)
        self.stop_button.pack(side=tk.TOP, pady=10)

        self.time_label = tk.Label(self.control_frame, text="识别时间间隔 (秒):")
        self.time_label.pack(side=tk.TOP, pady=10)

        self.time_entry = tk.Entry(self.control_frame, width=10)
        self.time_entry.pack(side=tk.TOP, pady=10)
        self.time_entry.insert(0, "10")  # 默认时间间隔为10秒

        self.last_detection_time = time.time()
        self.detection_interval = 10  # 默认每10秒钟识别一次

        self.db_manager = DatabaseManager()
        self.db_manager.create_table()

        self.stats_frame = tk.Frame(self.control_frame)
        self.stats_frame.pack(side=tk.TOP, pady=10)

        self.stats_labels = {}
        self.update_stats()

        self.update_frame()

    def capture_frames(self):
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))  # 降低分辨率以减少计算量
                self.frame_queue.put(frame)

    def update_frame(self):
        if not self.frame_queue.empty():
            frame = self.frame_queue.get()
            if self.detection_event.is_set() and time.time() - self.last_detection_time >= self.detection_interval:
                detections = self.detector.detect(frame)
                frame = self.detector.draw_detections(frame, detections)
                self.last_detection_time = time.time()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.imgtk = imgtk
        self.root.after(10, self.update_frame)

    def start_detection(self):
        self.detection_event.set()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_detection_interval()

    def stop_detection(self):
        self.detection_event.clear()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_detection_interval(self):
        try:
            self.detection_interval = float(self.time_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, "10")
            self.detection_interval = 10

    def update_stats(self):
        stats = self.db_manager.get_detection_counts()
        for class_name, count in stats.items():
            if class_name not in self.stats_labels:
                label = tk.Label(self.stats_frame, text=f"{class_name}: {count}")
                label.pack(side=tk.TOP, anchor=tk.W)
                self.stats_labels[class_name] = label
            else:
                self.stats_labels[class_name].config(text=f"{class_name}: {count}")
        self.root.after(1000, self.update_stats)  # 每秒更新一次统计数据

    def close(self):
        self.stop_event.set()
        self.capture_thread.join()
        self.cap.release()
        self.root.destroy()
