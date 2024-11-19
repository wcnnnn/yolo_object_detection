from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QPushButton, QFileDialog, QScrollArea, QLabel,
                           QFrame, QSizePolicy, QGraphicsDropShadowEffect,
                           QWidget, QVBoxLayout, QScroller)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QPoint, QRectF
from PyQt5.QtGui import QTextCharFormat, QTextCursor, QFont, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
import markdown2
import qtawesome as qta
from queue import Queue
from threading import Lock

class CustomWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # 重写以捕获 JavaScript 控制台消息
        print(f"JS Console: {message}")

class MarkdownView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        
        # 使用自定义页面以捕获 JS 错误
        custom_page = CustomWebPage(self)
        self.setPage(custom_page)
        
        # 设置固定高度和宽度策略
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # 优化的HTML模板
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            
            <!-- KaTeX -->
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
            <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
            
            <!-- Prism.js -->
            <link href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
            
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
                    line-height: 1.6;
                    padding: 8px;
                    margin: 0;
                    color: {text_color};
                    font-size: 14px;
                    overflow-wrap: break-word;
                    word-break: break-word;
                }}
                pre {{
                    background-color: #282c34;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 8px 0;
                    overflow-x: auto;
                }}
                code {{
                    font-family: "SFMono-Regular", Consolas, monospace;
                    font-size: 13px;
                }}
                p code {{
                    background-color: rgba(175, 184, 193, 0.2);
                    padding: 0.2em 0.4em;
                    border-radius: 6px;
                    font-size: 85%;
                }}
                .katex {{
                    font-size: 1.1em;
                }}
                .katex-display {{
                    overflow-x: auto;
                    overflow-y: hidden;
                    padding: 8px 0;
                    margin: 0.5em 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 12px 0;
                }}
                th, td {{
                    border: 1px solid #e1e4e8;
                    padding: 8px;
                }}
                th {{
                    background-color: #f6f8fa;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 6px;
                }}
            </style>
        </head>
        <body>
            <div id="content">{content}</div>
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    try {{
                        renderMathInElement(document.body, {{
                            delimiters: [
                                {{left: "$$", right: "$$", display: true}},
                                {{left: "$", right: "$", display: false}},
                                {{left: "\\[", right: "\\]", display: true}},
                                {{left: "\\(", right: "\\)", display: false}}
                            ],
                            throwOnError: false,
                            errorColor: '#cc0000',
                            strict: false
                        }});
                        Prism.highlightAll();
                    }} catch(e) {{
                        console.error("渲染错误:", e);
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
    def set_markdown(self, text: str, is_user: bool = False):
        """设置Markdown内容"""
        try:
            # 转换Markdown为HTML，添加更多扩展支持
            html = markdown2.markdown(text, extras=[
                'fenced-code-blocks',
                'tables',
                'break-on-newline',
                'cuddled-lists',
                'code-friendly'
            ])
            
            # 设置文本颜色
            text_color = '#ffffff' if is_user else '#24292e'
            
            # 使用模板生成完整HTML
            full_html = self.html_template.format(
                content=html,
                text_color=text_color
            )
            
            # 加载HTML内容
            self.setHtml(full_html)
            
            # 动态调整高度
            self.page().runJavaScript(
                'document.documentElement.scrollHeight',
                self._adjust_height
            )
            
        except Exception as e:
            print(f"Markdown渲染错误: {str(e)}")
            self.setHtml(f"<p style='color: red;'>渲染错误: {str(e)}</p>")
            
    def _adjust_height(self, height):
        """调整视图高度"""
        try:
            # 添加一些padding
            self.setMinimumHeight(height + 20)
        except Exception as e:
            print(f"调整高度错误: {str(e)}")

class ChatMessage(QFrame):
    def __init__(self, message: str, is_user: bool = True):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        
        # 消息容器
        msg_container = QFrame()
        msg_container.setMaximumWidth(600)
        msg_layout = QHBoxLayout(msg_container)
        msg_layout.setContentsMargins(12, 8, 12, 8)
        
        # Markdown 查看器
        self.message_view = MarkdownView()
        self.message_view.set_markdown(self.message, self.is_user)
        msg_layout.addWidget(self.message_view)
        
        if self.is_user:
            layout.addStretch()
            msg_container.setStyleSheet("""
                QFrame {
                    background-color: #1a73e8;
                    border-radius: 12px;
                }
            """)
        else:
            msg_container.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-radius: 12px;
                    border: 1px solid #e1e4e8;
                }
            """)
            layout.addStretch()
            
        layout.addWidget(msg_container)
        self.setLayout(layout)
        
    def update_text(self, text: str):
        """更新消息文本"""
        self.message = text
        self.message_view.set_markdown(text, self.is_user)

class OptimizedScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 启用平滑滚动
        QScroller.grabGesture(self.viewport(), QScroller.TouchGesture)
        
        # 优化滚动性能
        self.setViewportMargins(0, 0, 0, 0)
        self.verticalScrollBar().setSingleStep(20)
        
        # 设置滚动条样式
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #c1c9d2;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8b2bd;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

class ChatWindow(QWidget):
    send_message = pyqtSignal(str)
    send_file = pyqtSignal(str)
    
    def __init__(self):
        try:
            super().__init__()
            print("初始化聊天窗口...")
            
            # 初始化消息队列和锁
            self.message_queue = Queue()
            self.update_lock = Lock()
            self.current_response_widget = None
            self.current_response_text = ""
            
            # 设置窗口属性
            self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            
            # 设置固定大小
            self.setFixedSize(400, 600)
            
            self.init_ui()
            
            # 设置更新定时器
            self.update_timer = QTimer(self)
            self.update_timer.timeout.connect(self.process_message_queue)
            self.update_timer.start(50)  # 50ms 更新间隔
            
            print("聊天窗口初始化完成")
            
        except Exception as e:
            print(f"聊天窗口初始化出错: {str(e)}")
            
    def init_ui(self):
        """初始化UI"""
        try:
            # 主布局
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # 标题栏
            title_bar = QFrame()
            title_bar.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-bottom: 1px solid #e1e4e8;
                }
            """)
            title_layout = QHBoxLayout(title_bar)
            title_layout.setContentsMargins(16, 8, 16, 8)
            
            # 标题
            title_label = QLabel("AI 助手")
            title_label.setStyleSheet("""
                QLabel {
                    color: #24292e;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            title_layout.addWidget(title_label)
            
            # 关闭按钮
            close_btn = QPushButton()
            close_btn.setIcon(qta.icon('fa5s.times', color='#666'))
            close_btn.setFixedSize(32, 32)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 16px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            close_btn.clicked.connect(self.hide)
            title_layout.addStretch()
            title_layout.addWidget(close_btn)
            
            main_layout.addWidget(title_bar)

            # 聊天区域
            self.chat_area = OptimizedScrollArea()
            self.chat_area.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background-color: #f7f7f7;
                }
            """)
            
            # 创建聊天容器widget
            chat_container = QWidget()
            self.chat_layout = QVBoxLayout(chat_container)
            self.chat_layout.setSpacing(16)
            self.chat_layout.setContentsMargins(0, 16, 0, 16)
            self.chat_layout.addStretch()
            
            # 设置聊天容器为滚动区域的widget
            self.chat_area.setWidget(chat_container)
            
            main_layout.addWidget(self.chat_area)

            # 输入区域
            input_container = QFrame()
            input_container.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-top: 1px solid #e1e4e8;
                }
            """)
            input_layout = QHBoxLayout(input_container)
            input_layout.setContentsMargins(16, 12, 16, 12)
            input_layout.setSpacing(12)

            # 输入框
            self.input_text = QTextEdit()
            self.input_text.setPlaceholderText("输入消息...")
            self.input_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #e1e4e8;
                    border-radius: 18px;
                    padding: 8px 16px;
                    background-color: #ffffff;
                    font-size: 14px;
                    line-height: 1.6;
                }
                QTextEdit:focus {
                    border: 1px solid #1a73e8;
                    outline: none;
                }
            """)
            self.input_text.setFixedHeight(36)
            input_layout.addWidget(self.input_text)

            # 发送按钮
            send_btn = QPushButton()
            send_btn.setIcon(qta.icon('fa5s.paper-plane', color='#ffffff'))
            send_btn.setFixedSize(36, 36)
            send_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a73e8;
                    border: none;
                    border-radius: 18px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #1557b0;
                }
            """)
            send_btn.clicked.connect(self.send_message_slot)
            input_layout.addWidget(send_btn)

            main_layout.addWidget(input_container)

            # 初始化消息队列和锁
            self.message_queue = Queue()
            self.update_lock = Lock()
            self.current_response_widget = None
            self.current_response_text = ""

            # 设置定时器处理消息队列
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.process_message_queue)
            self.update_timer.start(50)  # 50ms 更新间隔

            # 添加窗口阴影
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 50))
            shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)

            # 添加欢迎消息
            self.add_message("你好！我是 AI 助手，有什么可以帮你的吗？\n\n示例功能：\n- 支持数学公式：$E = mc^2$\n- 支持代码高亮：\n```python\nprint('Hello, World!')\n```\n- 支持表格：\n| 列1 | 列2 |\n|-----|-----|\n| 内容1 | 内容2 |", False)

        except Exception as e:
            print(f"初始化UI出错: {str(e)}")

    def process_message_queue(self):
        """处理消息队列"""
        try:
            with self.update_lock:
                while not self.message_queue.empty():
                    message, is_user, is_stream = self.message_queue.get()
                    self._add_message_internal(message, is_user, is_stream)
        except Exception as e:
            print(f"处理消息队列错误: {str(e)}")

    def add_message(self, message: str, is_user: bool = True, is_stream: bool = False):
        """添加新消息到队列"""
        self.message_queue.put((message, is_user, is_stream))

    def _add_message_internal(self, message: str, is_user: bool = True, is_stream: bool = False):
        """内部处理消息添加"""
        if is_stream and not is_user:
            if not self.current_response_widget:
                self.current_response_widget = ChatMessage("", False)
                self.chat_layout.insertWidget(self.chat_layout.count() - 1, 
                                           self.current_response_widget)
                self.current_response_text = ""
            self.current_response_text += message
            self.current_response_widget.update_text(self.current_response_text)
        else:
            msg_widget = ChatMessage(message, is_user)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_widget)
            if is_user:
                self.current_response_widget = None
                self.current_response_text = ""
        
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_path:
            self.send_file.emit(file_path)

    def send_message_slot(self):
        """发送消息槽函数"""
        message = self.input_text.toPlainText().strip()
        if message:
            self.send_message.emit(message)
            self.input_text.clear()

    def keyPressEvent(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.NoModifier:
            self.send_message_slot()
            event.accept()
        else:
            super().keyPressEvent(event)