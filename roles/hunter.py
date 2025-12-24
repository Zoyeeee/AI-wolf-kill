"""
猎人角色实现
"""
from typing import Optional, List, TYPE_CHECKING
from roles.base_role import BaseRole, RoleType, RoleCamp

if TYPE_CHECKING:
    from core.game_state import GameState
    from players.player import Player
    from actions.base_action import BaseAction


class Hunter(BaseRole):
    """
    猎人角色

    特点：
    - 属于好人阵营
    - 没有夜晚行动
    - 特殊能力：死亡时可以开枪带走一名玩家
    - 注意：被女巫毒死不能开枪
    """

    def __init__(self):
        super().__init__()
        self.role_type = RoleType.HUNTER
        self.camp = RoleCamp.VILLAGER
        self.has_night_action = False
        self.action_priority = 999  # 不参与夜晚行动排序
        self.can_shoot = True       # 是否可以开枪

    def get_role_description(self) -> str:
        """获取角色描述"""
        return (
            "你是猎人，属于好人阵营。\n"
            "你没有夜晚行动，但拥有强大的被动技能：\n"
            "当你死亡时（被狼人杀死或被投票放逐），你可以开枪带走一名玩家。\n"
            "注意：如果你被女巫毒死，则不能开枪。"
        )

    def can_act_at_night(self, game_state: 'GameState') -> bool:
        """猎人没有夜晚行动"""
        return False

    def get_available_actions(self, game_state: 'GameState') -> List[str]:
        """猎人没有主动行动"""
        return []

    async def perform_night_action(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> Optional['BaseAction']:
        """猎人没有夜晚行动"""
        return None

    def on_death(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> Optional['BaseAction']:
        """
        猎人死亡时触发：开枪

        Args:
            player: 猎人玩家
            game_state: 游戏状态

        Returns:
            ShootAction: 开枪行动，如果不能开枪则返回None
        """
        if not self.can_shoot:
            return None

        # 导入放在这里避免循环导入
        from actions.shoot_action import ShootAction

        # 获取可选目标（所有存活玩家）
        available_targets = game_state.alive_players.copy()

        if not available_targets:
            return None

        # 注意：这是同步调用，因为死亡事件处理时需要立即获得目标
        # 实际实现中可能需要特殊处理
        import asyncio
        try:
            target = asyncio.create_task(player.choose_target(
                game_state=game_state,
                available_targets=available_targets,
                action_type="shoot"
            ))
            target_result = asyncio.run(asyncio.wait_for(target, timeout=30))

            if target_result:
                self.can_shoot = False
                return ShootAction(actor=player, target=target_result)
        except Exception:
            pass

        return None

    def disable_shoot(self):
        """禁用开枪能力（被女巫毒死时调用）"""
        self.can_shoot = False
