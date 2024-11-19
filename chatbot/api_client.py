from openai import OpenAI
from typing import List, Dict, Generator
import time

class DeepSeekClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """同步聊天完成"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"聊天请求错误: {str(e)}")
            return "请求失败，请稍后重试。"

    def chat_completion_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """流式聊天完成"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"流式聊天错误: {str(e)}")
            yield "请求失败，请稍后重试。"

    def chat_completion_stream_mock(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """模拟流式聊天响应（用于测试）"""
        response = "这是一个模拟的回复，用于测试流式输出功能。"
        for char in response:
            yield char
            time.sleep(0.05)  # 模拟网络延迟