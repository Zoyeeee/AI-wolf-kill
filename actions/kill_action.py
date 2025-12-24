"""
杀人行动 - 狼人的夜晚行动
"""
from typing import TYPE_CHECKING
from actions.base_action import BaseAction

if TYPE_CHECKING:
    from players.player import Player
    from core.game_state import GameState


class KillAction(BaseAction):
    """狼人杀人行动"""

    def __init__(self, actor: 'Player', target: 'Player'):
        super().__init__(actor, target)

    async def execute(self, game_state: 'GameState') -> dict:
        """
        执行杀人行动

        Returns:
            dict: {
                "success": True,
                "message": "狼人选择杀死玩家X",
                "data": {"victim_id": X}
            }
        """
        if not self.can_execute(game_state):
            return {
                "success": False,
                "message": "无法执行杀人行动",
                "data": {}
            }

        # 记录今晚的受害者（实际死亡由女巫决定）
        game_state.tonight_victim = self.target
        self.executed = True

        return {
            "success": True,
            "message": f"狼人选择杀死 {self.target.name}",
            "data": {
                "victim_id": self.target.id,
                "victim_name": self.target.name
            }
        }

    def can_execute(self, game_state: 'GameState') -> bool:
        """检查是否可以执行"""
        # 目标必须存活
        if not self.target.is_alive:
            return False

        # 不能杀狼人
        from roles.base_role import RoleCamp
        if self.target.role.camp == RoleCamp.WEREWOLF:
            return False

        return True

    def get_description(self) -> str:
        """获取描述"""
        return f"{self.actor.name} 杀死 {self.target.name}"
