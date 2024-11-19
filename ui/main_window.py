from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QVBoxLayout, QWidget,
                           QLabel, QFrame, QPushButton)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QIcon, QPalette, QColor
from .components.video_display import VideoDisplay
from .components.control_panel import ControlPanel
from .components.visualization import VisualizationPanel
import qtawesome as qta
from chatbot.floating_button import FloatingButton
from chatbot.chat_window import ChatWindow
from chatbot.message_handler import MessageHandler
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QGuiApplication
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
        
        # 初始化聊天机器人
        self.init_chatbot()
        
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
        
        # 添加摄像头控制按钮到工具栏
        self.toolbar = self.addToolBar('Camera Control')
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("""
            QToolBar {
                spacing: 5px;
                padding: 5px;
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
        """)
        
        # 开启摄像头按钮
        self.start_camera_btn = QPushButton()
        self.start_camera_btn.setIcon(qta.icon('fa5s.video', color='white'))
        self.start_camera_btn.setToolTip('开启摄像头')
        self.start_camera_btn.clicked.connect(self.start_camera)
        self.start_camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 5px;
                padding: 8px;
                min-width: 40px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        # 关闭摄像头按钮
        self.stop_camera_btn = QPushButton()
        self.stop_camera_btn.setIcon(qta.icon('fa5s.video-slash', color='white'))
        self.stop_camera_btn.setToolTip('关闭摄像头')
        self.stop_camera_btn.clicked.connect(self.stop_camera)
        self.stop_camera_btn.setEnabled(False)
        self.stop_camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                border-radius: 5px;
                padding: 8px;
                min-width: 40px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

        # 添加按钮到工具栏
        self.toolbar.addWidget(self.start_camera_btn)
        self.toolbar.addWidget(self.stop_camera_btn)
        self.toolbar.addSeparator()

        # 连接视频显示组件的信号
        self.video_display.camera_status_signal.connect(self.update_camera_buttons)

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

    def init_chatbot(self):
        """初始化聊天机器人"""
        try:
            print("初始化聊天机器人...")
            # 创建悬浮按钮和聊天窗口
            self.float_btn = FloatingButton()
            self.chat_window = ChatWindow()
            
            # 创建消息处理器
            self.message_handler = MessageHandler(
                "sk-7a283ea1e5084e34b15dc59d332eacf8"
            )
            
            # 连接信号
            print("连接信号...")
            # 直接连接到方法
            self.float_btn.clicked_signal.connect(self.toggle_chat_window)
            self.chat_window.send_message.connect(self.handle_chat_message)
            self.chat_window.send_file.connect(self.handle_chat_file)
            
            # 显示悬浮按钮
            self.float_btn.show()
            print("悬浮按钮已显示")
            
            # 初始化时隐藏聊天窗口
            self.chat_window.hide()
            print("聊天窗口已初始化")
            
        except Exception as e:
            print(f"初始化聊天机器人时出错: {str(e)}")

    def toggle_chat_window(self):
        """切换聊天窗口显示状态"""
        try:
            print("触发切换聊天窗口...")  # 调试信息
            if not hasattr(self, 'chat_window') or not hasattr(self, 'float_btn'):
                print("聊天窗口或悬浮按钮未初始化")
                return
            
            if self.chat_window.isVisible():
                print("隐藏聊天窗口")
                self.chat_window.hide()
            else:
                print("准备显示聊天窗口")
                # 获取悬浮按钮的全局位置
                btn_global_pos = self.float_btn.mapToGlobal(QPoint(0, 0))
                print(f"按钮位置: {btn_global_pos.x()}, {btn_global_pos.y()}")
                
                # 计算聊天窗口位置
                chat_x = btn_global_pos.x() - self.chat_window.width() - 10
                chat_y = btn_global_pos.y() - (self.chat_window.height() // 2) + (self.float_btn.height() // 2)
                
                # 确保窗口不会超出屏幕边界
                screen = QGuiApplication.primaryScreen().availableGeometry()
                if chat_x < 0:
                    chat_x = btn_global_pos.x() + self.float_btn.width() + 10
                if chat_y < 0:
                    chat_y = 0
                if chat_y + self.chat_window.height() > screen.height():
                    chat_y = screen.height() - self.chat_window.height()
                
                print(f"设置窗口位置: {chat_x}, {chat_y}")
                self.chat_window.move(chat_x, chat_y)
                self.chat_window.show()
                self.chat_window.raise_()
                self.chat_window.activateWindow()
                print("聊天窗口已显示")
                
        except Exception as e:
            print(f"切换聊天窗口时出错: {str(e)}")

    def handle_chat_message(self, message: str):
        """处理聊天消息"""
        try:
            # 显示用户消息
            self.chat_window.add_message(message, True)
            
            # 使用流式处理
            try:
                for chunk in self.message_handler.handle_message_stream(message):
                    if chunk:  # 确保chunk不为空
                        self.chat_window.add_message(chunk, False, True)
                        QApplication.processEvents()  # 确保UI更新
                        
            except Exception as e:
                print(f"流式处理错误: {str(e)}")
                # 如果流式处理失败，尝试普通处理
                response = self.message_handler.handle_message(message)
                self.chat_window.add_message(response, False)
                
        except Exception as e:
            print(f"处理消息错误: {str(e)}")
            self.chat_window.add_message("抱歉，发生错误，请稍后重试。", False)
        
    def handle_chat_file(self, file_path: str):
        """处理文件上传"""
        # 显示上传消息
        self.chat_window.add_message(f"正在上传文件: {file_path}", True)
        
        # 处理文件
        response = self.message_handler.handle_file(file_path)
        
        # 显示处理结果
        self.chat_window.add_message(response, False)

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        self.float_btn.close()
        self.chat_window.close()
        super().closeEvent(event)

    def start_camera(self):
        """开启摄像头"""
        self.video_display.start_camera()
        self.logger.log_info("摄像头已开")

    def stop_camera(self):
        """关闭摄像头"""
        self.video_display.stop_camera()
        self.logger.log_info("摄像头已关闭")

    def update_camera_buttons(self, is_camera_on: bool):
        """更新摄像头控制按钮状态"""
        self.start_camera_btn.setEnabled(not is_camera_on)
        self.stop_camera_btn.setEnabled(is_camera_on)
        # 记录状态变化
        status = "开启" if is_camera_on else "关闭"
        self.logger.log_info(f"摄像头状态变更为：{status}")

    def init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
        
        # 添加摄像头状态标签
        self.camera_status_label = QLabel("摄像头：关闭")
        self.camera_status_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 3px;
            }
        """)
        self.status_bar.addPermanentWidget(self.camera_status_label)

        # 连接摄像头状态信号
        self.video_display.camera_status_signal.connect(self.update_camera_status)

    def update_camera_status(self, is_camera_on: bool):
        """更新摄像头状态显示"""
        status_text = "摄像头：开启" if is_camera_on else "摄像头：关闭"
        status_style = """
            QLabel {
                color: #4CAF50;
                padding: 3px;
            }
        """ if is_camera_on else """
            QLabel {
                color: #666;
                padding: 3px;
            }
        """
        self.camera_status_label.setText(status_text)
        self.camera_status_label.setStyleSheet(status_style)

    # 如果遇到错误时
    def handle_camera_error(self, error_message):
        """处理摄像头错误"""
        self.logger.log_error(f"摄像头错误：{error_message}")
        # 可以在这里添加错误处理逻辑，比如显示错误对话框等