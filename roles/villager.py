"""
村民角色实现
"""
from typing import Optional, List, TYPE_CHECKING
from roles.base_role import BaseRole, RoleType, RoleCamp

if TYPE_CHECKING:
    from core.game_state import GameState
    from players.player import Player
    from actions.base_action import BaseAction


class Villager(BaseRole):
    """
    村民角色

    特点：
    - 属于好人阵营
    - 没有任何特殊能力
    - 只能通过白天发言和投票参与游戏
    - 是最基础的角色
    """

    def __init__(self):
        super().__init__()
        self.role_type = RoleType.VILLAGER
        self.camp = RoleCamp.VILLAGER
        self.has_night_action = False  # 村民没有夜晚行动
        self.action_priority = 999     # 不参与夜晚行动排序

    def get_role_description(self) -> str:
        """获取角色描述"""
        return (
            "你是村民，属于好人阵营。\n"
            "你没有任何特殊能力，但你可以通过白天的发言和投票来帮助好人阵营。\n"
            "你的目标是找出并投死所有狼人。"
        )

    def can_act_at_night(self, game_state: 'GameState') -> bool:
        """村民不能在夜晚行动"""
        return False

    def get_available_actions(self, game_state: 'GameState') -> List[str]:
        """村民没有特殊行动"""
        return []

    async def perform_night_action(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> Optional['BaseAction']:
        """村民没有夜晚行动"""
        return None
