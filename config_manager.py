import json
import os
from datetime import datetime

class ConfigManager:
    def __init__(self):
        self.config_file = "detection_config.json"
        self.default_config = {
            "model_size": "s",
            "detection_interval": 10,
            "confidence_threshold": 0.5,
            "save_screenshots": False,
            "auto_export": False,
            "camera_id": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    def save_config(self, config):
        try:
            config['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置出错: {e}")
            return False
            
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 确保所有默认配置项都存在
                for key in self.default_config:
                    if key not in config:
                        config[key] = self.default_config[key]
                return config
            return self.default_config.copy()
        except Exception as e:
            print(f"加载配置出错: {e}")
            return self.default_config.copy()
    
    def update_config(self, key, value):
        """更新单个配置项"""
        try:
            config = self.load_config()
            config[key] = value
            return self.save_config(config)
        except Exception as e:
            print(f"更新配置出错: {e}")
            return False