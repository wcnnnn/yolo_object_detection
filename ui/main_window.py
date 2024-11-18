from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QVBoxLayout, QWidget,
                           QLabel, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPalette, QColor
from .components.video_display import VideoDisplay
from .components.control_panel import ControlPanel
from .components.visualization import VisualizationPanel
import qtawesome as qta

class MainWindow(QMainWindow):
    def __init__(self, db_manager, model_manager, logger):
        super().__init__()
        self.db_manager = db_manager
        self.model_manager = model_manager
        self.logger = logger
        self.init_ui()
        self.setup_connections()
        self.setup_update_timer()
        self.setup_styles()
        
    def init_ui(self):
        self.setWindowTitle("智能人脸检测系统")
        self.setWindowIcon(qta.icon('fa5s.desktop', color='#2c3e50'))
        self.setGeometry(100, 100, 1280, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 左侧视频显示
        video_container = QFrame()
        video_container.setFrameStyle(QFrame.StyledPanel)
        video_layout = QVBoxLayout()
        video_title_layout = QHBoxLayout()
        video_icon = QLabel()
        video_icon.setPixmap(qta.icon('fa5s.video', color='#2c3e50').pixmap(24, 24))
        video_title = QLabel("实时检测")
        video_title.setAlignment(Qt.AlignCenter)
        video_title_layout.addWidget(video_icon)
        video_title_layout.addWidget(video_title)
        video_title_layout.setAlignment(Qt.AlignCenter)
        video_title = QLabel("实时检测")
        video_title.setAlignment(Qt.AlignCenter)
        video_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        self.video_display = VideoDisplay(self.model_manager, self.db_manager)
        video_layout.addLayout(video_title_layout)
        video_layout.addWidget(self.video_display)
        video_container.setLayout(video_layout)
        
        # 右侧面板
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.StyledPanel)
        right_layout = QVBoxLayout()
        self.control_panel = ControlPanel(self.model_manager, self.logger, self.db_manager)
        self.visualization_panel = VisualizationPanel(self.db_manager)
        
        right_layout.addWidget(self.control_panel)
        right_layout.addWidget(self.visualization_panel)
        right_panel.setLayout(right_layout)
        
        # 设置比例
        main_layout.addWidget(video_container, 2)
        main_layout.addWidget(right_panel, 1)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
    def setup_connections(self):
        # 连接开始/停止按钮的信号
        self.control_panel.start_btn.clicked.connect(self.start_detection)
        self.control_panel.stop_btn.clicked.connect(self.stop_detection)
        
        # 连接检测信号到数据库和日志
        self.video_display.detection_signal.connect(self.handle_detection)

    def setup_update_timer(self):
        # 创建定时器用于更新可视化
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.visualization_panel.update_charts)
        self.update_timer.start(5000)  # 每5秒更新一次图表

    def start_detection(self):
        interval = self.control_panel.get_detection_interval()
        self.video_display.start_detection(interval)
        self.control_panel.start_detection()

    def stop_detection(self):
        self.video_display.stop_detection()
        self.control_panel.stop_detection()

    def handle_detection(self, class_name, x, y, confidence):
        # 更新数据库
        self.db_manager.add_detection(class_name, x, y, confidence)
        
        # 更新日志
        log_message = self.logger.log_detection(class_name, confidence)
        self.control_panel.update_log(log_message)

    def closeEvent(self, event):
        self.video_display.closeEvent(event)
        super().closeEvent(event)

    def setup_styles(self):
        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #bdc3c7;
            }
        """)