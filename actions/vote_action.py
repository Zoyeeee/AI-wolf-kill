"""
投票行动 - 白天投票放逐玩家
"""
from typing import TYPE_CHECKING
from actions.base_action import BaseAction

if TYPE_CHECKING:
    from players.player import Player
    from core.game_state import GameState


class VoteAction(BaseAction):
    """投票行动"""

    def __init__(self, actor: 'Player', target: 'Player'):
        super().__init__(actor, target)

    async def execute(self, game_state: 'GameState') -> dict:
        """
        执行投票行动

        Returns:
            dict: {
                "success": True,
                "message": "投票",
                "data": {"voted_for": X}
            }
        """
        if not self.can_execute(game_state):
            return {
                "success": False,
                "message": "无法投票",
                "data": {}
            }

        # 记录投票
        self.target.votes_received += 1

        self.executed = True

        return {
            "success": True,
            "message": f"{self.actor.name} 投票给 {self.target.name}",
            "data": {
                "voter_id": self.actor.id,
                "voted_for_id": self.target.id,
                "voted_for_name": self.target.name
            }
        }

    def can_execute(self, game_state: 'GameState') -> bool:
        """检查是否可以执行"""
        # 投票者和目标都必须存活
        if not self.actor.is_alive or not self.target.is_alive:
            return False

        return True

    def get_description(self) -> str:
        """获取描述"""
        return f"{self.actor.name} 投票给 {self.target.name}"
