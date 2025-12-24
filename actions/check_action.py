"""
查验行动 - 预言家的夜晚行动
"""
from typing import TYPE_CHECKING
from actions.base_action import BaseAction

if TYPE_CHECKING:
    from players.player import Player
    from core.game_state import GameState


class CheckAction(BaseAction):
    """预言家查验身份行动"""

    def __init__(self, actor: 'Player', target: 'Player'):
        super().__init__(actor, target)

    async def execute(self, game_state: 'GameState') -> dict:
        """
        执行查验行动

        Returns:
            dict: {
                "success": True,
                "message": "查验结果",
                "data": {
                    "target_id": X,
                    "is_werewolf": bool
                }
            }
        """
        if not self.can_execute(game_state):
            return {
                "success": False,
                "message": "无法执行查验行动",
                "data": {}
            }

        # 判断目标是否是狼人
        from roles.base_role import RoleCamp
        is_werewolf = self.target.role.camp == RoleCamp.WEREWOLF

        self.executed = True

        result_text = "狼人" if is_werewolf else "好人"

        return {
            "success": True,
            "message": f"{self.target.name} 是 {result_text}",
            "data": {
                "target_id": self.target.id,
                "target_name": self.target.name,
                "is_werewolf": is_werewolf,
                "result": result_text
            }
        }

    def can_execute(self, game_state: 'GameState') -> bool:
        """检查是否可以执行"""
        # 目标必须存活
        if not self.target.is_alive:
            return False

        # 不能查验自己
        if self.target.id == self.actor.id:
            return False

        return True

    def get_description(self) -> str:
        """获取描述"""
        return f"{self.actor.name} 查验 {self.target.name}"
