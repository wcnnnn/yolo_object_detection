import logging
import os
from datetime import datetime

class Logger:
    def __init__(self):
        # 创建logs文件夹（如果不存在）
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 设置日志文件路径
        log_file = os.path.join(log_dir, 'detection_logs.log')
        
        # 配置日志
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 同时输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # 获取根日志记录器并添加控制台处理程序
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
        
        logging.info("日志系统初始化完成")
        
    def log_detection(self, class_name, confidence):
        """记录检测结果"""
        message = f"检测到 {class_name}，置信度: {confidence:.2f}"
        logging.info(message)
        return message
        
    def log_error(self, error_message):
        """记录错误信息"""
        logging.error(f"错误: {error_message}")
        
    def log_warning(self, warning_message):
        """记录警告信息"""
        logging.warning(f"警告: {warning_message}")
        
    def log_info(self, info_message):
        """记录一般信息"""
        logging.info(info_message)