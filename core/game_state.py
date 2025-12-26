"""
游戏状态管理
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from players.player import Player
from roles.base_role import RoleCamp


class GameState:
    """
    游戏状态类

    管理游戏的所有状态信息
    """

    def __init__(self):
        # 基本信息
        self.game_id: str = ""
        self.round_number: int = 0
        self.current_phase: str = "init"  # init, night, day, vote, end
        self.board_config: str = "basic"  # 游戏板子配置

        # 玩家信息
        self.all_players: List[Player] = []
        self.alive_players: List[Player] = []
        self.dead_players: List[Player] = []

        # 夜晚行动结果
        self.tonight_victim: Optional[Player] = None  # 今晚被狼人杀的目标
        self.poisoned_tonight: List[Player] = []      # 今晚被毒的玩家
        self.saved_tonight: bool = False               # 今晚是否有人被救

        # 白天结果
        self.today_voted_out: Optional[Player] = None  # 今天被放逐的玩家

        # 历史记录
        self.conversation_history: List[Dict[str, Any]] = []
        self.action_history: List[Dict[str, Any]] = []

        # 私密对话系统（阵营内部对话）
        self.private_conversations: Dict[str, List[Dict]] = {
            "werewolf": [],  # 狼人私聊
            # 未来可扩展其他阵营
        }

        # 狼人夜晚协商状态
        self.werewolf_discussion_round: int = 0  # 当前讨论轮数
        self.werewolf_kill_votes: Dict[int, int] = {}  # {狼人ID: 目标ID}

        # 临时数据
        self.last_werewolf_target: Optional[str] = None
        self.last_night_victim_name: Optional[str] = None
        self.seer_check_results: Dict[int, List[str]] = {}

        # 警长系统
        self.sheriff_player_id: Optional[int] = None  # 警长玩家ID
        self.sheriff_election_done: bool = False      # 是否已完成警长竞选
        self.speaking_order_direction: str = "clockwise"  # 发言顺序方向
        self.last_death_seat: Optional[int] = None    # 最近死者座位号（取最小）

        # 女巫用药历史记录
        self.witch_action_history: List[Dict[str, Any]] = []
        # 格式：[
        #   {
        #       "round": 1,
        #       "action_type": "save",  # "save"/"poison"/"skip"
        #       "target_name": "玩家A",
        #       "target_id": 3,
        #       "remaining_antidote": False,
        #       "remaining_poison": True
        #   }
        # ]

    def add_speech(self, round_num: int, player: Player, content: str):
        """记录玩家发言"""
        self.conversation_history.append({
            "round": round_num,
            "phase": self.current_phase,
            "player_id": player.id,
            "player_name": player.name,
            "action_type": "speech",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def add_vote(self, round_num: int, voter: Player, target: Player):
        """记录投票"""
        self.conversation_history.append({
            "round": round_num,
            "phase": "vote",
            "player_id": voter.id,
            "player_name": voter.name,
            "action_type": "vote",
            "content": f"投票给{target.name}",
            "target_id": target.id,
            "timestamp": datetime.now().isoformat()
        })

    def add_announcement(self, round_num: int, content: str):
        """记录系统公告（夜晚死亡、投票结果等）"""
        self.conversation_history.append({
            "round": round_num,
            "phase": self.current_phase,
            "player_id": 0,  # 0表示系统
            "player_name": "系统",
            "action_type": "announcement",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_full_conversation_history(self) -> str:
        """获取格式化的完整对话历史"""
        if not self.conversation_history:
            return "暂无历史记录"

        history_lines = []
        for record in self.conversation_history[-30:]:  # 最近30条
            phase_name = {"night": "夜晚", "day": "白天", "vote": "投票"}.get(record['phase'], record['phase'])
            history_lines.append(
                f"[第{record['round']}轮-{phase_name}] "
                f"{record['player_name']}（{record['player_id']}号）: {record['content']}"
            )

        return "\n".join(history_lines)

    def get_player_speech_summary(self, player_id: int) -> str:
        """获取指定玩家的历史发言总结"""
        speeches = [
            r for r in self.conversation_history
            if r['player_id'] == player_id and r['action_type'] == 'speech'
        ]

        if not speeches:
            return "这是你的第一次发言"

        summary_lines = [f"你在第{s['round']}轮说过: {s['content'][:50]}..." for s in speeches[-5:]]
        return "\n".join(summary_lines)

    def get_player_voting_summary(self, player_id: int) -> str:
        """获取指定玩家的投票历史"""
        votes = [
            r for r in self.conversation_history
            if r['player_id'] == player_id and r['action_type'] == 'vote'
        ]

        if not votes:
            return "这是你的第一次投票"

        summary_lines = [f"第{v['round']}轮你{v['content']}" for v in votes[-3:]]
        return "\n".join(summary_lines)

    def get_alive_werewolves(self) -> List[Player]:
        """获取存活的狼人"""
        from roles.base_role import RoleType
        return [
            p for p in self.alive_players
            if p.role.role_type == RoleType.WEREWOLF
        ]

    def get_alive_villagers(self) -> List[Player]:
        """获取存活的好人"""
        return [
            p for p in self.alive_players
            if p.role.camp == RoleCamp.VILLAGER
        ]

    def check_werewolf_victory(self) -> bool:
        """
        检查狼人是否获胜

        标准规则：狼人数量 >= 好人数量
        原因：当狼人数量达到或超过好人数量时，狼人在投票中已掌控局面
        """
        werewolves = self.get_alive_werewolves()

        if len(werewolves) == 0:
            return False

        # 统计好人数量（所有非狼人阵营的玩家）
        good_guys = [p for p in self.alive_players
                     if p.role.camp == RoleCamp.VILLAGER]

        # 标准规则：狼人数 >= 好人数
        return len(werewolves) >= len(good_guys)

    def check_villager_victory(self) -> bool:
        """检查好人是否获胜"""
        werewolves = self.get_alive_werewolves()

        # 所有狼人都死了
        return len(werewolves) == 0

    def is_game_over(self) -> Optional[str]:
        """
        检查游戏是否结束

        Returns:
            Optional[str]: 获胜阵营名称，None表示游戏继续
        """
        if self.check_werewolf_victory():
            return "狼人阵营"
        elif self.check_villager_victory():
            return "好人阵营"
        return None

    def process_night_deaths(self) -> List[Player]:
        """
        处理夜晚的死亡

        Returns:
            List[Player]: 死亡的玩家列表
        """
        deaths = []

        # 处理狼人杀人
        if self.tonight_victim and not self.saved_tonight:
            self.tonight_victim.is_alive = False
            deaths.append(self.tonight_victim)
            self.last_night_victim_name = self.tonight_victim.name

        # 处理女巫毒人
        if self.poisoned_tonight:
            for victim in self.poisoned_tonight:
                if victim.is_alive:
                    victim.is_alive = False
                    deaths.append(victim)

        # 更新存活/死亡列表
        for dead_player in deaths:
            if dead_player in self.alive_players:
                self.alive_players.remove(dead_player)
                self.dead_players.append(dead_player)

        # 重置夜晚状态
        self.tonight_victim = None
        self.poisoned_tonight = []
        self.saved_tonight = False

        return deaths

    def add_private_speech(
        self,
        camp: str,  # "werewolf"
        round_num: int,
        player: Player,
        content: str
    ):
        """记录私密对话（只对同阵营可见）"""
        self.private_conversations[camp].append({
            "round": round_num,
            "phase": "night_private",
            "player_id": player.id,
            "player_name": player.name,
            "action_type": "private_speech",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_private_conversation_history(
        self,
        camp: str,
        max_records: int = 30
    ) -> str:
        """获取私密对话历史（仅限同阵营）"""
        records = self.private_conversations.get(camp, [])

        if not records:
            return "暂无私聊记录"

        history_lines = []
        for record in records[-max_records:]:
            history_lines.append(
                f"[第{record['round']}轮-狼人频道] "
                f"{record['player_name']}（{record['player_id']}号）: {record['content']}"
            )

        return "\n".join(history_lines)

    def get_combined_history_for_werewolf(self, player_id: int) -> str:
        """
        获取狼人能看到的完整历史（公开+私密）

        Returns:
            str: 包含公开对话和狼人私聊的完整历史
        """
        public_history = self.get_full_conversation_history()
        private_history = self.get_private_conversation_history("werewolf")

        return f"""【公开对话历史】
{public_history}

【狼人私聊历史】
{private_history}"""

    def reset_votes(self):
        """重置所有玩家的投票数"""
        for player in self.all_players:
            player.reset_votes()

    def set_sheriff(self, player_id: Optional[int]) -> None:
        """
        设置警长（同步更新 player.is_sheriff）

        Args:
            player_id: 警长玩家ID，None表示清除警长
        """
        # 清除旧警长标记
        for p in self.all_players:
            p.is_sheriff = False

        # 设置新警长
        self.sheriff_player_id = player_id
        if player_id:
            player = next((p for p in self.all_players if p.id == player_id), None)
            if player:
                player.is_sheriff = True

    def get_sheriff(self) -> Optional[Player]:
        """
        获取警长玩家对象

        Returns:
            Optional[Player]: 警长玩家对象，如果没有警长则返回None
        """
        if not self.sheriff_player_id:
            return None

        return next((p for p in self.all_players if p.id == self.sheriff_player_id), None)

    def transfer_sheriff(self, from_player_id: int, to_player_id: int) -> None:
        """
        转移警徽

        Args:
            from_player_id: 原警长ID
            to_player_id: 新警长ID
        """
        if self.sheriff_player_id == from_player_id:
            self.set_sheriff(to_player_id)

    def calculate_speaking_order(self) -> List[Player]:
        """
        计算本轮发言顺序

        Returns:
            List[Player]: 按发言顺序排列的存活玩家列表
        """
        alive = self.alive_players.copy()

        # 第一轮：随机顺序
        if self.round_number == 1:
            import random
            random.shuffle(alive)
            return alive

        # 无死者：按座位号顺序
        if not self.last_death_seat:
            return sorted(alive, key=lambda p: p.seat_number)

        # 从死者位置开始（根据警长选择的方向）
        direction = self.speaking_order_direction
        start_seat = self.get_next_seat(self.last_death_seat, direction)

        # 按座位号排序后旋转到起始位置
        sorted_players = sorted(alive, key=lambda p: p.seat_number)

        # 找到起始玩家索引
        start_index = 0
        for i, player in enumerate(sorted_players):
            if player.seat_number >= start_seat:
                start_index = i
                break

        # 旋转列表
        return sorted_players[start_index:] + sorted_players[:start_index]

    def get_next_seat(self, current_seat: int, direction: str) -> int:
        """
        获取下一个存活座位号（跳过死者）

        Args:
            current_seat: 当前座位号
            direction: 方向 ("clockwise"顺时针/死右, "counterclockwise"逆时针/死左)

        Returns:
            int: 下一个存活座位号
        """
        total_seats = len(self.all_players)

        if direction == "clockwise":
            # 死右：座位号增加方向
            next_seat = (current_seat % total_seats) + 1
        else:  # counterclockwise
            # 死左：座位号减少方向
            next_seat = ((current_seat - 2) % total_seats) + 1

        # 找到下一个存活玩家的座位
        alive_seats = sorted([p.seat_number for p in self.alive_players])

        # 循环查找下一个存活座位
        for _ in range(total_seats):
            if next_seat in alive_seats:
                return next_seat

            if direction == "clockwise":
                next_seat = (next_seat % total_seats) + 1
            else:
                next_seat = ((next_seat - 2) % total_seats) + 1

        # 默认返回第一个存活座位
        return alive_seats[0] if alive_seats else 1

    def record_witch_action(
        self,
        round_num: int,
        action_type: str,  # "save"/"poison"/"skip"
        target: Optional['Player'],
        remaining_antidote: bool,
        remaining_poison: bool
    ) -> None:
        """
        记录女巫用药历史

        Args:
            round_num: 轮次
            action_type: 行动类型（save/poison/skip）
            target: 目标玩家（如果是skip则为None）
            remaining_antidote: 剩余解药
            remaining_poison: 剩余毒药
        """
        self.witch_action_history.append({
            "round": round_num,
            "action_type": action_type,
            "target_name": target.name if target else "无",
            "target_id": target.id if target else 0,
            "remaining_antidote": remaining_antidote,
            "remaining_poison": remaining_poison,
            "timestamp": datetime.now().isoformat()
        })

    def get_witch_action_summary(self) -> str:
        """
        获取女巫用药历史摘要（供AI生成发言使用）

        Returns:
            str: 格式化的用药历史
        """
        if not self.witch_action_history:
            return "你还没有使用过任何药物"

        summary_lines = []
        for record in self.witch_action_history:
            round_num = record["round"]
            action_type = record["action_type"]
            target_name = record["target_name"]

            if action_type == "save":
                summary_lines.append(
                    f"第{round_num}轮：使用解药救了{target_name}"
                )
            elif action_type == "poison":
                summary_lines.append(
                    f"第{round_num}轮：使用毒药毒死了{target_name}"
                )
            elif action_type == "skip":
                summary_lines.append(
                    f"第{round_num}轮：没有使用任何药物"
                )

        # 添加当前剩余药物状态
        if self.witch_action_history:
            last_record = self.witch_action_history[-1]
            remaining = []
            if last_record["remaining_antidote"]:
                remaining.append("解药")
            if last_record["remaining_poison"]:
                remaining.append("毒药")

            if remaining:
                summary_lines.append(f"当前剩余：{', '.join(remaining)}")
            else:
                summary_lines.append("当前剩余：无药物")

        return "\n".join(summary_lines)

    def get_victory_reason(self, winner: str) -> str:
        """
        获取胜利原因的详细说明

        Args:
            winner: 获胜阵营（"狼人阵营" 或 "好人阵营"）

        Returns:
            str: 胜利原因的详细说明
        """
        werewolves = self.get_alive_werewolves()
        good_guys = [p for p in self.alive_players
                     if p.role.camp == RoleCamp.VILLAGER]

        if winner == "狼人阵营":
            if len(werewolves) >= len(good_guys):
                return f"""
【胜利原因】
当前局势：{len(werewolves)}只狼人 vs {len(good_guys)}个好人
根据标准狼人杀规则，当狼人数量 >= 好人数量时，狼人已在投票中掌控局面，游戏结束。

存活狼人：{', '.join([f'{w.name}（{w.id}号）' for w in werewolves])}
存活好人：{', '.join([f'{g.name}（{g.id}号，{g.role.role_type.value}）' for g in good_guys])}
"""
        elif winner == "好人阵营":
            return f"""
【胜利原因】
所有狼人已被淘汰！好人阵营成功保卫了村庄！

存活好人：{', '.join([f'{g.name}（{g.id}号，{g.role.role_type.value}）' for g in good_guys])}
"""

        return ""

    def __repr__(self) -> str:
        return (
            f"<GameState(round={self.round_number}, "
            f"alive={len(self.alive_players)}, "
            f"dead={len(self.dead_players)})>"
        )
