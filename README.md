# 智能人脸检测系统 2.0

## 项目简介
这是一个基于 PyQt5 和 YOLO 的智能人脸检测系统2.0版本。系统集成了实时人脸检测、AI助手、数据分析等功能，采用模块化设计，具有良好的可扩展性和用户体验。

## 主要特性

### 1. 检测功能
- 实时视频显示和人脸检测
- 多种 YOLO 模型支持（nano/small/medium/large）
- 可调节的检测时间间隔
- 实时检测结果显示

### 2. AI 助手功能
- 实时流式对话
  - Markdown 实时渲染
  - LaTeX 数学公式支持
  - 代码高亮显示
  - 表格渲染支持
- 智能悬浮按钮
  - 可拖拽定位
  - 始终置顶显示
  - 位置记忆功能
- 上下文理解
  - 智能对话管理
  - 历史记录保存
  - 会话状态维护

### 3. 数据分析功能
- 实时统计分析
- 多维度数据可视化
- 趋势预测
- 自定义报表导出

### 4. 用户界面
- 现代化界面设计
- 响应式布局

## 项目结构
```
recognize/
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
├── README.md              # 项目文档
├── config.py              # 配置文件
│
├── database/              # 数据库模块
│   ├── __init__.py
│   ├── db_manager.py      # 数据库管理器
│   └── models.py          # 数据模型
│
├── models/                # 模型模块
│   ├── __init__.py
│   ├── model_manager.py   # 模型管理器
│   └── model_analyzer.py  # 模型分析器
│
├── utils/                 # 工具模块
│   ├── __init__.py
│   ├── logger.py         # 日志管理器
│   └── helpers.py        # 辅助函数
│
├── ui/                    # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py    # 主窗口
│   └── components/       # UI组件
│       ├── control_panel.py   # 控制面板
│       ├── video_display.py   # 视频显示
│       └── visualization.py   # 数据可视化
│
├── chatbot/              # AI助手模块
│   ├── __init__.py
│   ├── api_client.py     # API客户端
│   ├── chat_window.py    # 聊天窗口
│   ├── floating_button.py # 悬浮按钮
│   └── message_handler.py # 消息处理器
│
└── logs/                 # 日志文件夹
    └── detection_logs.log # 检测日志
```

## 安装说明

### 环境要求
- Python 3.8+
- MySQL 5.7+
- 摄像头设备

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/yourusername/face-detection-system.git
cd face-detection-system
```

2. 创建虚拟环境
```bash
python -m venv venv
```

3. 激活环境
Windows:
```bash
venv\Scripts\activate
```
Linux/Mac:
```bash
source venv/bin/activate
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用说明

### 1. 启动程序
```bash
python main.py
```

### 2. 检测功能
- 选择检测模型
- 调整检测参数
- 开始/停止检测
- 查看检测结果

### 3. AI助手功能
- 点击悬浮按钮打开对话窗口
- 支持以下功能：
  ```
  - 数学公式：$E = mc^2$
  - 代码块：```python
  - 表格：| 表头 | 表头 |
  ```
- 使用 Enter 发送消息
- Shift+Enter 换行

### 4. 数据管理
- 查看检测记录
- 导出数据报表
- 分析统计图表
- 清理历史数据

## 配置说明

### 主要配置项
```python
# config.py

# 检测配置
DETECTION_INTERVAL = 100    # 检测间隔(ms)
MODEL_TYPE = 'yolov8n'     # 模型类型
CONFIDENCE_THRESHOLD = 0.5  # 置信度阈值

# AI助手配置
DEEPSEEK_API_KEY = "your_api_key"
CHAT_UPDATE_INTERVAL = 50   # 消息更新间隔
MAX_HISTORY_LENGTH = 100    # 最大历史消息数

# 数据库配置
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "face_detection"
```

## 性能优化

### 1. 界面优化
- 消息队列
- 异步处理
- 虚拟滚动
- 延迟加载

### 2. 内存管理
- 自动清理
- 资源复用
- 缓存优化

## 常见问题

1. 运行问题
   - 摄像头访问
   - 模型加载
   - 数据库连接

## 更新日志

### v2.0.0 (2024-11-19)
- 新增 AI 助手功能
- 优化检测性能
- 改进用户界面
- 增强数据分析
- 添加深色模式

### v1.0.0 (2024-11-18)
- 初始版本发布

## 开发计划
- [ ] 多摄像头支持
- [ ] 云端同步功能
- [ ] 移动端适配
- [ ] 更多AI模型集成

## 许可证
[MIT License](LICENSE)

## 联系方式
- 作者：wcnnnn
- 邮箱：3076648528@qq.com
- GitHub：[wcnnnn](https://github.com/wcnnnn)