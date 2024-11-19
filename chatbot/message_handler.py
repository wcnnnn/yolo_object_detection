from typing import Generator
import asyncio
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI  # 使用 OpenAI SDK

class MessageHandler:
    def __init__(self, api_key: str):
        # 使用 OpenAI SDK 初始化客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.message_history = []
        
    def handle_message_stream(self, message: str) -> Generator[str, None, None]:
        """同步流式处理消息"""
        try:
            print(f"处理消息: {message}")
            
            # 添加用户消息到历史
            self.message_history.append({
                "role": "user",
                "content": message
            })
            
            print(f"消息历史: {self.message_history}")
            
            # 使用 OpenAI SDK 的方式调用 API
            response_stream = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    *self.message_history
                ],
                stream=True
            )
            
            current_response = ""
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    current_response += content
                    yield content
            
            # 将 AI 的回复添加到历史记录
            if current_response:
                self.message_history.append({
                    "role": "assistant",
                    "content": current_response
                })
                
        except Exception as e:
            print(f"流式聊天错误: {str(e)}")
            yield f"抱歉，处理消息时出现错误: {str(e)}"
            
    def handle_message(self, message: str) -> str:
        """同步处理消息（非流式）"""
        try:
            # 添加用户消息到历史
            self.message_history.append({
                "role": "user",
                "content": message
            })
            
            # 使用 OpenAI SDK 的方式调用 API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    *self.message_history
                ],
                stream=False
            )
            
            response_content = response.choices[0].message.content
            
            # 将 AI 的回复添加到历史记录
            if response_content:
                self.message_history.append({
                    "role": "assistant",
                    "content": response_content
                })
            
            return response_content
            
        except Exception as e:
            print(f"聊天错误: {str(e)}")
            return f"抱歉，处理消息时出现错误: {str(e)}"
            
    def clear_history(self):
        """清空聊天历史"""
        self.message_history = [] 