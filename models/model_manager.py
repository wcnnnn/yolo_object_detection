from ultralytics import YOLO

class ModelManager:
    def __init__(self):
        self.available_models = {
            'YOLOv10-nano': 'yolov8n.pt',
            'YOLOv10-small': 'yolov8s.pt',
            'YOLOv10-medium': 'yolov8m.pt',
            'YOLOv10-large': 'yolov8l.pt'
        }
        self.current_model = None
        
    def load_model(self, model_name):
        try:
            if model_name in self.available_models:
                model_path = self.available_models[model_name]
                self.current_model = YOLO(model_path)
                return True
            return False
        except Exception as e:
            print(f"加载模型错误: {str(e)}")
            return False
    
    def detect(self, frame):
        try:
            if self.current_model:
                results = self.current_model(frame)
                return results
            return None
        except Exception as e:
            print(f"检测错误: {str(e)}")
            return None 