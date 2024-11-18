from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QComboBox, QTextEdit, QLabel, QSpinBox, QStyle, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
import qtawesome as qta  # 需要先安装 qtawesome

class ControlPanel(QWidget):
    def __init__(self, model_manager, logger, db_manager):
        super().__init__()
        self.model_manager = model_manager
        self.logger = logger
        self.db_manager = db_manager
        self.init_ui()
        self.setup_styles()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题带图标
        title_layout = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.cog', color='#2c3e50').pixmap(32, 32))
        title_label = QLabel("控制面板")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)
        title_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(title_layout)
        
        # 模型选择区域
        model_group = QVBoxLayout()
        model_label = QLabel("选择模型:")
        model_label.setFont(QFont("Arial", 10))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            'YOLOv10-nano', 
            'YOLOv10-small', 
            'YOLOv10-medium', 
            'YOLOv10-large'
        ])
        # 添加下拉箭头图标
        self.model_combo.setStyleSheet("""
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        model_icon = qta.icon('fa5s.chevron-down', color='#4a90e2')
        self.model_combo.setItemIcon(0, qta.icon('fa5s.microchip', color='#3498db'))
        self.model_combo.setItemIcon(1, qta.icon('fa5s.microchip', color='#2ecc71'))
        self.model_combo.setItemIcon(2, qta.icon('fa5s.microchip', color='#e67e22'))
        self.model_combo.setItemIcon(3, qta.icon('fa5s.microchip', color='#e74c3c'))
        
        model_group.addWidget(model_label)
        model_group.addWidget(self.model_combo)
        main_layout.addLayout(model_group)
        
        # 检测间隔设置
        interval_layout = QHBoxLayout()
        interval_icon = QLabel()
        interval_icon.setPixmap(qta.icon('fa5s.clock', color='#2c3e50').pixmap(16, 16))
        interval_label = QLabel("检测间隔(ms):")
        interval_label.setFont(QFont("Arial", 10))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 5000)
        self.interval_spin.setValue(500)
        self.interval_spin.setSingleStep(100)
        
        interval_layout.addWidget(interval_icon)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spin)
        main_layout.addLayout(interval_layout)
        
        # 控制按钮区域
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始检测")
        self.stop_btn = QPushButton("停止检测")
        
        # 使用 QtAwesome 图标
        self.start_btn.setIcon(qta.icon('fa5s.play', color='white'))
        self.stop_btn.setIcon(qta.icon('fa5s.stop', color='white'))
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        main_layout.addLayout(button_layout)
        
        # 日志显示区域
        log_layout = QHBoxLayout()
        log_icon = QLabel()
        log_icon.setPixmap(qta.icon('fa5s.list', color='#2c3e50').pixmap(16, 16))
        log_label = QLabel("检测日志:")
        log_label.setFont(QFont("Arial", 10))
        log_layout.addWidget(log_icon)
        log_layout.addWidget(log_label)
        main_layout.addLayout(log_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        main_layout.addWidget(self.log_text)
        
        # 添加数据管理按钮组
        data_management_layout = QHBoxLayout()
        
        # 删除今日数据按钮
        self.delete_btn = QPushButton("删除今日数据")
        self.delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='white'))
        self.delete_btn.clicked.connect(self.delete_today_data)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        # 导出数据按钮
        self.export_btn = QPushButton("导出数据")
        self.export_btn.setIcon(qta.icon('fa5s.file-export', color='white'))
        self.export_btn.clicked.connect(self.show_export_options)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        data_management_layout.addWidget(self.delete_btn)
        data_management_layout.addWidget(self.export_btn)
        main_layout.addLayout(data_management_layout)
        
        self.setLayout(main_layout)
        
    def setup_styles(self):
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                color: #2c3e50;
            }
            QLabel {
                color: #34495e;
            }
        """)
        
    def get_detection_interval(self):
        """获取检测间隔时间"""
        return self.interval_spin.value()
        
    def start_detection(self):
        model_name = self.model_combo.currentText()
        if self.model_manager.load_model(model_name):
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.model_combo.setEnabled(False)
            self.interval_spin.setEnabled(False)
            self.log_text.append(f"已加载模型: {model_name}")
            self.log_text.append(f"检测间隔设置为: {self.get_detection_interval()}ms")
            
    def stop_detection(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.model_combo.setEnabled(True)
        self.interval_spin.setEnabled(True)
        self.log_text.append("检测已停止")
        
    def update_log(self, message):
        self.log_text.append(message)
        
    def delete_today_data(self):
        """删除今日数据"""
        reply = QMessageBox.question(self, '确认删除', 
                                   '确定要删除今日所有检测数据吗？',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, message = self.db_manager.delete_today_data()
            if success:
                QMessageBox.information(self, '成功', message)
                self.log_text.append(message)
            else:
                QMessageBox.warning(self, '错误', message)
                self.log_text.append(f"错误: {message}")

    def show_export_options(self):
        """显示导出选项"""
        export_menu = QMessageBox(self)
        export_menu.setWindowTitle("选择导出格式")
        export_menu.setText("请选择导出格式：")
        
        excel_button = export_menu.addButton("Excel", QMessageBox.ActionRole)
        csv_button = export_menu.addButton("CSV", QMessageBox.ActionRole)
        cancel_button = export_menu.addButton("取消", QMessageBox.RejectRole)
        
        export_menu.exec_()
        
        if export_menu.clickedButton() == excel_button:
            self.export_data('excel')
        elif export_menu.clickedButton() == csv_button:
            self.export_data('csv')

    def export_data(self, export_type):
        """导出数据"""
        success, message = self.db_manager.export_data(export_type)
        if success:
            QMessageBox.information(self, '成功', message)
            self.log_text.append(message)
        else:
            QMessageBox.warning(self, '错误', message)
            self.log_text.append(f"错误: {message}")