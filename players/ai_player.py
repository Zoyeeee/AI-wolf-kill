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
        # AI角色推理数据库：存储对其他玩家的角色推断
        # 格式: {player_id: {suspected_roles: [], camp_belief: str, confidence: str, reasoning: str}}
        self.role_beliefs = {}

    async def make_speech(self, game_state: 'GameState') -> str:
        """AI玩家发言 - 通过AI生成"""
        # 在发言前，先更新该AI对其他玩家的角色推理
        await self._update_role_beliefs_before_speech(game_state)

        speech = await self.ai.generate_speech(self, game_state)
        self.add_speech(speech)
        return speech

    async def _update_role_beliefs_before_speech(self, game_state: 'GameState'):
        """
        在发言前更新角色推理

        分析所有之前的发言，更新对其他玩家的角色推断
        """
        # 获取最近的几条发言（不包括自己）
        recent_speeches = []
        for record in game_state.conversation_history[-10:]:  # 最近10条记录
            if record.get('action_type') == 'speech' and record.get('player_id') != self.id:
                recent_speeches.append({
                    'player_id': record['player_id'],
                    'player_name': record['player_name'],
                    'content': record['content']
                })

        # 如果有新的发言，更新角色推理
        if recent_speeches:
            # 合并最近的发言为一个摘要
            speech_summary = "\n".join([
                f"{s['player_id']}号{s['player_name']}: {s['content']}"
                for s in recent_speeches[-3:]  # 只取最近3条
            ])

            try:
                await self.ai.update_role_beliefs(
                    self,
                    game_state,
                    recent_speeches[-1]['player_id'],  # 最后一个发言者
                    speech_summary
                )
            except Exception as e:
                # 更新失败不影响发言
                pass

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
        """AI决定是否竞选警长 - 通过AI智能决策"""
        return await self.ai.decide_sheriff_candidacy(self, game_state)

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
        """AI警长选择继承人 - 通过AI智能决策"""
        from roles.base_role import RoleCamp

        candidates = [p for p in game_state.alive_players if p.id != self.id]

        if not candidates:
            return None

        if self.role.camp == RoleCamp.WEREWOLF:
            # 狼人警长：使用AI智能选择对狼人胜利最有利的继承人
            choice = await self.ai.choose_sheriff_successor_strategically(
                self,
                game_state,
                candidates
            )
            return choice
        else:
            # 好人警长：使用AI智能选择基于角色分析
            choice = await self.ai.choose_sheriff_successor_for_good(
                self,
                game_state,
                candidates
            )
            return choice
