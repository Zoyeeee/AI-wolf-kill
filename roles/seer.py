"""
预言家角色实现
"""
from typing import Optional, List, TYPE_CHECKING
from roles.base_role import BaseRole, RoleType, RoleCamp

if TYPE_CHECKING:
    from core.game_state import GameState
    from players.player import Player
    from actions.base_action import BaseAction


class Seer(BaseRole):
    """
    预言家角色

    特点：
    - 属于好人阵营
    - 每晚可以查验一名玩家的身份
    - 行动优先级2（在狼人之后）
    - 是好人阵营最重要的角色
    """

    def __init__(self):
        super().__init__()
        self.role_type = RoleType.SEER
        self.camp = RoleCamp.VILLAGER
        self.has_night_action = True
        self.action_priority = 2  # 在狼人之后
        self.checked_players: List[int] = []  # 记录已查验的玩家ID
        # DEBUG: 确认每次都创建新的预言家实例
        import random
        self._instance_id = random.randint(1000, 9999)
        # print(f"[DEBUG] 创建新预言家实例 {self._instance_id}, checked_players={self.checked_players}")

    def get_role_description(self) -> str:
        """获取角色描述"""
        return (
            "你是预言家，属于好人阵营。\n"
            "每晚你可以查验一名玩家的身份（好人或狼人）。\n"
            "你是好人阵营的眼睛，请谨慎使用你的能力，并在白天合适的时机公布信息。"
        )

    def can_act_at_night(self, game_state: 'GameState') -> bool:
        """预言家存活就可以行动"""
        return True

    def get_available_actions(self, game_state: 'GameState') -> List[str]:
        """预言家可以查验或跳过"""
        return ["check", "skip"]

    async def perform_night_action(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> Optional['BaseAction']:
        """
        预言家的夜晚行动：查验玩家身份

        Args:
            player: 预言家玩家
            game_state: 游戏状态

        Returns:
            CheckAction: 查验行动，如果跳过则返回None
        """
        from actions.check_action import CheckAction

        # 获取可选目标（排除自己和已死亡的）
        available_targets = [
            p for p in game_state.alive_players
            if p.id != player.id
        ]

        if not available_targets:
            return None

        # 选择目标
        target = await player.choose_target(
            game_state=game_state,
            available_targets=available_targets,
            action_type="check"
        )

        if target:
            self.checked_players.append(target.id)
            return CheckAction(actor=player, target=target)

        return None

    def has_checked_player(self, player_id: int) -> bool:
        """检查是否已经查验过某个玩家"""
        return player_id in self.checked_players
