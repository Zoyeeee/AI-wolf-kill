"""
行动基类 - 所有游戏行动的抽象接口
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from players.player import Player
    from core.game_state import GameState


class BaseAction(ABC):
    """
    行动抽象基类

    所有游戏中的行动（杀人、查验、用药等）都继承此类
    使用命令模式，便于记录和撤销
    """

    def __init__(self, actor: 'Player', target: Optional['Player'] = None):
        """
        初始化行动

        Args:
            actor: 执行行动的玩家
            target: 行动目标玩家（可选）
        """
        self.actor = actor
        self.target = target
        self.executed = False  # 是否已执行

    @abstractmethod
    async def execute(self, game_state: 'GameState') -> dict:
        """
        执行行动

        Args:
            game_state: 当前游戏状态

        Returns:
            dict: 行动结果，格式为:
            {
                "success": bool,
                "message": str,
                "data": dict
            }
        """
        pass

    @abstractmethod
    def can_execute(self, game_state: 'GameState') -> bool:
        """
        检查行动是否可以执行

        Args:
            game_state: 当前游戏状态

        Returns:
            bool: True表示可以执行
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        获取行动描述

        Returns:
            str: 行动的文字描述
        """
        pass

    def __str__(self) -> str:
        """返回行动的字符串表示"""
        return self.get_description()

    def __repr__(self) -> str:
        """返回行动的详细信息"""
        target_info = f", target={self.target.name}" if self.target else ""
        return f"<{self.__class__.__name__}(actor={self.actor.name}{target_info})>"
