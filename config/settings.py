"""
配置管理模块 - 从环境变量加载配置
"""
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Settings:
    """全局配置类"""

    # DeepSeek API配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_EXPIRE_TIME: int = int(os.getenv("REDIS_EXPIRE_TIME", "86400"))

    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY is required in .env file")
        if not cls.REDIS_HOST:
            raise ValueError("REDIS_HOST is required in .env file")
        return True


# 创建全局配置实例
settings = Settings()
