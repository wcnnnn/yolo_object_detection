# YOLO实时物体检测系统

这是一个基于YOLOv8的实时物体检测系统，具有实时视频检测、数据统计、结果导出等功能。

## 功能特点

- 实时视频物体检测
- 检测结果实时显示和统计
- 数据库存储检测记录
- 可视化统计图表
- 检测结果导出(CSV/Excel)
- 配置管理
- 日志记录

## 系统要求

- Python 3.8+
- MySQL 8.0+
- CUDA支持（推荐，用于GPU加速）

## 安装步骤

1. 克隆项目
```
bash
git clone https://github.com/wcnnnn/yolo_object_detection.git
cd yolo_object_detection

2. 创建虚拟环境（推荐）
```
bash
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

3. 安装依赖\
```
bash
pip install -r requirements.txt


4. 配置数据库
- 在MySQL中创建数据库
- 修改 config.py 中的数据库配置

## 项目结构
yolo_object_detection/
├── main.py # 程序入口
├── ui.py # 用户界面模块
├── detector.py # YOLO检测模块
├── database.py # 数据库操作模块
├── visualization.py # 数据可视化模块
├── config_manager.py # 配置管理模块
├── report_generator.py # 报告生成模块
├── config.py # 配置文件
├── requirements.txt # 依赖包列表
└── README.md # 项目说明文档


## 使用说明

1. 启动程序
```
bash
python main.py


2. 主要功能
- 开始/停止检测：控制视频检测
- 检测设置：调整模型参数和检测间隔
- 统计图表：查看检测统计数据
- 数据导出：导出检测记录
- 配置管理：管理系统配置

3. 快捷键
- `Ctrl+S`: 保存当前配置
- `Ctrl+Q`: 退出程序
- `Space`: 开始/停止检测

## 配置说明

在 config.py 中可以修改以下配置：
- 数据库连接信息
- YOLO模型参数
- 检测阈值
- 其他系统参数

## 数据导出

系统支持两种导出格式：
1. CSV格式：包含日期、类别、检测次数
2. Excel格式：包含详细统计信息和图表

## 常见问题

1. 数据库连接错误
- 检查MySQL服务是否启动
- 验证数据库配置信息

2. 摄像头无法打开
- 确认摄像头设备已正确连接
- 检查设备权限

3. GPU不可用
- 确认CUDA正确安装
- 检查GPU驱动版本

## 开发说明

1. 添加新功能
- 在相应模块中添加功能实现
- 在UI中添加控制元素
- 更新配置文件

2. 修改检测模型
- 替换 detector.py 中的模型文件
- 调整相关参数

## 维护者

- [Your Name](https://github.com/yourusername)

## 许可证

MIT License

## 更新日志

### v1.0.0 (2024-03-xx)
- 初始版本发布
- 基本检测功能
- 数据统计和导出
- 配置管理

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 致谢

- [YOLOv8](https://github.com/ultralytics/ultralytics)
- [OpenCV](https://opencv.org/)
- [其他使用的开源项目]
