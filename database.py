import mysql.connector.pooling
from config import DB_CONFIG
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.db_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)

    def create_table(self):
        try:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detections (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    class_name VARCHAR(255),
                    count INT DEFAULT 0,
                    detection_date DATE
                )
            ''')
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error creating table: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def update_detection_count(self, class_name):
        try:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            today = datetime.today().date()
            cursor.execute('SELECT count FROM detections WHERE class_name = %s AND detection_date = %s', (class_name, today))
            result = cursor.fetchone()
            if result:
                count = result[0] + 1
                cursor.execute('UPDATE detections SET count = %s WHERE class_name = %s AND detection_date = %s', (count, class_name, today))
            else:
                cursor.execute('INSERT INTO detections (class_name, count, detection_date) VALUES (%s, 1, %s)', (class_name, today))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error updating detection count: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_detection_counts(self, date=None):
        """获取指定日期的检测统计数据"""
        try:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            
            if date is None:
                date = datetime.today().date()
            
            cursor.execute('''
                SELECT class_name, count 
                FROM detections 
                WHERE detection_date = %s
            ''', (date,))
            
            results = cursor.fetchall()
            stats = {row[0]: row[1] for row in results}
            return stats
            
        except mysql.connector.Error as err:
            print(f"Error getting detection counts: {err}")
            return {}
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def delete_today_stats(self):
        """删除今日的统计数据"""
        try:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            today = datetime.today().date()
            
            cursor.execute('DELETE FROM detections WHERE detection_date = %s', (today,))
            conn.commit()
            
        except mysql.connector.Error as err:
            print(f"Error deleting today's stats: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_history_records(self, start_date=None, end_date=None, class_name=None):
        try:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT detection_date, class_name, count FROM detections WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND detection_date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND detection_date <= %s"
                params.append(end_date)
            if class_name:
                query += " AND class_name = %s"
                params.append(class_name)
            
            query += " ORDER BY detection_date DESC"
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting history records: {err}")
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()