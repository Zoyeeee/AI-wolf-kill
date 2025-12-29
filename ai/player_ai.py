"""
玩家AI - 生成发言和决策
"""
import re
from typing import Optional, List, Tuple, TYPE_CHECKING
from ai.llm_client import llm_client
from ai.prompts import player_prompts
from roles.base_role import RoleType, RoleCamp
from config.game_config import GameConfig, ROLE_COMPOSITIONS

if TYPE_CHECKING:
    from players.player import Player
    from core.game_state import GameState


class PlayerAI:
    """
    玩家AI

    职责：
    - 生成发言
    - 做出投票决策
    - 选择行动目标
    """

    def __init__(self):
        self.llm = llm_client

    def _get_board_info(self, board_config: str) -> str:
        """
        生成板子配置信息描述

        Args:
            board_config: 板子配置名称

        Returns:
            str: 板子配置信息描述
        """
        role_composition = ROLE_COMPOSITIONS.get(board_config, ROLE_COMPOSITIONS["basic"])

        # 角色中文名映射
        role_names = {
            "werewolf": "狼人",
            "villager": "村民",
            "seer": "预言家",
            "witch": "女巫",
            "hunter": "猎人",
            "guard": "守卫"
        }

        # 生成角色列表
        role_list = []
        for role_key, count in role_composition.items():
            role_name = role_names.get(role_key, role_key)
            role_list.append(f"{role_name}x{count}")

        total_players = sum(role_composition.values())
        config_name = "基础版" if board_config == "basic" else "标准版"

        return f"""本局游戏：{config_name}（{total_players}人局）
角色配置：{', '.join(role_list)}"""

    def _get_good_god_roles(self, board_config: str) -> str:
        """
        获取好人神职列表（根据板子配置）

        Args:
            board_config: 板子配置名称

        Returns:
            str: 好人神职列表，用顿号分隔
        """
        role_composition = ROLE_COMPOSITIONS.get(board_config, ROLE_COMPOSITIONS["basic"])

        # 角色中文名映射
        role_names = {
            "seer": "预言家",
            "witch": "女巫",
            "hunter": "猎人",
            "guard": "守卫"
        }

        # 获取好人神职（排除狼人和村民）
        god_roles = []
        for role_key in role_composition.keys():
            if role_key not in ["werewolf", "villager"] and role_key in role_names:
                god_roles.append(role_names[role_key])

        return "、".join(god_roles) if god_roles else "无"

    async def generate_speech(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> str:
        """
        生成发言

        Args:
            player: 当前玩家
            game_state: 游戏状态

        Returns:
            str: 发言内容
        """
        # 根据阵营决定可见历史（权限控制）
        if player.role.camp == RoleCamp.WEREWOLF:
            # 狼人能看到公开对话 + 狼人私聊
            full_history = game_state.get_combined_history_for_werewolf(player.id)
        else:
            # 好人只能看到公开对话
            full_history = game_state.get_full_conversation_history()

        # 获取该玩家的历史发言
        player_history = game_state.get_player_speech_summary(player.id)

        # 根据角色选择提示词
        role_type = player.role.role_type

        if role_type == RoleType.WEREWOLF:
            prompt_template = player_prompts.WEREWOLF_SPEECH
            werewolf_target = game_state.last_werewolf_target or "未知"
        elif role_type == RoleType.SEER:
            prompt_template = player_prompts.SEER_SPEECH
        elif role_type == RoleType.WITCH:
            prompt_template = player_prompts.WITCH_SPEECH
        elif role_type == RoleType.HUNTER:
            prompt_template = player_prompts.HUNTER_SPEECH
        else:
            prompt_template = player_prompts.VILLAGER_SPEECH

        # 填充提示词
        alive_list = ", ".join([f"{p.name}（{p.id}号）" for p in game_state.alive_players])
        dead_list = ", ".join([f"{p.name}（{p.id}号）" for p in game_state.dead_players]) if game_state.dead_players else "无"

        # 生成板子信息
        board_info = self._get_board_info(game_state.board_config)
        good_god_roles = self._get_good_god_roles(game_state.board_config)

        prompt_data = {
            "player_name": player.name,
            "player_id": player.id,
            "round": game_state.round_number,
            "board_info": board_info,
            "good_god_roles": good_god_roles,
            "alive_players": alive_list,
            "dead_players": dead_list,
            "last_night_victim": getattr(game_state, 'last_night_victim_name', "无"),
            "full_conversation_history": full_history or "暂无历史记录",
            "your_previous_speeches": player_history or "这是你第一次发言",
        }

        # 狼人特有信息
        if role_type == RoleType.WEREWOLF:
            prompt_data["werewolf_target"] = getattr(game_state, 'last_werewolf_target', "未知")

        # 预言家特有信息
        if role_type == RoleType.SEER:
            prompt_data["check_results"] = getattr(game_state, 'seer_check_results', {}).get(player.id, "暂无")

        # 女巫特有信息
        if role_type == RoleType.WITCH:
            prompt_data["witch_action_history"] = game_state.get_witch_action_summary()

        prompt = prompt_template.format(**prompt_data)

        speech = await self.llm.generate(prompt)

        if not speech:
            speech = "我没什么要说的。"

        return speech

    async def generate_sheriff_campaign_speech(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> str:
        """
        生成警长竞选演讲

        Args:
            player: 当前玩家
            game_state: 游戏状态

        Returns:
            str: 竞选演讲内容
        """
        # 获取玩家的历史发言
        player_history = game_state.get_player_speech_summary(player.id)

        # 存活玩家列表
        alive_list = ", ".join([f"{p.name}（{p.id}号）" for p in game_state.alive_players])

        # 填充提示词
        prompt = player_prompts.SHERIFF_CAMPAIGN_SPEECH.format(
            player_name=player.name,
            player_id=player.id,
            role=player.role.role_type.value,
            alive_players=alive_list,
            round=game_state.round_number,
            your_previous_speeches=player_history or "暂无历史发言"
        )

        speech = await self.llm.generate(prompt)

        if not speech:
            speech = f"我是{player.name}，我想竞选警长，请大家支持我。"

        return speech

    async def generate_werewolf_discussion(
        self,
        player: 'Player',
        game_state: 'GameState',
        round_idx: int
    ) -> str:
        """
        生成狼人讨论发言

        Args:
            player: 狼人玩家
            game_state: 游戏状态
            round_idx: 讨论轮数

        Returns:
            str: 讨论内容
        """
        # 获取狼人能看到的完整历史（公开+私密）
        combined_history = game_state.get_combined_history_for_werewolf(player.id)

        # 获取狼人队友
        werewolves = game_state.get_alive_werewolves()
        teammates = [w for w in werewolves if w.id != player.id]

        # 获取可杀目标
        targets = [
            p for p in game_state.alive_players
            if p.role.camp != RoleCamp.WEREWOLF
        ]

        # 构建提示词
        prompt = player_prompts.WEREWOLF_DISCUSSION_PROMPT.format(
            player_name=player.name,
            player_id=player.id,
            round_idx=round_idx,
            max_rounds=3,
            teammates=", ".join([f"{t.name}（{t.id}号）" for t in teammates]) or "无其他队友",
            available_targets=", ".join([f"{t.name}（{t.id}号）" for t in targets]),
            combined_history=combined_history,
            private_history=game_state.get_private_conversation_history("werewolf")
        )

        speech = await self.llm.generate(prompt)

        if not speech:
            speech = "我建议我们杀掉最可疑的玩家。"

        return speech

    async def make_vote_decision(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> Optional['Player']:
        """
        做出投票决策

        Args:
            player: 当前玩家
            game_state: 游戏状态

        Returns:
            Optional[Player]: 投票目标
        """
        alive_players = [p for p in game_state.alive_players if p.id != player.id]
        if not alive_players:
            return None

        # 根据阵营决定可见历史（权限控制）
        if player.role.camp == RoleCamp.WEREWOLF:
            full_history = game_state.get_combined_history_for_werewolf(player.id)
        else:
            full_history = game_state.get_full_conversation_history()

        voting_history = game_state.get_player_voting_summary(player.id)
        alive_list = ", ".join([f"{p.name}（{p.id}号）" for p in alive_players])

        prompt = player_prompts.VOTE_DECISION.format(
            player_name=player.name,
            player_id=player.id,
            role=player.role.role_type.value,
            full_conversation_history=full_history or "暂无",
            your_voting_history=voting_history or "这是第一轮投票",
            alive_players=alive_list
        )

        response = await self.llm.generate(prompt)

        # 解析返回的玩家ID
        target_id = self._extract_player_id(response, alive_players)

        if target_id:
            for p in alive_players:
                if p.id == target_id:
                    return p

        # 默认随机选择
        import random
        return random.choice(alive_players) if alive_players else None

    async def choose_action_target(
        self,
        player: 'Player',
        game_state: 'GameState',
        available_targets: List['Player'],
        action_type: str
    ) -> Optional['Player']:
        """
        选择行动目标

        Args:
            player: 当前玩家
            game_state: 游戏状态
            available_targets: 可选目标
            action_type: 行动类型

        Returns:
            Optional[Player]: 选择的目标
        """
        if not available_targets:
            return None

        # 根据行动类型选择提示词
        if action_type == "kill":
            prompt_template = player_prompts.WEREWOLF_KILL_DECISION
            werewolves = [p for p in game_state.alive_players if p.role.role_type == RoleType.WEREWOLF]
            teammates = ", ".join([f"{w.name}（{w.id}号）" for w in werewolves if w.id != player.id])

            # 狼人能看到私聊历史
            conversation_history = game_state.get_combined_history_for_werewolf(player.id)

            prompt_data = {
                "player_name": player.name,
                "player_id": player.id,
                "werewolf_teammates": teammates or "只有你一个狼人",
                "full_conversation_history": conversation_history or "暂无",
                "available_targets": ", ".join([f"{t.name}（{t.id}号）" for t in available_targets])
            }

        elif action_type == "check":
            from roles.seer import Seer
            checked = []
            if isinstance(player.role, Seer):
                checked = [str(pid) for pid in player.role.checked_players]

            prompt_template = player_prompts.SEER_CHECK_DECISION
            prompt_data = {
                "player_name": player.name,
                "player_id": player.id,
                "checked_players": ", ".join(checked) or "暂无",
                "alive_players": ", ".join([f"{t.name}（{t.id}号）" for t in available_targets]),
                "full_conversation_history": game_state.get_full_conversation_history() or "暂无"
            }

        else:
            # 其他行动类型简化处理
            import random
            return random.choice(available_targets) if available_targets else None

        prompt = prompt_template.format(**prompt_data)
        response = await self.llm.generate(prompt)

        # 解析目标ID
        target_id = self._extract_player_id(response, available_targets)

        if target_id == 0:  # 跳过
            return None

        if target_id:
            for t in available_targets:
                if t.id == target_id:
                    return t

        # 默认随机选择
        import random
        return random.choice(available_targets) if available_targets else None

    async def choose_witch_action(
        self,
        player: 'Player',
        game_state: 'GameState',
        witch_role
    ) -> Optional[Tuple[str, 'Player']]:
        """
        女巫选择行动

        Args:
            player: 女巫玩家
            game_state: 游戏状态
            witch_role: 女巫角色对象

        Returns:
            Optional[Tuple[str, Player]]: (行动类型, 目标)
        """
        # 简化实现：随机决策
        import random

        actions = []

        # 女巫不能救自己
        if witch_role.has_antidote and game_state.tonight_victim:
            if game_state.tonight_victim.id != player.id:
                actions.append(("save", game_state.tonight_victim))

        if witch_role.has_poison:
            alive = [p for p in game_state.alive_players if p.id != player.id]
            if alive:
                actions.append(("poison", random.choice(alive)))

        if not actions:
            return None

        # 30%概率跳过
        if random.random() < 0.3:
            return None

        return random.choice(actions)

    async def choose_sheriff_successor_strategically(
        self,
        player: 'Player',
        game_state: 'GameState',
        candidates: List['Player']
    ) -> Optional['Player']:
        """
        狼人警长智能选择警徽继承人

        策略：选择对狼人阵营胜利最有利的玩家
        - 可以传给狼人队友
        - 也可以传给好人中最不可能带领好人胜利的玩家
        - 或者撕毁警徽

        Args:
            player: 狼人警长
            game_state: 游戏状态
            candidates: 可选继承人列表

        Returns:
            Optional[Player]: 选择的继承人，None表示撕毁警徽
        """
        if not candidates:
            return None

        # 获取狼人能看到的完整历史
        combined_history = game_state.get_combined_history_for_werewolf(player.id)

        # 获取狼人队友信息
        werewolves = game_state.get_alive_werewolves()
        werewolf_candidates = [c for c in candidates if c.role.camp == RoleCamp.WEREWOLF]

        # 构建候选人列表信息
        candidate_info = []
        for c in candidates:
            is_werewolf = "是" if c in werewolf_candidates else "否"
            candidate_info.append(f"{c.name}（{c.id}号）- 是否狼人：{is_werewolf}")

        # 构建提示词
        prompt = player_prompts.WEREWOLF_SHERIFF_SUCCESSION.format(
            player_name=player.name,
            player_id=player.id,
            werewolf_count=len(werewolves),
            good_count=len(game_state.alive_players) - len(werewolves),
            candidates="\n".join(candidate_info),
            full_history=combined_history or "暂无历史",
            round=game_state.round_number
        )

        response = await self.llm.generate(prompt)

        # 解析目标ID
        target_id = self._extract_player_id(response, candidates)

        if target_id == 0:  # 0表示撕毁警徽
            return None

        if target_id:
            for c in candidates:
                if c.id == target_id:
                    return c

        # 默认策略：优先传给狼队友，否则随机
        import random
        if werewolf_candidates:
            return random.choice(werewolf_candidates)
        else:
            # 没有狼队友时，有50%概率撕毁警徽，50%概率传给好人
            if random.random() < 0.5:
                return None
            else:
                return random.choice(candidates)

    def _extract_player_id(self, text: str, available_players: List['Player']) -> Optional[int]:
        """
        从文本中提取玩家ID

        Args:
            text: 文本
            available_players: 可选玩家列表

        Returns:
            Optional[int]: 提取的玩家ID
        """
        # 提取所有数字
        numbers = re.findall(r'\d+', text)

        if not numbers:
            return None

        # 尝试匹配可用玩家ID
        available_ids = [p.id for p in available_players] + [0]  # 0表示跳过

        for num_str in numbers:
            num = int(num_str)
            if num in available_ids:
                return num

        return None

    async def decide_sheriff_candidacy(
        self,
        player: 'Player',
        game_state: 'GameState'
    ) -> bool:
        """
        AI决定是否竞选警长

        Args:
            player: 当前玩家
            game_state: 游戏状态

        Returns:
            bool: 是否竞选警长
        """
        # 获取历史记录
        if player.role.camp == RoleCamp.WEREWOLF:
            full_history = game_state.get_combined_history_for_werewolf(player.id)
        else:
            full_history = game_state.get_full_conversation_history()

        # 获取角色分析
        role_analysis = self._get_role_analysis_summary(player)

        alive_list = ", ".join([f"{p.name}（{p.id}号）" for p in game_state.alive_players])

        prompt = player_prompts.SHERIFF_CANDIDACY_DECISION.format(
            player_name=player.name,
            player_id=player.id,
            role=player.role.role_type.value,
            round=game_state.round_number,
            alive_players=alive_list,
            full_history=full_history or "暂无历史记录",
            role_analysis=role_analysis
        )

        response = await self.llm.generate(prompt)

        # 解析返回结果
        if response and "yes" in response.lower():
            return True
        else:
            return False

    async def choose_sheriff_successor_for_good(
        self,
        player: 'Player',
        game_state: 'GameState',
        candidates: List['Player']
    ) -> Optional['Player']:
        """
        好人警长智能选择警徽继承人

        Args:
            player: 好人警长
            game_state: 游戏状态
            candidates: 可选继承人列表

        Returns:
            Optional[Player]: 选择的继承人，None表示撕毁警徽
        """
        if not candidates:
            return None

        # 获取历史记录
        full_history = game_state.get_full_conversation_history()

        # 获取角色分析
        role_analysis = self._get_role_analysis_summary(player)

        # 获取可见信息
        visible_info = self._get_visible_info(player, game_state)

        # 构建候选人列表信息
        candidate_info = []
        for c in candidates:
            candidate_info.append(f"{c.name}（{c.id}号）")

        # 估计存活狼人和好人数量
        werewolves = game_state.get_alive_werewolves()
        good_guys = [p for p in game_state.alive_players if p.role.camp == RoleCamp.VILLAGER]

        # 构建提示词
        prompt = player_prompts.GOOD_SHERIFF_SUCCESSION.format(
            player_name=player.name,
            player_id=player.id,
            role=player.role.role_type.value,
            werewolf_count=len(werewolves),
            good_count=len(good_guys),
            candidates="\n".join(candidate_info),
            full_history=full_history or "暂无历史",
            role_analysis=role_analysis,
            visible_info=visible_info,
            round=game_state.round_number
        )

        response = await self.llm.generate(prompt)

        # 解析目标ID
        target_id = self._extract_player_id(response, candidates)

        if target_id == 0:  # 0表示撕毁警徽
            return None

        if target_id:
            for c in candidates:
                if c.id == target_id:
                    return c

        # 默认随机选择
        import random
        return random.choice(candidates) if candidates else None

    async def update_role_beliefs(
        self,
        player: 'Player',
        game_state: 'GameState',
        recent_speaker_id: int,
        recent_speech: str
    ) -> None:
        """
        更新AI对其他玩家角色的推理分析

        Args:
            player: 当前AI玩家
            game_state: 游戏状态
            recent_speaker_id: 最近发言的玩家ID
            recent_speech: 最近的发言内容
        """
        # 获取历史记录
        if player.role.camp == RoleCamp.WEREWOLF:
            full_history = game_state.get_combined_history_for_werewolf(player.id)
        else:
            full_history = game_state.get_full_conversation_history()

        # 获取当前推理
        current_beliefs = self._get_role_analysis_summary(player)

        # 获取可见信息
        visible_info = self._get_visible_info(player, game_state)

        alive_list = ", ".join([f"{p.name}（{p.id}号）" for p in game_state.alive_players])

        # 构建提示词
        prompt = player_prompts.UPDATE_ROLE_BELIEFS.format(
            player_name=player.name,
            player_id=player.id,
            role=player.role.role_type.value,
            recent_speech=f"{recent_speaker_id}号玩家: {recent_speech}",
            round=game_state.round_number,
            alive_players=alive_list,
            full_history=full_history or "暂无历史记录",
            current_beliefs=current_beliefs,
            visible_info=visible_info
        )

        response = await self.llm.generate(prompt)

        # 解析JSON并更新player的role_beliefs
        try:
            import json
            # 提取JSON内容
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                beliefs_data = json.loads(json_match.group())
                # 更新玩家的角色推理数据
                if hasattr(player, 'role_beliefs'):
                    player.role_beliefs = beliefs_data
        except Exception as e:
            # 解析失败时保持原有推理不变
            pass

    def _get_role_analysis_summary(self, player: 'Player') -> str:
        """
        获取AI对其他玩家的角色分析摘要

        Args:
            player: 当前玩家

        Returns:
            str: 角色分析摘要
        """
        if not hasattr(player, 'role_beliefs') or not player.role_beliefs:
            return "暂无角色分析数据"

        summary_lines = []
        for pid, analysis in player.role_beliefs.items():
            suspected_roles = ", ".join(analysis.get('suspected_roles', ['未知']))
            camp = analysis.get('camp_belief', 'unknown')
            confidence = analysis.get('confidence', 'low')
            reasoning = analysis.get('reasoning', '暂无')

            camp_cn = {"good": "好人", "werewolf": "狼人", "unknown": "未知"}.get(camp, "未知")
            confidence_cn = {"high": "高", "medium": "中", "low": "低"}.get(confidence, "低")

            summary_lines.append(
                f"{pid}号玩家: 可能是{suspected_roles}, "
                f"阵营倾向={camp_cn}, 信心={confidence_cn}, "
                f"依据: {reasoning}"
            )

        return "\n".join(summary_lines) if summary_lines else "暂无角色分析数据"

    def _get_visible_info(self, player: 'Player', game_state: 'GameState') -> str:
        """
        获取玩家的可见信息（根据角色不同）

        Args:
            player: 当前玩家
            game_state: 游戏状态

        Returns:
            str: 可见信息摘要
        """
        info_lines = []

        # 预言家的查验结果
        if player.role.role_type == RoleType.SEER:
            check_results = game_state.seer_check_results.get(player.id, [])
            if check_results:
                info_lines.append("【预言家查验结果】")
                for result in check_results:
                    info_lines.append(f"  {result}")
            else:
                info_lines.append("【预言家查验结果】暂无")

        # 女巫的用药历史
        elif player.role.role_type == RoleType.WITCH:
            witch_history = game_state.get_witch_action_summary()
            info_lines.append("【女巫用药历史】")
            info_lines.append(f"  {witch_history}")

        # 狼人知道队友
        elif player.role.camp == RoleCamp.WEREWOLF:
            werewolves = game_state.get_alive_werewolves()
            teammates = [w for w in werewolves if w.id != player.id]
            if teammates:
                info_lines.append("【狼人队友】")
                for t in teammates:
                    info_lines.append(f"  {t.name}（{t.id}号）")
            else:
                info_lines.append("【狼人队友】无其他队友")

        # 普通村民和猎人没有特殊可见信息
        else:
            info_lines.append("【可见信息】无特殊信息")

        return "\n".join(info_lines)
