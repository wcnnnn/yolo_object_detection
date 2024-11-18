from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib
# 设置后端，避免交互模式提示
matplotlib.use('Qt5Agg')
# 关闭交互模式
matplotlib.interactive(False)
import warnings
import scienceplots
import matplotlib
import time
# 设置后端为 'Agg'
matplotlib.use('Agg')
# 关闭交互模式
plt.ioff()
import matplotlib.font_manager as fm
from matplotlib.figure import Figure
import os
warnings.filterwarnings('ignore')

# 字体配置
font_dir = r'C:\Users\30766\anaconda3\envs\Tensorflow\Lib\site-packages\matplotlib\mpl-data\fonts\ttf'
font_files = fm.findSystemFonts(fontpaths=[font_dir])
for font_file in font_files:
    fm.fontManager.addfont(font_file)
fonts = [fm.FontProperties(fname=f).get_name() for f in font_files]
plt.style.use(['science', 'bright','no-latex','cjk-sc-font'])

class VisualizationPanel(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        
        # 创建四个图表容器
        self.create_bar_chart()
        self.create_trend_chart()
        self.create_heatmap()
        self.create_pie_chart()
        
        # 添加到标签页
        self.tab_widget.addTab(self.bar_widget, "类别统计")
        self.tab_widget.addTab(self.trend_widget, "趋势图")
        self.tab_widget.addTab(self.heatmap_widget, "热力图")
        self.tab_widget.addTab(self.pie_widget, "占比分布")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def create_bar_chart(self):
        self.bar_widget = QWidget()
        layout = QVBoxLayout()
        self.bar_figure = Figure(figsize=(8, 6))
        self.bar_canvas = FigureCanvas(self.bar_figure)
        layout.addWidget(self.bar_canvas)
        self.bar_widget.setLayout(layout)
        
    def create_trend_chart(self):
        self.trend_widget = QWidget()
        layout = QVBoxLayout()
        self.trend_figure = Figure(figsize=(8, 6))
        self.trend_canvas = FigureCanvas(self.trend_figure)
        layout.addWidget(self.trend_canvas)
        self.trend_widget.setLayout(layout)
        
    def create_heatmap(self):
        self.heatmap_widget = QWidget()
        layout = QVBoxLayout()
        self.heatmap_figure = Figure(figsize=(8, 6))
        self.heatmap_canvas = FigureCanvas(self.heatmap_figure)
        layout.addWidget(self.heatmap_canvas)
        self.heatmap_widget.setLayout(layout)
        
    def create_pie_chart(self):
        self.pie_widget = QWidget()
        layout = QVBoxLayout()
        self.pie_figure = Figure(figsize=(8, 6))
        self.pie_canvas = FigureCanvas(self.pie_figure)
        layout.addWidget(self.pie_canvas)
        self.pie_widget.setLayout(layout)
        
    def update_bar_chart(self):
        data = self.db_manager.get_today_stats()
        if not data:
            return
            
        self.bar_figure.clear()
        ax = self.bar_figure.add_subplot(111)
        
        categories = [item[0] for item in data]
        values = [item[1] for item in data]
        
        bars = ax.bar(categories, values)
        ax.set_title('今日检测类别统计', fontsize=12, pad=15)
        ax.set_xlabel('检测类别')
        ax.set_ylabel('数量')
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom')
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        self.bar_figure.tight_layout()
        self.bar_canvas.draw()
        
    def update_trend_chart(self):
        data = self.db_manager.get_detection_stats(7)
        if not data:
            return
            
        self.trend_figure.clear()
        ax = self.trend_figure.add_subplot(111)
        
        df = pd.DataFrame(data, columns=['class_name', 'count', 'date'])
        
        for class_name in df['class_name'].unique():
            class_data = df[df['class_name'] == class_name]
            ax.plot(class_data['date'], class_data['count'], 
                   marker='o', label=class_name)
        
        ax.set_title('近7天检测趋势', fontsize=12, pad=15)
        ax.set_xlabel('日期')
        ax.set_ylabel('检测数量')
        ax.legend()
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        self.trend_figure.tight_layout()
        self.trend_canvas.draw()
        
    def update_heatmap(self):
        data = self.db_manager.get_position_data()
        if not data:
            return
            
        self.heatmap_figure.clear()
        ax = self.heatmap_figure.add_subplot(111)
        
        x = [item[0] for item in data]
        y = [item[1] for item in data]
        
        # 创建热力图
        heatmap = ax.hist2d(x, y, bins=30, cmap='YlOrRd')
        self.heatmap_figure.colorbar(heatmap[3], ax=ax)
        
        ax.set_title('检测位置热力图', fontsize=12, pad=15)
        ax.set_xlabel('X坐标')
        ax.set_ylabel('Y坐标')
        
        self.heatmap_figure.tight_layout()
        self.heatmap_canvas.draw()
        
    def update_pie_chart(self):
        data = self.db_manager.get_total_stats()
        if not data:
            return
            
        self.pie_figure.clear()
        ax = self.pie_figure.add_subplot(111)
        
        labels = [item[0] for item in data]
        sizes = [item[1] for item in data]
        
        # 计算百分比
        total = sum(sizes)
        percentages = [f'{(size/total)*100:.1f}%' for size in sizes]
        
        # 创建饼图
        patches, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                         startangle=90)
        
        ax.set_title('检测类别分布', fontsize=12, pad=15)
        ax.axis('equal')  # 保持饼图为圆形
        
        # 添加图例
        ax.legend(patches, [f'{l} ({p})' for l, p in zip(labels, percentages)],
                 title="类别 (占比)",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
        
        self.pie_figure.tight_layout()
        self.pie_canvas.draw()
        
    def update_charts(self):
        try:
            self.update_bar_chart()
            self.update_trend_chart()
            self.update_heatmap()
            self.update_pie_chart()
        except Exception as e:
            print(f"更新图表错误: {str(e)}")