"""
角色基类 - 策略模式的核心
定义所有角色必须实现的接口
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_state import GameState
    from players.player import Player
    from actions.base_action import BaseAction


class RoleCamp(Enum):
    """角色阵营"""
    WEREWOLF = "狼人阵营"
    VILLAGER = "好人阵营"
    NEUTRAL = "中立阵营"


class RoleType(Enum):
    """角色类型"""
    WEREWOLF = "狼人"
    VILLAGER = "村民"
    SEER = "预言家"
    WITCH = "女巫"
    HUNTER = "猎人"
    GUARD = "守卫"
    CUPID = "丘比特"


class BaseRole(ABC):
    """
    角色抽象基类 - 策略模式

    所有角色必须继承此类并实现抽象方法
    这样设计的好处：
    1. 易于扩展：添加新角色只需继承并实现方法
    2. 统一接口：所有角色都有相同的调用方式
    3. 灵活配置：可以动态更换角色策略
    """

    def __init__(self):
        self.role_type: Optional[RoleType] = None
        self.camp: Optional[RoleCamp] = None
        self.has_night_action: bool = False  # 是否有夜晚行动
        self.action_priority: int = 0        # 夜晚行动优先级（数字越小越先行动）

    @abstractmethod
    def get_role_description(self) -> str:
        """
        获取角色描述

        Returns:
            str: 角色的详细描述，用于游戏开始时告知玩家
        """
        pass

    @abstractmethod
    def can_act_at_night(self, game_state: 'GameState') -> bool:
        """
        判断角色是否可以在夜晚行动

        Args:
            game_state: 当前游戏状态

        Returns:
            bool: True表示可以行动，False表示不能行动
        """
        pass

    @abstractmethod
    def get_available_actions(self, game_state: 'GameState') -> List[str]:
        """
        获取角色当前可用的行动列表

        Args:
            game_state: 当前游戏状态

        Returns:
            List[str]: 可用行动列表，如 ["kill", "skip"]
        """
        pass

    @abstractmethod
    async def perform_night_action(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> Optional['BaseAction']:
        """
        执行夜晚行动

        Args:
            player: 执行行动的玩家
            game_state: 当前游戏状态

        Returns:
            Optional[BaseAction]: 返回行动对象，如果跳过则返回None
        """
        pass

    def on_death(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> Optional['BaseAction']:
        """
        死亡时触发的事件（如猎人开枪）

        Args:
            player: 死亡的玩家
            game_state: 当前游戏状态

        Returns:
            Optional[BaseAction]: 返回触发的行动，如果没有则返回None
        """
        return None

    def check_win_condition(self, game_state: 'GameState') -> bool:
        """
        检查该角色的胜利条件

        Args:
            game_state: 当前游戏状态

        Returns:
            bool: True表示该阵营获胜
        """
        if self.camp == RoleCamp.WEREWOLF:
            return game_state.check_werewolf_victory()
        elif self.camp == RoleCamp.VILLAGER:
            return game_state.check_villager_victory()
        return False

    def __str__(self) -> str:
        """返回角色类型的字符串表示"""
        return self.role_type.value if self.role_type else "未知角色"

    def __repr__(self) -> str:
        """返回角色的详细信息"""
        return f"<{self.__class__.__name__}: {self.role_type.value if self.role_type else 'Unknown'}>"
