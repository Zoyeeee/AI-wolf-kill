"""
LLM客户端 - 封装DeepSeek API调用
"""
import os
import warnings
from typing import Optional
from langchain_openai import ChatOpenAI
from config.settings import settings
import httpx

# 抑制SSL验证警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class LLMClient:
    """
    LLM客户端

    封装对DeepSeek API的调用
    """

    def __init__(self):
        """初始化LLM客户端"""
        # 创建一个禁用SSL验证的httpx客户端
        # 注意：这是为了解决SSL证书验证问题，生产环境应该使用正确的证书
        http_client = httpx.AsyncClient(verify=False)

        self.llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            temperature=0.1,  # 较低的温度使输出更确定
            http_async_client=http_client,  # 使用自定义的http客户端
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
            import traceback
            print(f"LLM生成错误: {type(e).__name__}: {e}")
            print("完整堆栈跟踪：")
            traceback.print_exc()
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
            import traceback
            print(f"LLM生成错误: {type(e).__name__}: {e}")
            print("完整堆栈跟踪：")
            traceback.print_exc()
            return ""


# 创建全局LLM客户端实例
llm_client = LLMClient()
