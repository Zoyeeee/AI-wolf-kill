"""
LLM客户端 - 封装DeepSeek API调用
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from config.settings import settings


class LLMClient:
    """
    LLM客户端

    封装对DeepSeek API的调用
    """

    def __init__(self):
        """初始化LLM客户端"""
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            temperature=0.1,  # 较低的温度使输出更确定
        )

    async def generate(self, prompt: str) -> str:
        """
        生成文本

        Args:
            prompt: 提示词

        Returns:
            str: 生成的文本
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"LLM生成错误: {e}")
            return ""

    def generate_sync(self, prompt: str) -> str:
        """
        同步生成文本

        Args:
            prompt: 提示词

        Returns:
            str: 生成的文本
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"LLM生成错误: {e}")
            return ""


# 创建全局LLM客户端实例
llm_client = LLMClient()
