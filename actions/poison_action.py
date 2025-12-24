"""
毒人行动 - 女巫使用毒药
"""
from typing import TYPE_CHECKING
from actions.base_action import BaseAction

if TYPE_CHECKING:
    from players.player import Player
    from core.game_state import GameState


class PoisonAction(BaseAction):
    """女巫使用毒药毒人"""

    def __init__(self, actor: 'Player', target: 'Player'):
        super().__init__(actor, target)

    async def execute(self, game_state: 'GameState') -> dict:
        """
        执行毒人行动

        Returns:
            dict: {
                "success": True,
                "message": "女巫使用毒药",
                "data": {"poisoned_id": X}
            }
        """
        if not self.can_execute(game_state):
            return {
                "success": False,
                "message": "无法使用毒药",
                "data": {}
            }

        # 标记目标被毒
        # 注意：被毒的猎人不能开枪
        from roles.hunter import Hunter
        if isinstance(self.target.role, Hunter):
            self.target.role.disable_shoot()

        # 将目标加入今晚死亡名单
        if not hasattr(game_state, 'poisoned_tonight'):
            game_state.poisoned_tonight = []
        game_state.poisoned_tonight.append(self.target)

        self.executed = True

        return {
            "success": True,
            "message": f"女巫使用毒药毒死 {self.target.name}",
            "data": {
                "poisoned_id": self.target.id,
                "poisoned_name": self.target.name
            }
        }

    def can_execute(self, game_state: 'GameState') -> bool:
        """检查是否可以执行"""
        # 目标必须存活
        if not self.target.is_alive:
            return False

        # 女巫必须还有毒药
        from roles.witch import Witch
        if isinstance(self.actor.role, Witch):
            return self.actor.role.has_poison

        return False

    def get_description(self) -> str:
        """获取描述"""
        return f"{self.actor.name} 使用毒药毒死 {self.target.name}"
