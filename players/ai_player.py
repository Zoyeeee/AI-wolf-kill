"""
AI玩家实现
"""
from typing import Optional, List, Tuple, TYPE_CHECKING
from players.player import Player

if TYPE_CHECKING:
    from roles.base_role import BaseRole
    from core.game_state import GameState
    from ai.player_ai import PlayerAI


class AIPlayer(Player):
    """
    AI玩家

    通过PlayerAI生成决策
    """

    def __init__(self, player_id: int, name: str, role: 'BaseRole', ai_client: 'PlayerAI'):
        super().__init__(player_id, name, role)
        self.ai = ai_client

    async def make_speech(self, game_state: 'GameState') -> str:
        """AI玩家发言 - 通过AI生成"""
        speech = await self.ai.generate_speech(self, game_state)
        self.add_speech(speech)
        return speech

    async def vote(self, game_state: 'GameState') -> Optional['Player']:
        """AI玩家投票 - 通过AI决策"""
        return await self.ai.make_vote_decision(self, game_state)

    async def choose_target(
        self,
        game_state: 'GameState',
        available_targets: List['Player'],
        action_type: str
    ) -> Optional['Player']:
        """AI玩家选择目标 - 通过AI决策"""
        return await self.ai.choose_action_target(
            self,
            game_state,
            available_targets,
            action_type
        )

    async def make_werewolf_discussion(
        self,
        game_state: 'GameState',
        round_idx: int
    ) -> str:
        """AI狼人在狼人频道发言"""
        return await self.ai.generate_werewolf_discussion(
            self,
            game_state,
            round_idx
        )

    async def choose_witch_action(
        self,
        game_state: 'GameState',
        witch_role: 'BaseRole'
    ) -> Optional[Tuple[str, 'Player']]:
        """AI女巫选择行动 - 通过AI决策"""
        return await self.ai.choose_witch_action(self, game_state, witch_role)

    async def decide_sheriff_candidacy(self, game_state: 'GameState') -> bool:
        """AI决定是否竞选警长"""
        from roles.base_role import RoleType, RoleCamp
        import random

        # 策略：神职70%/狼人50%/村民30%概率竞选
        if self.role.role_type in [RoleType.SEER, RoleType.WITCH, RoleType.HUNTER]:
            return random.random() < 0.7
        elif self.role.camp == RoleCamp.WEREWOLF:
            return random.random() < 0.5
        else:
            return random.random() < 0.3

    async def make_sheriff_campaign_speech(self, game_state: 'GameState') -> str:
        """AI生成竞选宣言"""
        return await self.ai.generate_sheriff_campaign_speech(self, game_state)

    async def vote_for_sheriff(
        self,
        game_state: 'GameState',
        candidates: List['Player']
    ) -> Optional['Player']:
        """AI投票选举警长"""
        from roles.base_role import RoleCamp
        import random

        if self.role.camp == RoleCamp.WEREWOLF:
            # 狼人优先投狼人候选人
            werewolf_candidates = [c for c in candidates if c.role.camp == RoleCamp.WEREWOLF]
            if werewolf_candidates:
                return random.choice(werewolf_candidates)

        # 否则随机选择
        return random.choice(candidates) if candidates else None

    async def choose_speaking_direction(self, game_state: 'GameState') -> str:
        """AI警长选择发言方向"""
        import random
        return random.choice(["clockwise", "counterclockwise"])

    async def choose_sheriff_successor(
        self,
        game_state: 'GameState'
    ) -> Optional['Player']:
        """AI警长选择继承人"""
        from roles.base_role import RoleCamp, RoleType
        import random

        candidates = [p for p in game_state.alive_players if p.id != self.id]

        if not candidates:
            return None

        if self.role.camp == RoleCamp.WEREWOLF:
            # 狼人警长：使用AI智能选择对狼人胜利最有利的继承人
            # 可以传给任何存活玩家（包括好人），策略性选择
            choice = await self.ai.choose_sheriff_successor_strategically(
                self,
                game_state,
                candidates
            )
            return choice
        else:
            # 好人警长传给神职
            gods = [c for c in candidates if c.role.role_type in [RoleType.SEER, RoleType.WITCH, RoleType.HUNTER]]
            if gods:
                return random.choice(gods)
            # 否则随机传给好人
            return random.choice(candidates)
