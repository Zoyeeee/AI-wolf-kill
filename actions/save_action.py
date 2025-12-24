"""
救人行动 - 女巫使用解药
"""
from typing import TYPE_CHECKING
from actions.base_action import BaseAction

if TYPE_CHECKING:
    from players.player import Player
    from core.game_state import GameState


class SaveAction(BaseAction):
    """女巫使用解药救人"""

    def __init__(self, actor: 'Player', target: 'Player'):
        super().__init__(actor, target)

    async def execute(self, game_state: 'GameState') -> dict:
        """
        执行救人行动

        Returns:
            dict: {
                "success": True,
                "message": "女巫使用解药",
                "data": {"saved_id": X}
            }
        """
        if not self.can_execute(game_state):
            return {
                "success": False,
                "message": "无法使用解药",
                "data": {}
            }

        # 救活目标（取消tonight_victim）
        if game_state.tonight_victim and game_state.tonight_victim.id == self.target.id:
            game_state.tonight_victim = None

        self.executed = True

        return {
            "success": True,
            "message": f"女巫使用解药救了 {self.target.name}",
            "data": {
                "saved_id": self.target.id,
                "saved_name": self.target.name
            }
        }

    def can_execute(self, game_state: 'GameState') -> bool:
        """检查是否可以执行"""
        # 目标必须是今晚的受害者
        if not game_state.tonight_victim:
            return False

        if game_state.tonight_victim.id != self.target.id:
            return False

        # 女巫必须还有解药
        from roles.witch import Witch
        if isinstance(self.actor.role, Witch):
            return self.actor.role.has_antidote

        return False

    def get_description(self) -> str:
        """获取描述"""
        return f"{self.actor.name} 使用解药救了 {self.target.name}"
