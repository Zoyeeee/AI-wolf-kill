"""
射击行动 - 猎人死亡时开枪
"""
from typing import TYPE_CHECKING
from actions.base_action import BaseAction

if TYPE_CHECKING:
    from players.player import Player
    from core.game_state import GameState


class ShootAction(BaseAction):
    """猎人开枪行动"""

    def __init__(self, actor: 'Player', target: 'Player'):
        super().__init__(actor, target)

    async def execute(self, game_state: 'GameState') -> dict:
        """
        执行开枪行动

        Returns:
            dict: {
                "success": True,
                "message": "猎人开枪",
                "data": {"shot_id": X}
            }
        """
        if not self.can_execute(game_state):
            return {
                "success": False,
                "message": "无法开枪",
                "data": {}
            }

        # 杀死目标
        self.target.is_alive = False
        game_state.dead_players.append(self.target)
        game_state.alive_players.remove(self.target)

        self.executed = True

        return {
            "success": True,
            "message": f"猎人 {self.actor.name} 开枪带走了 {self.target.name}",
            "data": {
                "shot_id": self.target.id,
                "shot_name": self.target.name
            }
        }

    def can_execute(self, game_state: 'GameState') -> bool:
        """检查是否可以执行"""
        # 目标必须存活
        if not self.target.is_alive:
            return False

        # 猎人必须能开枪
        from roles.hunter import Hunter
        if isinstance(self.actor.role, Hunter):
            return self.actor.role.can_shoot

        return False

    def get_description(self) -> str:
        """获取描述"""
        return f"{self.actor.name} 开枪射击 {self.target.name}"
