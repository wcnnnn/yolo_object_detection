# config.py

# 数据库配置
DB_CONFIG = {
    'user': 'root',
    'password': '',  
    'host': '',
    'port': ,
    'database': 'my_database',
    'pool_name': 'mypool',
    'pool_size': 5,
}

# YOLO模型配置
YOLO_CONFIG = {
    'model_path': 'yolov8s.pt',  # 使用 YOLOv8s 模型
    'confidence_threshold': 0.5,
    'nms_threshold': 0.4,
}
