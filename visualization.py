import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import matplotlib.font_manager as fm
from matplotlib.figure import Figure
import os
import warnings
import scienceplots
import matplotlib
import time
# 设置后端为 'Agg'
matplotlib.use('Agg')
# 关闭交互模式
plt.ioff()

warnings.filterwarnings('ignore')

# 字体配置
font_dir = r'C:\Users\30766\anaconda3\envs\Tensorflow\Lib\site-packages\matplotlib\mpl-data\fonts\ttf'
font_files = fm.findSystemFonts(fontpaths=[font_dir])
for font_file in font_files:
    fm.fontManager.addfont(font_file)
fonts = [fm.FontProperties(fname=f).get_name() for f in font_files]
plt.style.use(['science', 'bright','no-latex','cjk-sc-font'])

class Visualization:
    def __init__(self, root, class_names):
        self.root = root
        self.class_names = class_names
        self.is_expanded = False
        self.target_width = 400
        self.min_width = 0
        self.animation_duration = 400
        self.animation_steps = 60
        
        # 添加防抖动控制
        self.last_resize_time = 0
        self.resize_delay = 50
        self.is_resizing = False
        self.pending_resize = None
        
        # 添加图表更新控制
        self.last_update_time = 0
        self.update_delay = 500
        self.pending_update = None
        self.last_update = time.time()
        self.update_interval = 1
        
        # 创建一个新窗口来容纳统计图
        self.stats_window = tk.Toplevel(self.root)
        self.stats_window.overrideredirect(True)
        self.stats_window.withdraw()
        self.stats_window.configure(bg='white', bd=1, relief=tk.RIDGE)
        
        # 创建标题栏
        self.title_bar = tk.Frame(self.stats_window, bg='#2196F3', height=30)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)
        
        # 标题
        self.title_label = tk.Label(
            self.title_bar, 
            text="检测统计", 
            bg='#2196F3',
            fg='white',
            font=('Arial', 10)
        )
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # 绑定拖动事件到标题栏
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.do_move)
        self.title_label.bind('<Button-1>', self.start_move)
        self.title_label.bind('<B1-Motion>', self.do_move)
        
        # 关闭按钮
        self.close_button = tk.Button(
            self.title_bar,
            text="×",
            command=self.toggle,
            font=('Arial', 12, 'bold'),
            bg='#2196F3',
            fg='white',
            bd=0,
            padx=10,
            cursor='hand2'
        )
        self.close_button.pack(side=tk.RIGHT)
        
        # 创建图表容器
        self.chart_frame = tk.Frame(self.stats_window, bg='white')
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建图表
        self.figure = Figure(figsize=(6, 5))
        self.ax = self.figure.add_subplot(111)  # 只需要一个子图
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # 初始化图表
        self.update_chart({})

    def update_chart(self, stats):
        """更新统计图表"""
        if not stats:
            return
        
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        
        try:
            # 清除原图
            self.ax.clear()
            
            # 准备数据
            categories = list(stats.keys())
            values = list(stats.values())
            
            if not categories or not values:
                return
            
            # 绘制条形图
            bars = self.ax.bar(categories, values, color='#2196F3')
            
            # 设置标题和标签
            self.ax.set_title('今日检测统计', pad=10, fontsize=12)
            self.ax.set_xlabel('检测类别', fontsize=10)
            self.ax.set_ylabel('检测次数', fontsize=10)
            
            # 设置x轴标签旋转
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
            
            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                self.ax.text(
                    bar.get_x() + bar.get_width()/2.,
                    height,
                    f'{int(height)}',
                    ha='center',
                    va='bottom',
                    fontsize=10
                )
            
            # 设置网格
            self.ax.grid(True, linestyle='--', alpha=0.3)
            
            # 调整布局
            self.figure.tight_layout()
            
            # 更新画布
            self.canvas.draw()
            
            # 更新时间戳
            self.last_update = current_time
            
        except Exception as e:
            print(f"Chart update error: {e}")

    def toggle(self):
        if not self.is_expanded:
            root_x = self.root.winfo_x()
            root_y = self.root.winfo_y()
            root_width = self.root.winfo_width()
            
            self.y_position = root_y + 50
            self.stats_window.geometry(f"{self.target_width}x600+{root_x + root_width - self.target_width}+{self.y_position}")
            self.stats_window.deiconify()
        else:
            self.stats_window.withdraw()
            
        self.is_expanded = not self.is_expanded

    def start_move(self, event):
        self.start_x = event.x_root - self.stats_window.winfo_x()
        self.start_y = event.y_root - self.stats_window.winfo_y()
        
    def do_move(self, event):
        x = event.x_root - self.start_x
        y = event.y_root - self.start_y
        self.stats_window.geometry(f"+{x}+{y}")
        
    def start_resize(self, event):
        self.start_width = self.stats_window.winfo_width()
        self.start_height = self.stats_window.winfo_height()
        self.start_x = event.x_root
        self.start_y = event.y_root
        
    def do_resize(self, event):
        width = max(300, self.start_width + (event.x_root - self.start_x))
        height = max(400, self.start_height + (event.y_root - self.start_y))
        self.stats_window.geometry(f"{width}x{height}")
        
        # 更新图表大小
        if self.pending_resize:
            self.stats_window.after_cancel(self.pending_resize)
        self.pending_resize = self.stats_window.after(
            self.resize_delay,
            lambda: self._update_chart_size(width, height)
        )
    
    def _update_chart_size(self, width, height):
        """更新图表大小时保持宽高比"""
        self.figure.set_size_inches(width/100, height/100)
        self.figure.tight_layout()  # 重新调整子图布局
        self.canvas.draw()

    def cleanup(self):
        """清理资源"""
        self.stats_window.destroy()
