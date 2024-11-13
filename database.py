import mysql.connector.pooling
from config import DB_CONFIG

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
                    count INT DEFAULT 0
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
            cursor.execute('SELECT count FROM detections WHERE class_name = %s', (class_name,))
            result = cursor.fetchone()
            if result:
                count = result[0] + 1
                cursor.execute('UPDATE detections SET count = %s WHERE class_name = %s', (count, class_name))
            else:
                cursor.execute('INSERT INTO detections (class_name, count) VALUES (%s, 1)', (class_name,))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error updating detection count: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_detection_counts(self):
        try:
            conn = self.db_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT class_name, count FROM detections')
            results = cursor.fetchall()
            return {class_name: count for class_name, count in results}
        except mysql.connector.Error as err:
            print(f"Error getting detection counts: {err}")
            return {}
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()