import tkinter as tk
from tkinter import messagebox, ttk
import cv2
from PIL import Image, ImageTk
from detector import YOLODetector
import threading
import queue
import time
from database import DatabaseManager
from visualization import Visualization
import os
from datetime import datetime
from config_manager import ConfigManager
import csv
import pandas as pd


class ObjectDetectionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO实时物体识别")
        self.root.geometry("1200x800")

        # 添加性能优化相关的属性 - 移到最前面
        self.last_frame_time = 0
        self.frame_delay = 33  # 约30FPS
        self.pending_frame_update = None

        # 更新主题色为更专业的配色
        self.theme_color = {
            'primary': '#1976D2',     # 深蓝主色调
            'secondary': '#F5F5F5',   # 浅灰背景色
            'accent': '#2196F3',      # 亮蓝强调色
            'text': '#212121',        # 深灰文字
            'text_secondary': '#757575', # 次要文字
            'border': '#E0E0E0',      # 边框颜色
            'success': '#4CAF50',     # 成功状态色
            'warning': '#FFC107',     # 警状态色
            'error': '#F44336',       # 错误状态色
            'background': '#FFFFFF'    # 添加背景色
        }
        
        # 统一按钮样式
        self.button_style = {
            'font': ('Arial', 10),
            'relief': tk.FLAT,
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2',
            'borderwidth': 0,
            'highlightthickness': 0,
            'bg': self.theme_color['primary'],
            'fg': 'white',
            'activebackground': self.theme_color['accent']
        }
        
        # 统一标签样式
        self.label_style = {
            'font': ('Arial', 10),
            'bg': self.theme_color['secondary'],
            'fg': self.theme_color['text'],
            'padx': 5
        }
        
        # 更新主容器样式
        self.main_container = tk.Frame(
            self.root, 
            bg=self.theme_color['background'],
            padx=20,
            pady=20
        )
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 初始化数据库管理器
        self.db_manager = DatabaseManager()  # 确保这里也初始化了

        # 更新侧边栏样式
        self.sidebar_container = tk.Frame(
            self.main_container, 
            bg=self.theme_color['secondary'],
            width=250,
            relief=tk.RIDGE,
            bd=1
        )
        
        self.detector = YOLODetector(model_size='s')
        self.cap = cv2.VideoCapture(0)

        self.frame_queue = queue.Queue(maxsize=10)
        self.stop_event = threading.Event()
        self.detection_event = threading.Event()
        self.detection_event.set()

        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.capture_thread.start()

        self.last_detection_time = time.time()
        self.detection_interval = 10

        # 初始化可视化模块
        self.class_names = self.detector.get_class_names()
        self.visualization = Visualization(self.main_container, self.class_names)

        # 添加配置管理器
        self.config_manager = ConfigManager()
        
        # 加载配置
        config = self.config_manager.load_config()
        self.detection_interval = config['detection_interval']
        self.confidence_threshold = config['confidence_threshold']
        
        # 初始化检测器时使用配置的模型大小
        self.detector = YOLODetector(
            model_size=config['model_size'],
            conf_threshold=config['confidence_threshold']
        )

        # 添加视频相关的属性
        self.cap = None
        self.current_frame = None
        self.last_frame_time = 0
        self.frame_delay = 33  # 约30FPS
        self.pending_frame_update = None
        
        # 创建事件标志
        self.stop_event = threading.Event()
        self.detection_event = threading.Event()
        
        # 创建界面
        self.create_widgets()
        
        # 启动视频捕获
        self.start_capture()
        
        # 添加性能优化相关的属性
        self.last_frame_time = 0
        self.frame_delay = 33  # 约30FPS
        self.pending_frame_update = None
    
        # 启动统计更新定时器
        self.root.after(1000, self.update_stats)  # 每秒更新一次统计
    
    def create_widgets(self):
        """创建所有界面元素"""
        # 创建主框架
        self.main_frame = tk.Frame(
            self.main_container,
            bg=self.theme_color['background']
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建视频显示区域
        self.create_video_frame()
        
        # 创建右侧控制面板
        self.create_control_panel()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_control_panel(self):
        """创建右侧控制面板"""
        # 创建控制面板主框架
        self.control_frame = tk.Frame(
            self.main_frame,
            bg=self.theme_color['secondary'],
            width=300
        )
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.control_frame.pack_propagate(False)
        
        # 添加标题
        self.control_title = tk.Label(
            self.control_frame,
            text="控制面板",
            font=('Arial', 12, 'bold'),
            bg=self.theme_color['secondary'],
            fg=self.theme_color['primary']
        )
        self.control_title.pack(pady=(0, 10))
        
        # 创建各个控制区域
        self.create_control_buttons()    # 控制按钮
        self.create_settings_frame()     # 检测设置
        self.create_stats_control_frame()  # 统计控制
        self.create_export_frame()       # 数据导出
        self.create_log_frame()          # 日志区域
    
    def create_control_buttons(self):
        """创建控制按钮"""
        # 按钮容器
        self.button_frame = tk.Frame(
            self.control_frame,
            bg=self.theme_color['secondary']
        )
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # 开始按钮
        start_button_style = self.button_style.copy()
        start_button_style.update({
            'bg': self.theme_color['success'],
            'activebackground': '#43A047'
        })
        
        self.start_button = tk.Button(
            self.button_frame,
            text="开始检测",
            command=self.start_detection,
            **start_button_style
        )
        self.start_button.pack(fill=tk.X, pady=2)
        
        # 停止按钮
        stop_button_style = self.button_style.copy()
        stop_button_style.update({
            'bg': self.theme_color['error'],
            'activebackground': '#E53935'
        })
        
        self.stop_button = tk.Button(
            self.button_frame,
            text="停止检测",
            command=self.stop_detection,
            state=tk.DISABLED,
            **stop_button_style
        )
        self.stop_button.pack(fill=tk.X, pady=2)
    
    def create_settings_frame(self):
        """创建设置区域"""
        self.settings_frame = tk.LabelFrame(
            self.control_frame,
            text="检测设置",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text'],
            font=('Arial', 10, 'bold'),
            padx=5,
            pady=5
        )
        self.settings_frame.pack(fill=tk.X, pady=10)
        
        # 检测间隔设置
        interval_frame = tk.Frame(
            self.settings_frame,
            bg=self.theme_color['secondary']
        )
        interval_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            interval_frame,
            text="检测间隔(秒):",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text']
        ).pack(side=tk.LEFT)
        
        self.time_entry = tk.Entry(
            interval_frame,
            width=8,
            justify=tk.CENTER
        )
        self.time_entry.insert(0, str(self.detection_interval))
        self.time_entry.pack(side=tk.LEFT, padx=5)
        
        # 模型大小选择
        model_frame = tk.Frame(
            self.settings_frame,
            bg=self.theme_color['secondary']
        )
        model_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            model_frame,
            text="模型大小:",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text']
        ).pack(side=tk.LEFT)
        
        self.model_size_var = tk.StringVar(value=self.detector.model_size)
        self.model_size_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_size_var,
            values=['n', 's', 'm', 'l', 'x'],
            width=6,
            state='readonly'
        )
        self.model_size_combo.pack(side=tk.LEFT, padx=5)
    
    def create_stats_control_frame(self):
        """创建统计控制区域"""
        self.stats_control_frame = tk.LabelFrame(
            self.control_frame,
            text="统计控制",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text'],
            font=('Arial', 10, 'bold'),
            padx=5,
            pady=5
        )
        self.stats_control_frame.pack(fill=tk.X, pady=10)
        
        # 统计图按钮
        self.visualize_button = tk.Button(
            self.stats_control_frame,
            text="显示统计图",
            command=self.visualization.toggle,
            **self.button_style
        )
        self.visualize_button.pack(fill=tk.X, pady=(5, 5))
        
        # 删除统计按钮
        delete_button_style = self.button_style.copy()
        delete_button_style.update({
            'bg': self.theme_color['error'],
            'activebackground': '#E53935',
            'fg': 'white'
        })
        
        self.delete_today_button = tk.Button(
            self.stats_control_frame,
            text="删除今日统计",
            command=self.delete_today_stats,
            **delete_button_style
        )
        self.delete_today_button.pack(fill=tk.X, pady=(0, 5))
    
    def create_export_frame(self):
        """创建导出控制区域"""
        self.export_frame = tk.LabelFrame(
            self.control_frame,
            text="数据导出",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text'],
            font=('Arial', 10, 'bold'),
            padx=5,
            pady=5
        )
        self.export_frame.pack(fill=tk.X, pady=10)
        
        # 日期选择框架
        date_frame = tk.Frame(self.export_frame, bg=self.theme_color['secondary'])
        date_frame.pack(fill=tk.X, pady=2)
        
        # 起始日期
        start_date_frame = tk.Frame(date_frame, bg=self.theme_color['secondary'])
        start_date_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            start_date_frame,
            text="起始日期:",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text']
        ).pack(side=tk.LEFT)
        
        self.start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.start_date_entry = tk.Entry(
            start_date_frame,
            textvariable=self.start_date_var,
            width=10
        )
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        
        # 结束日期
        end_date_frame = tk.Frame(date_frame, bg=self.theme_color['secondary'])
        end_date_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            end_date_frame,
            text="结束日期:",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text']
        ).pack(side=tk.LEFT)
        
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.end_date_entry = tk.Entry(
            end_date_frame,
            textvariable=self.end_date_var,
            width=10
        )
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        
        # 导出按钮
        export_button_style = self.button_style.copy()
        export_button_style.update({
            'bg': self.theme_color['primary'],
            'activebackground': '#1565C0'
        })
        
        self.export_csv_button = tk.Button(
            self.export_frame,
            text="导出CSV",
            command=self.export_to_csv,
            **export_button_style
        )
        self.export_csv_button.pack(fill=tk.X, pady=2)
        
        self.export_excel_button = tk.Button(
            self.export_frame,
            text="导出Excel",
            command=self.export_to_excel,
            **export_button_style
        )
        self.export_excel_button.pack(fill=tk.X, pady=2)
    
    def create_tooltip(self, widget, text):
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # 创建工具提示窗口
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(
                self.tooltip,
                text=text,
                justify=tk.LEFT,
                background="#ffffe0",
                relief=tk.SOLID,
                borderwidth=1,
                font=("Arial", "8", "normal"),
                padx=5,
                pady=2
            )
            label.pack()
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
            
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
    
    def toggle_sidebar(self):
        if self.sidebar_container.winfo_ismapped():
            self.sidebar_container.pack_forget()
            self.toggle_sidebar_button.config(text="显示侧边栏")
        else:
            self.sidebar_container.pack(side=tk.RIGHT, fill=tk.Y)
            self.toggle_sidebar_button.config(text="隐藏侧边栏")

    def capture_frames(self):
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))  # 降低分辨率以减少计算量
                self.frame_queue.put(frame)

    def update_frame(self):
        """更新视频帧"""
        try:
            current_time = time.time()
            if current_time - self.last_frame_time >= self.frame_delay / 1000:
                ret, frame = self.cap.read()
                if ret:
                    # 调整帧大小以适应显示区域
                    frame = cv2.resize(frame, (800, 600))
                    
                    # 如果检测事件被设置，执行检测
                    if self.detection_event.is_set():
                        detections = self.detector.detect(frame)
                        frame = self.detector.draw_detections(frame, detections)
                        self.update_database(detections)
                        self.log_detection(detections)
                    
                    # 转换颜色空间并创建PhotoImage
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.current_frame = frame  # 保存当前帧
                    image = Image.fromarray(frame_rgb)
                    photo = ImageTk.PhotoImage(image=image)
                    
                    # 更新画布
                    self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                    self.canvas.photo = photo
                    
                    self.last_frame_time = current_time
                    
            # 安排下一次更新
            self.pending_frame_update = self.root.after(1, self.update_frame)
                
        except Exception as e:
            print(f"Frame update error: {e}")
            if self.cap is not None and self.cap.isOpened():
                self.pending_frame_update = self.root.after(100, self.update_frame)

    def start_capture(self):
        """启动视频捕获"""
        try:
            self.cap = cv2.VideoCapture(0)  # 使用默认摄像头
            if not self.cap.isOpened():
                raise RuntimeError("无法打开摄像头")
            
            # 设置摄像头分辨率
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
            
            # 开始更新帧
            self.update_frame()
            
        except Exception as e:
            self.update_status(f"摄像头启动失败: {str(e)}", "error")
            messagebox.showerror("错误", f"摄像头启动失败: {str(e)}")

    def start_detection(self):
        self.detection_event.set()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_detection_interval()

    def stop_detection(self):
        self.detection_event.clear()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_detection_interval(self):
        try:
            self.detection_interval = float(self.time_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, "10")
            self.detection_interval = 10
    def update_database(self, detections):
        """更新检测结果到数据库"""
        try:
            for class_name, _, _ in detections:
                self.db_manager.update_detection_count(class_name)
        except Exception as e:
            print(f"Database update error: {e}")

    def log_detection(self, detections):
        for detection in detections:
            class_name, confidence, box = detection[:3]  # 只解包前三个值
            log_message = f"检测到 {class_name} (置信度: {confidence:.2f})"
            self.log_text.insert(tk.END, log_message + "\n")
            self.log_text.see(tk.END)

    def update_stats(self):
        """更新统计图表"""
        try:
            # 获取今日统计数据
            stats = self.db_manager.get_detection_counts()
            # 更新图表
            self.visualization.update_chart(stats)
        except Exception as e:
            print(f"Stats update error: {e}")
        finally:
            # 继续定时更新
            self.root.after(1000, self.update_stats)

    def apply_settings(self):
        try:
            # 获取新的模型大小
            new_model_size = self.model_size_var.get()
            
            # 暂停当前检测
            was_detecting = self.detection_event.is_set()
            if was_detecting:
                self.detection_event.clear()
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
            
            # 显示加载提示
            self.status_bar.config(text="正在加载新模型...", fg=self.theme_color['warning'])
            self.root.update()
            
            # 创建新的检测器
            try:
                new_detector = YOLODetector(model_size=new_model_size)
                
                # 如果新模型加载成功，更新当前检测器
                self.detector = new_detector
                self.class_names = self.detector.get_class_names()
                
                # 更新可视化模块的类别名称
                self.visualization.class_names = self.class_names
                
                # 显示成功消息
                self.status_bar.config(
                    text=f"模型已更改为: yolov8{new_model_size}.pt",
                    fg=self.theme_color['success']
                )
                
                # 如果之前在检测，恢复检测状态
                if was_detecting:
                    self.detection_event.set()
                    self.start_button.config(state=tk.DISABLED)
                    self.stop_button.config(state=tk.NORMAL)
                    
            except Exception as e:
                # 如果加载失败，恢复原来的模型大小
                self.model_size_var.set(self.detector.model_size)
                error_msg = f"模型加载失败: {str(e)}"
                messagebox.showerror("错误", error_msg)
                self.status_bar.config(text=error_msg, fg=self.theme_color['error'])
                
                # 如果之前在检测，尝试恢检测
                if was_detecting:
                    self.detection_event.set()
                    self.start_button.config(state=tk.DISABLED)
                    self.stop_button.config(state=tk.NORMAL)
                    
        except Exception as e:
            messagebox.showerror("错误", f"设置应用失败: {str(e)}")
            self.status_bar.config(text="设置应用失败", fg=self.theme_color['error'])

    def toggle_visualization(self):
        self.visualization.toggle()

    def delete_today_stats(self):
        confirm = messagebox.askyesno("确认删除", "确定要删除今日的统计数据吗？")
        if confirm:
            self.db_manager.delete_today_stats()
            self.update_stats()
            self.status_bar.config(text="今日统计数据已删除")

    def close(self):
        """关闭应用程序"""
        try:
            # 停止视频更新
            if self.pending_frame_update:
                self.root.after_cancel(self.pending_frame_update)
            
            # 停止检测
            self.detection_event.clear()
            
            # 放摄像头
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
            
            # 清理其他资源
            if hasattr(self, 'visualization'):
                self.visualization.cleanup()
            
            # 销毁窗口
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
    def update_status(self, message, status_type='info'):
        """更新状态栏信息"""
        status_colors = {
            'info': self.theme_color['text'],
            'success': self.theme_color['success'],
            'warning': self.theme_color['warning'],
            'error': self.theme_color['error']
        }
        
        self.status_bar.config(
            text=message,
            fg=status_colors.get(status_type, self.theme_color['text'])
        )
        
    def show_loading(self, message="加载中..."):
        """显示加载动画"""
        self.loading_dots = 0
        
        def update_dots():
            if hasattr(self, 'loading_dots'):
                self.loading_dots = (self.loading_dots + 1) % 4
                dots = "." * self.loading_dots
                self.status_bar.config(text=f"{message}{dots}")
                self.loading_timer = self.root.after(500, update_dots)
        
        update_dots()

    def hide_loading(self):
        """隐藏加载动画"""
        if hasattr(self, 'loading_timer'):
            self.root.after_cancel(self.loading_timer)
            delattr(self, 'loading_dots')

    def capture_screenshot(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{timestamp}.jpg"
            
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            current_frame = self.current_frame.copy()
            cv2.imwrite(f"screenshots/{filename}", current_frame)
            self.update_status(f"截图已保存: {filename}", "success")
        except Exception as e:
            self.update_status(f"截图保存失败: {str(e)}", "error")

    def create_config_frame(self):
        """创建配置面板"""
        self.config_frame = tk.LabelFrame(
            self.control_frame,
            text="配置设置",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text'],
            font=('Arial', 10, 'bold'),
            padx=5,
            pady=5
        )
        self.config_frame.pack(fill=tk.X, pady=10)

        # 置信度阈值设置
        conf_frame = tk.Frame(self.config_frame, bg=self.theme_color['secondary'])
        conf_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            conf_frame,
            text="置信度阈值:",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text']
        ).pack(side=tk.LEFT)
        
        self.conf_var = tk.StringVar(value=str(self.config_manager.load_config()['confidence_threshold']))
        conf_entry = tk.Entry(
            conf_frame,
            textvariable=self.conf_var,
            width=6,
            justify=tk.CENTER
        )
        conf_entry.pack(side=tk.LEFT, padx=5)
        
        # 自动截图开关
        self.auto_screenshot_var = tk.BooleanVar(
            value=self.config_manager.load_config()['save_screenshots']
        )
        tk.Checkbutton(
            self.config_frame,
            text="自动保存截图",
            variable=self.auto_screenshot_var,
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text'],
            command=lambda: self.config_manager.update_config('save_screenshots', 
                                                            self.auto_screenshot_var.get())
        ).pack(fill=tk.X)
        
        # 自动导出开关
        self.auto_export_var = tk.BooleanVar(
            value=self.config_manager.load_config()['auto_export']
        )
        tk.Checkbutton(
            self.config_frame,
            text="自动导出数据",
            variable=self.auto_export_var,
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text'],
            command=lambda: self.config_manager.update_config('auto_export', 
                                                            self.auto_export_var.get())
        ).pack(fill=tk.X)
        
        # 保存配置按钮
        save_button_style = self.button_style.copy()
        save_button_style.update({
            'bg': self.theme_color['success'],
            'activebackground': '#43A047'
        })
        
        tk.Button(
            self.config_frame,
            text="保存配置",
            command=self.save_current_config,
            **save_button_style
        ).pack(fill=tk.X, pady=5)

    def save_current_config(self):
        """保存当前配置"""
        try:
            config = {
                'model_size': self.model_size_var.get(),
                'detection_interval': float(self.time_entry.get()),
                'confidence_threshold': float(self.conf_var.get()),
                'save_screenshots': self.auto_screenshot_var.get(),
                'auto_export': self.auto_export_var.get(),
                'camera_id': 0  # 默认摄像头
            }
            
            if self.config_manager.save_config(config):
                self.update_status("配置已保存", "success")
            else:
                self.update_status("配置保存失败", "error")
        except ValueError as e:
            self.update_status("请输入有效的数值", "error")
        except Exception as e:
            self.update_status(f"保存配置时出错: {str(e)}", "error")

    def export_to_csv(self):
        """导出数据到CSV文件"""
        try:
            start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").date()
            
            if not os.path.exists("exports"):
                os.makedirs("exports")
            
            filename = f"detection_stats_{start_date}_{end_date}.csv"
            filepath = os.path.join("exports", filename)
            
            # 获取数据
            records = self.db_manager.get_history_records(start_date, end_date)
            
            # 写入CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['日期', '类别', '检测次数'])
                for record in records:
                    writer.writerow(record)
                
            self.update_status(f"数据已导出到: {filename}", "success")
            
        except ValueError:
            self.update_status("请输入有效的日期格式 (YYYY-MM-DD)", "error")
        except Exception as e:
            self.update_status(f"导出失败: {str(e)}", "error")

    def export_to_excel(self):
        """导出数据到Excel文件"""
        try:
            start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").date()
            
            if not os.path.exists("exports"):
                os.makedirs("exports")
            
            filename = f"detection_stats_{start_date}_{end_date}.xlsx"
            filepath = os.path.join("exports", filename)
            
            # 获取数据
            records = self.db_manager.get_history_records(start_date, end_date)
            
            # 创建DataFrame
            df = pd.DataFrame(records, columns=['日期', '类别', '检测次数'])
            
            # 导出到Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            self.update_status(f"数据已导出到: {filename}", "success")
            
        except ValueError:
            self.update_status("请输入有效的日期格式 (YYYY-MM-DD)", "error")
        except Exception as e:
            self.update_status(f"导出失败: {str(e)}", "error")

    def create_log_frame(self):
        """创建日志区域"""
        self.log_frame = tk.LabelFrame(
            self.control_frame,
            text="检测日志",
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text'],
            font=('Arial', 10, 'bold'),
            padx=5,
            pady=5
        )
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建文本框和滚动条
        self.log_text = tk.Text(
            self.log_frame,
            height=10,
            width=30,
            bg='white',
            fg=self.theme_color['text'],
            font=('Arial', 9),
            wrap=tk.WORD
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.log_scrollbar = tk.Scrollbar(
            self.log_frame,
            orient=tk.VERTICAL,
            command=self.log_text.yview
        )
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text.config(yscrollcommand=self.log_scrollbar.set)
        
        # 禁用文本框编辑
        self.log_text.config(state=tk.DISABLED)

    def log_message(self, message):
        """添加日志消息"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def log_detection(self, detections):
        """记录检测结果"""
        for detection in detections:
            class_name, confidence, _ = detection
            message = f"检测到 {class_name} (置信度: {confidence:.2f})"
            self.log_message(message)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Label(
            self.root,
            text="就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Arial', 9),
            bg=self.theme_color['secondary'],
            fg=self.theme_color['text'],
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message, status_type='info'):
        """更新状态栏信息"""
        status_colors = {
            'info': self.theme_color['text'],
            'success': self.theme_color['success'],
            'warning': self.theme_color['warning'],
            'error': self.theme_color['error']
        }
        
        self.status_bar.config(
            text=message,
            fg=status_colors.get(status_type, self.theme_color['text'])
        )

    def create_video_frame(self):
        """创建视频显示区域"""
        self.video_frame = tk.Frame(
            self.main_frame,
            bg=self.theme_color['border'],
            width=800,
            height=600
        )
        self.video_frame.pack(side=tk.LEFT, padx=(0, 20))
        self.video_frame.pack_propagate(False)
        
        # 创建画布用于显示视频
        self.canvas = tk.Canvas(
            self.video_frame,
            width=800,
            height=600,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ObjectDetectionUI(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()