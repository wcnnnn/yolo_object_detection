import mysql.connector
from datetime import datetime
import pandas as pd
import os

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'user': 'root',
            'password': 'wn159753',
            'host': '127.0.0.1',
            'port': 3306
        }
        # 首先创建数据库（如果不存在）
        self.create_database()
        
        # 更新配置以包含数据库名
        self.db_config['database'] = 'face_detection'
        self.connect()
        self.create_tables()
    
    def create_database(self):
        try:
            # 创建临时连接（不指定数据库）
            conn = mysql.connector.connect(
                user=self.db_config['user'],
                password=self.db_config['password'],
                host=self.db_config['host'],
                port=self.db_config['port']
            )
            cursor = conn.cursor()
            
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS face_detection")
            
            cursor.close()
            conn.close()
            
        except mysql.connector.Error as err:
            print(f"创建数据库错误: {err}")
            raise
    
    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"数据库连接错误: {err}")
            raise
    
    def create_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS detections (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    class_name VARCHAR(50),
                    timestamp DATETIME,
                    x_coord FLOAT,
                    y_coord FLOAT,
                    confidence FLOAT
                )
            ''')
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"创建表错误: {err}")
            raise
    
    def add_detection(self, class_name, x_coord, y_coord, confidence):
        try:
            sql = '''
                INSERT INTO detections (class_name, timestamp, x_coord, y_coord, confidence)
                VALUES (%s, %s, %s, %s, %s)
            '''
            self.cursor.execute(sql, (class_name, datetime.now(), x_coord, y_coord, confidence))
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"插入数据错误: {err}")
    
    def get_today_stats(self):
        try:
            sql = '''
                SELECT class_name, COUNT(*) as count
                FROM detections
                WHERE DATE(timestamp) = CURDATE()
                GROUP BY class_name
            '''
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"获取今日统计数据错误: {err}")
            return []

    def get_detection_stats(self, days=7):
        try:
            sql = '''
                SELECT class_name, COUNT(*) as count, DATE(timestamp) as date
                FROM detections
                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY class_name, DATE(timestamp)
            '''
            self.cursor.execute(sql, (days,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"获取检测统计数据错误: {err}")
            return []

    def get_position_data(self):
        try:
            sql = '''
                SELECT x_coord, y_coord
                FROM detections
                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY)
            '''
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"获取位置数据错误: {err}")
            return []

    def get_total_stats(self):
        try:
            sql = '''
                SELECT class_name, COUNT(*) as count
                FROM detections
                GROUP BY class_name
            '''
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"获取总体统计数据错误: {err}")
            return []
            
    def delete_today_data(self):
        """删除今日统计数据"""
        try:
            sql = '''
                DELETE FROM detections 
                WHERE DATE(timestamp) = CURDATE()
            '''
            self.cursor.execute(sql)
            self.conn.commit()
            return True, "今日数据已清除"
        except mysql.connector.Error as err:
            return False, f"删除数据错误: {err}"

    def export_data(self, export_type='excel'):
        """导出检测数据"""
        try:
            # 获取所有检测数据
            sql = '''
                SELECT class_name, timestamp, x_coord, y_coord, confidence
                FROM detections
                ORDER BY timestamp DESC
            '''
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            
            # 创建DataFrame
            df = pd.DataFrame(data, columns=[
                '检测类别', '检测时间', 'X坐标', 'Y坐标', '置信度'
            ])
            
            # 获取桌面路径
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_type == 'excel':
                filename = os.path.join(desktop, f'detection_data_{timestamp}.xlsx')
                df.to_excel(filename, index=False)
            else:  # csv
                filename = os.path.join(desktop, f'detection_data_{timestamp}.csv')
                df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            return True, f"数据已导出到: {filename}"
        except Exception as err:
            return False, f"导出数据错误: {err}"
            
    def __del__(self):
        """析构函数，确保关闭数据库连接"""
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()