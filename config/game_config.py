"""
游戏规则配置模块
"""
from enum import Enum
from typing import Dict, List


class GameMode(Enum):
    """游戏模式"""
    SINGLE_VS_AI = "single_vs_ai"  # 单人vs AI
    MULTIPLAYER = "multiplayer"     # 多人在线


class RoleConfig(Enum):
    """角色配置预设"""
    BASIC = "basic"      # 基础版：狼人、村民、预言家、女巫、猎人
    STANDARD = "standard"  # 标准版：增加守卫、白痴等
    FULL = "full"        # 完整版：所有角色


# 不同配置的角色组成
ROLE_COMPOSITIONS: Dict[str, Dict[str, int]] = {
    "basic": {
        "werewolf": 3,     # 狼人
        "villager": 3,     # 村民
        "seer": 1,         # 预言家
        "witch": 1,        # 女巫
        "hunter": 1,       # 猎人
        # 总计：9人
    },
    "standard": {
        "werewolf": 4,     # 狼人
        "villager": 4,     # 村民
        "seer": 1,         # 预言家
        "witch": 1,        # 女巫
        "hunter": 1,       # 猎人
        "guard": 1,        # 守卫
        # 总计：12人
    },
}


class GameConfig:
    """游戏配置类"""

    # 默认玩家数量
    DEFAULT_TOTAL_PLAYERS = 9
    DEFAULT_HUMAN_PLAYERS = 1

    # 默认角色配置
    DEFAULT_ROLE_CONFIG = "basic"

    # 游戏流程配置
    ENABLE_FIRST_NIGHT = True  # 是否启用第一夜（所有角色认识身份）
    SPEECH_TIME_LIMIT = 60     # 发言时间限制（秒）
    VOTE_TIME_LIMIT = 30       # 投票时间限制（秒）

    # AI配置
    AI_NAME_PREFIX = "AI-"     # AI玩家名称前缀
    AI_TEMPERATURE = 0.1       # AI生成温度（0-1，越低越确定）

    # Redis配置
    GAME_KEY_PREFIX = "game:"  # Redis键前缀

    # 胜利判断配置
    victory_check_config = {
        # 是否允许已分胜负时猎人开枪（可能逆转结果）
        "allow_hunter_shoot_after_victory": True,

        # 是否在警长传递前判断胜利
        "check_victory_before_sheriff_transfer": True,

        # 胜利判断粒度：
        # "immediate": 每次死亡后立即判断
        # "after_chain": 完成完整死亡连锁后再判断
        "check_granularity": "after_chain"
    }

    @staticmethod
    def get_role_composition(config: str) -> Dict[str, int]:
        """获取指定配置的角色组成"""
        return ROLE_COMPOSITIONS.get(config, ROLE_COMPOSITIONS["basic"])

    @staticmethod
    def get_total_players(config: str) -> int:
        """获取指定配置的总玩家数"""
        composition = GameConfig.get_role_composition(config)
        return sum(composition.values())

    @staticmethod
    def validate_config(config: str) -> bool:
        """验证配置是否有效"""
        return config in ROLE_COMPOSITIONS


# 创建全局游戏配置实例
game_config = GameConfig()
