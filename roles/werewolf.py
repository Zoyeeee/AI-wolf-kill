"""
狼人角色实现
"""
from typing import Optional, List, TYPE_CHECKING
from roles.base_role import BaseRole, RoleType, RoleCamp

if TYPE_CHECKING:
    from core.game_state import GameState
    from players.player import Player
    from actions.base_action import BaseAction


class Werewolf(BaseRole):
    """
    狼人角色

    特点：
    - 属于狼人阵营
    - 夜晚可以杀人
    - 行动优先级最高（优先级1）
    - 多个狼人需要协商选择目标
    """

    def __init__(self):
        super().__init__()
        self.role_type = RoleType.WEREWOLF
        self.camp = RoleCamp.WEREWOLF
        self.has_night_action = True
        self.action_priority = 1  # 狼人最先行动

    def get_role_description(self) -> str:
        """获取角色描述"""
        return (
            "你是狼人，属于狼人阵营。\n"
            "每晚你可以与同伴协商，选择杀死一名玩家。\n"
            "你的目标是消灭所有好人，或让好人数量不多于狼人数量。"
        )

    def can_act_at_night(self, game_state: 'GameState') -> bool:
        """狼人只要有存活就可以行动"""
        return len(game_state.get_alive_werewolves()) > 0

    def get_available_actions(self, game_state: 'GameState') -> List[str]:
        """狼人可以杀人或跳过"""
        return ["kill", "skip"]

    async def perform_night_action(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> Optional['BaseAction']:
        """
        狼人的夜晚行动：选择杀人目标

        Args:
            player: 当前狼人玩家
            game_state: 游戏状态

        Returns:
            KillAction: 杀人行动，如果跳过则返回None
        """
        # 导入放在这里避免循环导入
        from actions.kill_action import KillAction

        # 获取所有存活的狼人
        werewolves = game_state.get_alive_werewolves()

        # 获取可选目标（排除狼人自己）
        available_targets = [
            p for p in game_state.alive_players
            if p.role.camp != RoleCamp.WEREWOLF
        ]

        if not available_targets:
            return None

        # 选择目标（如果是AI玩家会通过AI选择，真人玩家通过CLI选择）
        target = await player.choose_target(
            game_state=game_state,
            available_targets=available_targets,
            action_type="kill"
        )

        if target:
            return KillAction(actor=player, target=target)

        return None
