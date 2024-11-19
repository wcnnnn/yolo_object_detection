from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QScreen, QGuiApplication
import qtawesome as qta

class FloatingButton(QPushButton):
    clicked_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = None  # 添加这行
        self.init_ui()
        
    def init_ui(self):
        # 设置按钮样式
        self.setIcon(qta.icon('fa5s.robot', color='white'))
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                border-radius: 25px;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        
        # 设置窗口标志
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # 将按钮放置在屏幕右侧中间位置
        self.position_button()
        
    def position_button(self):
        """将按钮定位到屏幕右侧中间位置"""
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = screen.width() - self.width() - 20
        y = screen.height() // 2 - self.height() // 2
        self.move(x, y)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.drag_position is None or (event.globalPos() - self.frameGeometry().topLeft() == self.drag_position):
                print("按钮被点击")  # 调试信息
                self.clicked_signal.emit()
            self.drag_position = None
        event.accept()