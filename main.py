import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from models.model_manager import ModelManager
from utils.logger import Logger

def main():
    app = QApplication(sys.argv)
    
    # 初始化各个模块
    db_manager = DatabaseManager()
    model_manager = ModelManager()
    logger = Logger()
    
    # 创建主窗口
    window = MainWindow(db_manager, model_manager, logger)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 