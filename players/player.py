"""
玩家基类
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from roles.base_role import BaseRole
    from core.game_state import GameState


class Player(ABC):
    """
    玩家抽象基类

    所有玩家（真人和AI）都继承此类
    """

    def __init__(self, player_id: int, name: str, role: 'BaseRole'):
        """
        初始化玩家

        Args:
            player_id: 玩家ID
            name: 玩家名称
            role: 玩家角色
        """
        self.id = player_id
        self.name = name
        self.role = role
        self.is_alive = True
        self.votes_received = 0  # 本轮收到的票数
        self.speech_history: List[str] = []  # 发言历史
        self.seat_number: int = player_id  # 座位号（默认等于ID）
        self.is_sheriff: bool = False      # 是否是警长

    @abstractmethod
    async def make_speech(self, game_state: 'GameState') -> str:
        """
        发言

        Args:
            game_state: 当前游戏状态

        Returns:
            str: 发言内容
        """
        pass

    @abstractmethod
    async def vote(self, game_state: 'GameState') -> Optional['Player']:
        """
        投票

        Args:
            game_state: 当前游戏状态

        Returns:
            Optional[Player]: 投票目标，None表示弃票
        """
        pass

    @abstractmethod
    async def choose_target(
        self,
        game_state: 'GameState',
        available_targets: List['Player'],
        action_type: str
    ) -> Optional['Player']:
        """
        选择目标（用于夜晚行动）

        Args:
            game_state: 当前游戏状态
            available_targets: 可选目标列表
            action_type: 行动类型（kill, check, poison等）

        Returns:
            Optional[Player]: 选择的目标，None表示跳过
        """
        pass

    @abstractmethod
    async def make_werewolf_discussion(
        self,
        game_state: 'GameState',
        round_idx: int
    ) -> str:
        """
        狼人讨论发言

        Args:
            game_state: 游戏状态
            round_idx: 当前讨论轮数（1-3）

        Returns:
            str: 讨论内容
        """
        pass

    async def choose_witch_action(
        self,
        game_state: 'GameState',
        witch_role: 'BaseRole'
    ) -> Optional[Tuple[str, 'Player']]:
        """
        女巫选择行动（救人或毒人）

        Args:
            game_state: 当前游戏状态
            witch_role: 女巫角色对象

        Returns:
            Optional[Tuple[str, Player]]: (行动类型, 目标)，None表示跳过
        """
        return None

    @abstractmethod
    async def decide_sheriff_candidacy(self, game_state: 'GameState') -> bool:
        """
        决定是否竞选警长

        Args:
            game_state: 当前游戏状态

        Returns:
            bool: True表示竞选，False表示不竞选
        """
        pass

    @abstractmethod
    async def make_sheriff_campaign_speech(self, game_state: 'GameState') -> str:
        """
        发表竞选宣言

        Args:
            game_state: 当前游戏状态

        Returns:
            str: 竞选宣言内容
        """
        pass

    @abstractmethod
    async def vote_for_sheriff(
        self,
        game_state: 'GameState',
        candidates: List['Player']
    ) -> Optional['Player']:
        """
        投票选举警长

        Args:
            game_state: 当前游戏状态
            candidates: 候选人列表

        Returns:
            Optional[Player]: 投票目标，None表示弃票
        """
        pass

    @abstractmethod
    async def choose_speaking_direction(self, game_state: 'GameState') -> str:
        """
        警长选择发言方向

        Args:
            game_state: 当前游戏状态

        Returns:
            str: "clockwise"（死右/顺时针）或 "counterclockwise"（死左/逆时针）
        """
        pass

    @abstractmethod
    async def choose_sheriff_successor(
        self,
        game_state: 'GameState'
    ) -> Optional['Player']:
        """
        警长选择继承人

        Args:
            game_state: 当前游戏状态

        Returns:
            Optional[Player]: 继承人，None表示撕毁警徽
        """
        pass

    def reset_votes(self):
        """重置本轮投票数"""
        self.votes_received = 0

    def add_speech(self, speech: str):
        """添加发言记录"""
        self.speech_history.append(speech)

    def __str__(self) -> str:
        """返回玩家信息"""
        status = "存活" if self.is_alive else "死亡"
        return f"{self.name}({self.id}号) - {self.role} - {status}"

    def __repr__(self) -> str:
        """返回玩家详细信息"""
        return f"<Player(id={self.id}, name={self.name}, role={self.role.role_type.value}, alive={self.is_alive})>"
