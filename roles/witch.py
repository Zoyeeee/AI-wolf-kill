"""
女巫角色实现
"""
from typing import Optional, List, TYPE_CHECKING
from roles.base_role import BaseRole, RoleType, RoleCamp

if TYPE_CHECKING:
    from core.game_state import GameState
    from players.player import Player
    from actions.base_action import BaseAction


class Witch(BaseRole):
    """
    女巫角色

    特点：
    - 属于好人阵营
    - 拥有一瓶解药和一瓶毒药
    - 解药可以救人，毒药可以毒人
    - 每晚最多使用一瓶药
    - 行动优先级3（在狼人和预言家之后）
    """

    def __init__(self):
        super().__init__()
        self.role_type = RoleType.WITCH
        self.camp = RoleCamp.VILLAGER
        self.has_night_action = True
        self.action_priority = 3  # 在狼人和预言家之后
        self.has_antidote = True  # 是否还有解药
        self.has_poison = True    # 是否还有毒药
        self.used_antidote_on_self = False  # 是否用解药救过自己
        # DEBUG: 确认每次都创建新的女巫实例
        import random
        self._instance_id = random.randint(1000, 9999)
        # print(f"[DEBUG] 创建新女巫实例 {self._instance_id}, 解药={self.has_antidote}, 毒药={self.has_poison}")

    def get_role_description(self) -> str:
        """获取角色描述"""
        return (
            "你是女巫，属于好人阵营。\n"
            "你拥有一瓶解药和一瓶毒药，整个游戏中各只能使用一次。\n"
            "解药：可以救活当晚被狼人杀死的玩家。\n"
            "毒药：可以毒死一名玩家。\n"
            "每晚最多使用一瓶药。"
        )

    def can_act_at_night(self, game_state: 'GameState') -> bool:
        """女巫只要还有药就可以行动"""
        return self.has_antidote or self.has_poison

    def get_available_actions(self, game_state: 'GameState') -> List[str]:
        """
        女巫可用的行动

        根据当前状态返回：
        - 如果有解药且今晚有人被杀：可以选择救人
        - 如果有毒药：可以选择毒人
        - 总是可以选择跳过
        """
        actions = ["skip"]

        # 如果有解药且今晚有受害者，可以救人
        if self.has_antidote and game_state.tonight_victim:
            actions.append("save")

        # 如果有毒药，可以毒人
        if self.has_poison:
            actions.append("poison")

        return actions

    async def perform_night_action(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> Optional['BaseAction']:
        """
        女巫的夜晚行动：使用解药或毒药

        Args:
            player: 女巫玩家
            game_state: 游戏状态

        Returns:
            SaveAction或PoisonAction，如果跳过则返回None
        """
        # 导入行动类
        from actions.save_action import SaveAction
        from actions.poison_action import PoisonAction

        # 让玩家选择行动（救人、毒人或跳过）
        action_choice = await player.choose_witch_action(
            game_state=game_state,
            witch_role=self
        )

        if action_choice is None:
            return None

        action_type, target = action_choice

        if action_type == "save" and self.has_antidote:
            # 使用解药救人
            self.has_antidote = False
            if target.id == player.id:
                self.used_antidote_on_self = True
            return SaveAction(actor=player, target=target)

        elif action_type == "poison" and self.has_poison:
            # 使用毒药毒人
            self.has_poison = False
            return PoisonAction(actor=player, target=target)

        return None

    def get_remaining_potions(self) -> str:
        """获取剩余药水的描述"""
        potions = []
        if self.has_antidote:
            potions.append("解药")
        if self.has_poison:
            potions.append("毒药")

        if not potions:
            return "无剩余药水"

        return f"剩余：{', '.join(potions)}"
