"""
狼人杀游戏 - 主程序入口
"""
import asyncio
import uuid
from typing import List

from config.settings import settings
from config.game_config import game_config, GameConfig
from core.game_state import GameState
from roles.role_factory import RoleFactory
from roles.base_role import RoleCamp
from players.player import Player
from players.human_player import HumanPlayer
from players.ai_player import AIPlayer
from ai.god_ai import GodAI
from ai.player_ai import PlayerAI
from ui.cli import CLI
from ui.display import Display


class WolfkillGame:
    """狼人杀游戏主类"""

    def __init__(self):
        self.game_state = GameState()
        self.god_ai = GodAI()
        self.player_ai = PlayerAI()

        # 调试信息：确认每次都创建新实例
        import random
        self.instance_id = random.randint(10000, 99999)
        print(f"[DEBUG] 创建新游戏实例 ID: {self.instance_id}")

    async def setup_game(self):
        """设置游戏"""
        CLI.print_header("狼人杀游戏")

        print("欢迎来到狼人杀游戏！")
        print("\n请选择游戏板子：")
        print("1. 基础版（9人局）")
        print("   - 狼人x3, 村民x3, 预言家x1, 女巫x1, 猎人x1")
        print("2. 标准版（12人局）[暂未实现守卫角色]")
        print("   - 狼人x4, 村民x4, 预言家x1, 女巫x1, 猎人x1, 守卫x1")

        choice = await CLI.get_number_input("\n请输入选择（1-2）: ", min_val=1, max_val=2)

        # 根据选择确定配置
        if choice == 1:
            board_config = "basic"
            board_name = "基础版（9人局）"
        else:
            print("\n⚠️  警告：守卫角色暂未实现，将使用基础版配置")
            board_config = "basic"
            board_name = "基础版（9人局）"

        print(f"\n已选择：{board_name}")
        print("- 模式：单人 vs AI\n")

        # 创建游戏ID
        self.game_state.game_id = str(uuid.uuid4())[:8]

        # 设置板子配置
        self.game_state.board_config = board_config

        # 分配角色
        roles = RoleFactory.distribute_roles(board_config)
        total_players = len(roles)

        # 获取玩家名字
        human_name = await CLI.get_input("请输入你的名字: ")

        # 创建玩家
        players: List[Player] = []

        # 创建真人玩家（1号玩家）
        human_player = HumanPlayer(1, human_name, roles[0])
        players.append(human_player)

        # 创建AI玩家（2到total_players号）
        for i in range(2, total_players + 1):
            ai_name = f"AI-{i}"
            ai_player = AIPlayer(i, ai_name, roles[i-1], self.player_ai)
            players.append(ai_player)

        self.game_state.all_players = players
        self.game_state.alive_players = players.copy()
        self.game_state.dead_players = []

        # 显示你的角色
        CLI.print_section("角色分配")
        print(f"你的角色是：{human_player.role.role_type.value}")
        print(f"阵营：{human_player.role.camp.value}")
        print(f"\n角色描述：")
        print(human_player.role.get_role_description())

        input("\n按回车键开始游戏...")

    def get_human_player(self) -> Player:
        """获取真人玩家"""
        for player in self.game_state.all_players:
            if isinstance(player, HumanPlayer):
                return player
        return None

    async def run_game(self):
        """运行游戏主循环"""
        print("\n" + "="*50)
        print("游戏开始！")
        print("="*50)

        while True:
            self.game_state.round_number += 1

            # 夜晚阶段
            await self.night_phase()

            # 检查游戏是否结束
            winner = self.game_state.is_game_over()
            if winner:
                await self.end_game(winner)
                break

            # 白天阶段
            await self.day_phase()

            # 完整检查胜负（包括好人和狼人）
            winner = self.game_state.is_game_over()
            if winner:
                await self.end_game(winner)
                break

            # 投票阶段
            await self.vote_phase()

            # 检查游戏是否结束
            winner = self.game_state.is_game_over()
            if winner:
                await self.end_game(winner)
                break

    async def night_phase(self):
        """夜晚阶段 - 完整实现"""
        # 显示轮次信息
        self.show_round_info()

        CLI.print_header(f"第{self.game_state.round_number}轮 - 夜晚")

        self.game_state.current_phase = "night"

        # 上帝宣布
        message = await self.god_ai.announce_night_start(self.game_state.round_number)
        print(f"\n{message}\n")

        await asyncio.sleep(1)

        # 1. 狼人协商阶段（优先级1）
        await self.werewolf_discussion_phase()

        # 2. 预言家查验（优先级2）- 简化实现
        await self.seer_check_phase()

        # 3. 女巫用药（优先级3）
        await self.witch_action_phase()

    async def werewolf_discussion_phase(self):
        """狼人协商阶段"""
        werewolves = self.game_state.get_alive_werewolves()

        if not werewolves:
            return

        # 判断是否显示狼人频道给真人玩家
        human_player = self.get_human_player()
        is_human_werewolf = (
            human_player and
            human_player.role.camp == RoleCamp.WEREWOLF and
            human_player.is_alive
        )

        if is_human_werewolf:
            CLI.print_section("🐺 狼人频道（只有你能看到）")
            print(f"存活狼人：{', '.join([w.name for w in werewolves])}\n")

        # 3轮讨论
        MAX_DISCUSSION_ROUNDS = 3

        for round_idx in range(1, MAX_DISCUSSION_ROUNDS + 1):
            if is_human_werewolf:
                print(f"\n--- 第{round_idx}轮讨论 ---\n")

            self.game_state.werewolf_discussion_round = round_idx

            for werewolf in werewolves:
                # 生成狼人的讨论内容
                speech = await werewolf.make_werewolf_discussion(
                    self.game_state,
                    round_idx
                )

                # 记录到私密对话
                self.game_state.add_private_speech(
                    "werewolf",
                    self.game_state.round_number,
                    werewolf,
                    speech
                )

                # 只对真人狼人显示
                if is_human_werewolf:
                    formatted = f"[狼人频道] {werewolf.name}（{werewolf.id}号）: {speech}"
                    print(formatted)

                await asyncio.sleep(0.5)

        # 讨论结束，每个狼人选择目标
        if is_human_werewolf:
            print(f"\n--- 讨论结束，请选择杀人目标 ---\n")
            print("提示：可以选择空刀(不杀人)，也可以自刀(杀死狼人)")

        # 狼人可以杀任何存活玩家，包括自己和其他狼人
        available_targets = self.game_state.alive_players.copy()

        if not available_targets:
            return

        # 收集投票
        votes = {}
        for werewolf in werewolves:
            target = await werewolf.choose_target(
                self.game_state,
                available_targets,
                "kill"
            )

            if target:
                votes[werewolf.id] = target.id

                if is_human_werewolf:
                    # 标注是否自刀
                    if target.role.camp == RoleCamp.WEREWOLF:
                        print(f"{werewolf.name} 选择自刀 {target.name}")
                    else:
                        print(f"{werewolf.name} 选择杀死 {target.name}")

        # 统计票数
        if not votes:
            if is_human_werewolf:
                print("\n狼人选择空刀。")
            else:
                print("\n[系统] 狼人今夜未行动")
            # 空刀，不设置受害者
            self.game_state.tonight_victim = None
            self.game_state.last_werewolf_target = "空刀"
            return

        from collections import Counter
        vote_counter = Counter(votes.values())
        max_votes = max(vote_counter.values())
        candidates = [tid for tid, count in vote_counter.items() if count == max_votes]

        # 平票随机选择
        import random
        chosen_target_id = random.choice(candidates)

        # 找到目标玩家
        target = next(p for p in self.game_state.alive_players if p.id == chosen_target_id)

        if is_human_werewolf:
            if len(candidates) > 1:
                print(f"\n平票！随机选择了 {target.name}")
            else:
                # 标注是否自刀
                if target.role.camp == RoleCamp.WEREWOLF:
                    print(f"\n最终决定：自刀 {target.name}")
                else:
                    print(f"\n最终决定：杀死 {target.name}")

        # 设置今晚的受害者
        self.game_state.tonight_victim = target
        self.game_state.last_werewolf_target = target.name

        # 系统提示（新增）
        if not is_human_werewolf:
            print("\n[系统] 狼人已确定今夜目标")

    async def seer_check_phase(self):
        """预言家查验阶段"""
        from roles.base_role import RoleType

        # 找到存活的预言家
        seer = None
        for player in self.game_state.alive_players:
            if player.role.role_type == RoleType.SEER:
                seer = player
                break

        if not seer:
            await asyncio.sleep(0.5)
            return

        # 判断是否是真人预言家
        human_player = self.get_human_player()
        is_human_seer = (
            human_player and
            human_player.id == seer.id and
            human_player.is_alive
        )

        if is_human_seer:
            CLI.print_section("🔮 预言家查验")

        # 获取可查验的目标
        available_targets = [p for p in self.game_state.alive_players if p.id != seer.id]

        if not available_targets:
            return

        # 预言家选择查验目标
        target = await seer.choose_target(
            self.game_state,
            available_targets,
            "check"
        )

        if target:
            # 查验结果
            result = "狼人" if target.role.camp == RoleCamp.WEREWOLF else "好人"

            if is_human_seer:
                print(f"\n你查验了 {target.name}（{target.id}号），TA 是：{result}")

            # 记录查验结果
            if seer.id not in self.game_state.seer_check_results:
                self.game_state.seer_check_results[seer.id] = []
            self.game_state.seer_check_results[seer.id].append(
                f"{target.name}（{target.id}号）是{result}"
            )

            # 系统提示（新增）
            if not is_human_seer:
                print("\n[系统] 预言家已完成查验")
        else:
            # 系统提示（新增）
            if not is_human_seer:
                print("\n[系统] 预言家未查验")

        await asyncio.sleep(0.5)

    async def witch_action_phase(self):
        """女巫用药阶段"""
        from roles.base_role import RoleType

        # 找到存活的女巫
        witch_player = None
        for player in self.game_state.alive_players:
            if player.role.role_type == RoleType.WITCH:
                witch_player = player
                break

        if not witch_player:
            await asyncio.sleep(0.5)
            return

        # 检查女巫是否还有药
        witch_role = witch_player.role
        if not witch_role.has_antidote and not witch_role.has_poison:
            await asyncio.sleep(0.5)
            return

        # 判断是否是真人女巫
        human_player = self.get_human_player()
        is_human_witch = (
            human_player and
            human_player.id == witch_player.id and
            human_player.is_alive
        )

        if is_human_witch:
            CLI.print_section("💊 女巫行动")
            print(f"剩余药水：{witch_role.get_remaining_potions()}")

        # 女巫选择行动
        action_result = await witch_player.choose_witch_action(
            self.game_state,
            witch_role
        )

        if action_result:
            action_type, target = action_result

            if action_type == "save":
                # 使用解药
                self.game_state.saved_tonight = True
                witch_role.has_antidote = False
                if is_human_witch:
                    print(f"\n你使用了解药，救了 {target.name}")

                # 记录到历史
                self.game_state.record_witch_action(
                    round_num=self.game_state.round_number,
                    action_type="save",
                    target=target,
                    remaining_antidote=witch_role.has_antidote,
                    remaining_poison=witch_role.has_poison
                )

                # 系统提示（新增）
                if not is_human_witch:
                    print("\n[系统] 女巫已使用药物")

            elif action_type == "poison":
                # 使用毒药
                self.game_state.poisoned_tonight.append(target)
                witch_role.has_poison = False
                if is_human_witch:
                    print(f"\n你使用了毒药，毒死了 {target.name}")

                # 记录到历史
                self.game_state.record_witch_action(
                    round_num=self.game_state.round_number,
                    action_type="poison",
                    target=target,
                    remaining_antidote=witch_role.has_antidote,
                    remaining_poison=witch_role.has_poison
                )

                # 系统提示（新增）
                if not is_human_witch:
                    print("\n[系统] 女巫已使用药物")
        else:
            # 跳过
            self.game_state.record_witch_action(
                round_num=self.game_state.round_number,
                action_type="skip",
                target=None,
                remaining_antidote=witch_role.has_antidote,
                remaining_poison=witch_role.has_poison
            )

            if is_human_witch:
                print("\n你选择跳过。")
            else:
                # 系统提示（新增）
                print("\n[系统] 女巫未使用药物")

        await asyncio.sleep(0.5)

    async def handle_hunter_shoot(self, deaths: List[Player]):
        """处理猎人开枪"""
        from roles.base_role import RoleType

        # 检查死者中是否有猎人
        hunter = None
        was_poisoned = False

        for dead_player in deaths:
            if dead_player.role.role_type == RoleType.HUNTER:
                hunter = dead_player
                # 检查是否被毒死（被毒死不能开枪）
                was_poisoned = dead_player in self.game_state.poisoned_tonight
                break

        if not hunter or was_poisoned:
            if hunter and was_poisoned:
                print(f"\n{hunter.name} 是猎人，但因为被女巫毒死，无法发动技能。")
            return

        # 猎人可以开枪
        hunter_role = hunter.role

        if not hunter_role.can_shoot:
            print(f"\n{hunter.name} 是猎人，但已经开过枪，无法再次发动技能。")
            return

        # 判断是否是真人猎人
        human_player = self.get_human_player()
        is_human_hunter = (
            human_player and
            human_player.id == hunter.id
        )

        if is_human_hunter:
            CLI.print_section("🔫 猎人开枪")
            print(f"你是猎人，已经死亡，可以选择开枪带走一名玩家。")
        else:
            print(f"\n{hunter.name} 是猎人，可以开枪...")

        # 获取可选目标
        available_targets = self.game_state.alive_players.copy()

        if not available_targets:
            return

        # 猎人选择目标
        target = await hunter.choose_target(
            self.game_state,
            available_targets,
            "shoot"
        )

        if target:
            # 开枪带走目标
            print(f"\n{hunter.name} 开枪带走了 {target.name}！")

            target.is_alive = False
            self.game_state.alive_players.remove(target)
            self.game_state.dead_players.append(target)

            hunter_role.can_shoot = False

            # 记录猎人开枪到对话历史
            self.game_state.add_announcement(
                self.game_state.round_number,
                f"{hunter.name}（{hunter.id}号）发动猎人技能，开枪带走了{target.name}（{target.id}号）"
            )

            await asyncio.sleep(1)

            # 检查被枪杀的是否是警长，如果是可以传递警徽
            await self.handle_sheriff_death(target)
        else:
            print(f"\n{hunter.name} 选择不开枪。")

            # 记录猎人放弃开枪
            self.game_state.add_announcement(
                self.game_state.round_number,
                f"{hunter.name}（{hunter.id}号）放弃开枪"
            )

        # 检查死亡的猎人本身是否是警长，如果是可以传递警徽
        await self.handle_sheriff_death(hunter)

    async def handle_hunter_shoot_after_vote(self, exiled_player: Player):
        """处理被投票出去的猎人开枪"""
        from roles.base_role import RoleType

        # 检查被放逐的是否是猎人
        if exiled_player.role.role_type != RoleType.HUNTER:
            return

        hunter_role = exiled_player.role

        if not hunter_role.can_shoot:
            return

        # 判断是否是真人猎人
        human_player = self.get_human_player()
        is_human_hunter = (
            human_player and
            human_player.id == exiled_player.id
        )

        if is_human_hunter:
            CLI.print_section("🔫 猎人开枪")
            print(f"你是猎人，已被放逐，可以选择开枪带走一名玩家。")
        else:
            print(f"\n{exiled_player.name} 是猎人，可以开枪...")

        # 获取可选目标
        available_targets = self.game_state.alive_players.copy()

        if not available_targets:
            return

        # 猎人选择目标
        target = await exiled_player.choose_target(
            self.game_state,
            available_targets,
            "shoot"
        )

        if target:
            # 开枪带走目标
            print(f"\n{exiled_player.name} 开枪带走了 {target.name}！")

            target.is_alive = False
            self.game_state.alive_players.remove(target)
            self.game_state.dead_players.append(target)

            hunter_role.can_shoot = False

            # 记录猎人开枪到对话历史
            self.game_state.add_announcement(
                self.game_state.round_number,
                f"{exiled_player.name}（{exiled_player.id}号）发动猎人技能，开枪带走了{target.name}（{target.id}号）"
            )

            await asyncio.sleep(1)

            # 检查被枪杀的是否是警长，如果是可以传递警徽
            await self.handle_sheriff_death(target)
        else:
            print(f"\n{exiled_player.name} 选择不开枪。")

            # 记录猎人放弃开枪
            self.game_state.add_announcement(
                self.game_state.round_number,
                f"{exiled_player.name}（{exiled_player.id}号）放弃开枪"
            )

    async def day_phase(self):
        """白天阶段"""
        # 处理夜晚死亡
        deaths = self.game_state.process_night_deaths()

        CLI.print_header(f"第{self.game_state.round_number}轮 - 白天")

        self.game_state.current_phase = "day"

        # 宣布死讯
        death_message = await self.god_ai.announce_death(deaths)
        print(f"\n{death_message}\n")

        # 记录夜晚死亡到对话历史（让所有玩家都能看到）
        if deaths:
            death_names = "、".join([f"{d.name}（{d.id}号）" for d in deaths])
            self.game_state.add_announcement(
                self.game_state.round_number,
                f"昨晚死亡：{death_names}"
            )

            # 更新最后死者座位号（取最小座位号）
            death_seats = [d.seat_number for d in deaths]
            self.game_state.last_death_seat = min(death_seats)

            # 警长决定发言方向（只在有警长且警长存活时）
            sheriff = self.game_state.get_sheriff()
            if sheriff and sheriff.is_alive:
                direction = await sheriff.choose_speaking_direction(self.game_state)
                self.game_state.speaking_order_direction = direction

                direction_name = "死者右边（座位号增加方向）" if direction == "clockwise" else "死者左边（座位号减少方向）"
                print(f"\n警长 {sheriff.name} 决定从{direction_name}开始发言。\n")
        else:
            self.game_state.add_announcement(
                self.game_state.round_number,
                "昨晚平安夜，无人死亡"
            )

        await asyncio.sleep(1)

        # 处理夜晚死亡的警长传递警徽
        for dead in deaths:
            await self.handle_sheriff_death(dead)

        # 处理猎人开枪（如果猎人被刀死）
        await self.handle_hunter_shoot(deaths)

        await asyncio.sleep(1)

        # 发言阶段
        CLI.print_section("发言阶段")

        # 计算发言顺序
        speaking_order = self.game_state.calculate_speaking_order()

        for player in speaking_order:
            print(f"\n轮到 {player.name}（{player.id}号）发言...")

            speech = await player.make_speech(self.game_state)

            formatted_speech = Display.format_speech(player, speech)
            print(formatted_speech)

            self.game_state.add_speech(self.game_state.round_number, player, speech)

            await asyncio.sleep(0.5)

        # 第一轮发言后进行警长竞选
        if self.game_state.round_number == 1 and not self.game_state.sheriff_election_done:
            await asyncio.sleep(1)
            await self.sheriff_election_phase()

    async def handle_sheriff_death(self, dead_player: Player):
        """处理警长死亡和警徽传递"""
        if not dead_player.is_sheriff:
            return

        print(f"\n警长 {dead_player.name} 已死亡，可以传递警徽...")

        # 获取可选继承人
        candidates = [p for p in self.game_state.alive_players if p.id != dead_player.id]

        if not candidates:
            print("没有存活玩家可以继承警徽。")
            self.game_state.set_sheriff(None)
            return

        # 警长选择继承人
        successor = await dead_player.choose_sheriff_successor(self.game_state)

        if successor:
            print(f"\n{dead_player.name} 将警徽传递给 {successor.name}（{successor.id}号）")
            self.game_state.transfer_sheriff(dead_player.id, successor.id)

            self.game_state.add_announcement(
                self.game_state.round_number,
                f"{dead_player.name}（{dead_player.id}号）将警徽传递给{successor.name}（{successor.id}号）"
            )
        else:
            print(f"\n{dead_player.name} 选择撕毁警徽。")
            self.game_state.set_sheriff(None)

            self.game_state.add_announcement(
                self.game_state.round_number,
                f"{dead_player.name}（{dead_player.id}号）撕毁警徽"
            )

    async def sheriff_election_phase(self):
        """警长竞选阶段"""
        # 检查是否已竞选过
        if self.game_state.sheriff_election_done:
            return

        CLI.print_header("警长竞选")

        print("\n现在开始警长竞选！")
        print("警长权利：")
        print("  1. 投票时票数为1.5票")
        print("  2. 决定后续轮次的发言顺序（从死者左边或右边开始）")
        print("  3. 死亡时可以传递警徽或撕毁警徽\n")

        await asyncio.sleep(1)

        # 收集竞选意愿
        print("询问所有玩家是否竞选警长...\n")
        candidates = []

        for player in self.game_state.alive_players:
            will_run = await player.decide_sheriff_candidacy(self.game_state)

            if will_run:
                candidates.append(player)
                print(f"{player.name}（{player.id}号）宣布竞选警长")

            await asyncio.sleep(0.3)

        # 无人竞选
        if not candidates:
            print("\n无人竞选警长，本轮无警长。")
            self.game_state.sheriff_election_done = True
            return

        print(f"\n共有 {len(candidates)} 位候选人。\n")
        await asyncio.sleep(1)

        # 候选人发表竞选宣言
        CLI.print_section("竞选宣言")

        for candidate in candidates:
            speech = await candidate.make_sheriff_campaign_speech(self.game_state)
            print(f"\n{candidate.name}（{candidate.id}号）：{speech}")

            # 记录竞选宣言到对话历史
            self.game_state.add_speech(
                self.game_state.round_number,
                candidate,
                f"[竞选宣言] {speech}"
            )

            await asyncio.sleep(0.5)

        # 单候选人直接当选
        if len(candidates) == 1:
            winner = candidates[0]
            print(f"\n只有一位候选人，{winner.name}（{winner.id}号）自动当选警长！")

            self.game_state.set_sheriff(winner.id)
            self.game_state.sheriff_election_done = True

            # 记录到对话历史
            self.game_state.add_announcement(
                self.game_state.round_number,
                f"{winner.name}（{winner.id}号）当选警长"
            )

            return

        # 多候选人投票
        await self._conduct_sheriff_voting(candidates)

    async def _conduct_sheriff_voting(self, candidates: List[Player], is_pk_round: bool = False):
        """进行警长投票"""
        if is_pk_round:
            print("\n进入PK轮投票...\n")
        else:
            print("\n开始投票选举警长...\n")

        print("注意：候选人不参与投票\n")

        # 收集投票
        votes = {}  # {candidate_id: vote_count}

        for candidate in candidates:
            votes[candidate.id] = 0

        # 候选人不能投票，只有非候选人才能投票
        voters = [p for p in self.game_state.alive_players if p not in candidates]

        for player in voters:
            choice = await player.vote_for_sheriff(self.game_state, candidates)

            if choice and choice in candidates:
                votes[choice.id] += 1
                print(f"{player.name}（{player.id}号）投给 {choice.name}（{choice.id}号）")
            else:
                print(f"{player.name}（{player.id}号）弃票")

            await asyncio.sleep(0.3)

        # 统计结果
        print(f"\n投票结果：")
        for candidate in candidates:
            vote_count = votes.get(candidate.id, 0)
            print(f"  {candidate.name}（{candidate.id}号）：{vote_count}票")

        # 找出最高票
        max_votes = max(votes.values()) if votes else 0

        if max_votes == 0:
            print("\n所有人都弃票，本轮无警长。")
            self.game_state.sheriff_election_done = True
            return

        winners = [c for c in candidates if votes.get(c.id, 0) == max_votes]

        # 平票处理
        if len(winners) > 1:
            if is_pk_round:
                # PK轮仍平票，随机选择
                import random
                winner = random.choice(winners)
                print(f"\nPK轮仍然平票！随机选择 {winner.name}（{winner.id}号）当选警长。")
            else:
                # 首轮平票，进入PK
                print(f"\n平票！{', '.join([w.name for w in winners])} 进入PK环节。")
                await asyncio.sleep(1)

                # PK发言
                CLI.print_section("PK发言")

                for candidate in winners:
                    speech = await candidate.make_sheriff_campaign_speech(self.game_state)
                    print(f"\n{candidate.name}（{candidate.id}号）：{speech}")

                    await asyncio.sleep(0.5)

                # 重新投票
                await self._conduct_sheriff_voting(winners, is_pk_round=True)
                return
        else:
            winner = winners[0]
            print(f"\n{winner.name}（{winner.id}号）当选警长！")

        # 设置警长
        self.game_state.set_sheriff(winner.id)
        self.game_state.sheriff_election_done = True

        # 记录到对话历史
        self.game_state.add_announcement(
            self.game_state.round_number,
            f"{winner.name}（{winner.id}号）当选警长"
        )

    async def vote_phase(self):
        """投票阶段"""
        CLI.print_header(f"第{self.game_state.round_number}轮 - 投票")

        self.game_state.current_phase = "vote"
        self.game_state.reset_votes()

        print("开始投票...\n")

        # 获取警长
        sheriff = self.game_state.get_sheriff()
        sheriff_id = sheriff.id if sheriff and sheriff.is_alive else None

        # 使用权重字典收集投票
        vote_weights = {}  # {target_id: float}
        vote_details = []  # 记录投票明细 [(voter, target, weight), ...]

        # 收集投票
        for player in self.game_state.alive_players:
            target = await player.vote(self.game_state)

            if target:
                # 警长1.5票，普通玩家1票
                weight = 1.5 if player.id == sheriff_id else 1.0

                if target.id not in vote_weights:
                    vote_weights[target.id] = 0.0
                vote_weights[target.id] += weight

                # 记录投票明细
                vote_details.append((player, target, weight))

                self.game_state.add_vote(self.game_state.round_number, player, target)

                if player.id == sheriff_id:
                    print(f"{player.name}（警长，1.5票） 投票给 {target.name}")
                else:
                    print(f"{player.name} 投票给 {target.name}")
            else:
                vote_details.append((player, None, 0))
                print(f"{player.name} 弃票")

            await asyncio.sleep(0.3)

        # 统计结果
        if not vote_weights:
            print("\n所有人都弃票，无人被放逐。")
            return

        # 显示投票结果（保留1位小数）
        print(f"\n投票结果：")
        for player_id, votes in vote_weights.items():
            player = next(p for p in self.game_state.all_players if p.id == player_id)
            print(f"  {player.name}（{player.id}号）：{votes:.1f}票")

        # 显示投票明细
        print(f"\n投票明细：")
        for voter, target, weight in vote_details:
            if target:
                if weight == 1.5:
                    print(f"  {voter.name}（{voter.id}号，警长） → {target.name}（{target.id}号）")
                else:
                    print(f"  {voter.name}（{voter.id}号） → {target.name}（{target.id}号）")
            else:
                print(f"  {voter.name}（{voter.id}号） → 弃票")

        # 找出得票最高的（使用浮点权重）
        max_votes = max(vote_weights.values())
        candidates = [p for p in self.game_state.alive_players if vote_weights.get(p.id, 0) == max_votes]

        if len(candidates) > 1:
            print(f"\n平票！{', '.join([c.name for c in candidates])} 都获得{max_votes:.1f}票。")
            print("本轮无人被放逐。")
            return

        exiled = candidates[0]

        # 宣布结果
        vote_message = await self.god_ai.announce_vote_result(exiled, max_votes)
        print(f"\n{vote_message}")

        # 放逐玩家
        exiled.is_alive = False
        self.game_state.alive_players.remove(exiled)
        self.game_state.dead_players.append(exiled)
        self.game_state.today_voted_out = exiled

        # 暗牌模式：不公开身份
        print(f"\n{exiled.name} 已被放逐。")

        # 记录投票结果到对话历史（让所有玩家都能看到）
        self.game_state.add_announcement(
            self.game_state.round_number,
            f"{exiled.name}（{exiled.id}号）被投票放逐，获得{max_votes:.1f}票"
        )

        await asyncio.sleep(1)

        # 检查被放逐的是否是猎人，如果是可以开枪
        await self.handle_hunter_shoot_after_vote(exiled)

        # 检查被放逐的是否是警长，如果是可以传递警徽
        await self.handle_sheriff_death(exiled)

    def show_round_info(self):
        """显示当前轮次的简要信息"""
        werewolves = self.game_state.get_alive_werewolves()
        good_guys = [p for p in self.game_state.alive_players
                     if p.role.camp == RoleCamp.VILLAGER]

        print(f"\n【第{self.game_state.round_number}轮】 存活：{len(werewolves)}狼 vs {len(good_guys)}好人")
        if self.game_state.sheriff_player_id:
            sheriff = next((p for p in self.game_state.all_players if p.id == self.game_state.sheriff_player_id), None)
            if sheriff:
                print(f"当前警长：{sheriff.name}（{sheriff.id}号）")

    async def save_game_log(self, winner: str):
        """
        保存游戏日志到JSON文件

        Args:
            winner: 获胜阵营
        """
        import json
        from datetime import datetime
        import os

        # 创建存储目录
        storage_dir = "storage/game_logs"
        os.makedirs(storage_dir, exist_ok=True)

        # 生成文件名（时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{storage_dir}/game_{timestamp}.json"

        # 构建游戏日志数据
        game_log = {
            "game_info": {
                "end_time": datetime.now().isoformat(),
                "winner": winner,
                "total_rounds": self.game_state.round_number,
                "board_config": self.game_state.board_config,
                "total_players": len(self.game_state.all_players),
                "alive_count": len(self.game_state.alive_players),
                "dead_count": len(self.game_state.dead_players)
            },
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "role": p.role.role_type.value,
                    "camp": p.role.camp.value,
                    "is_alive": p.is_alive,
                    "is_sheriff": (p.id == self.game_state.sheriff_player_id)
                }
                for p in self.game_state.all_players
            ],
            "conversation_history": self.game_state.conversation_history,
            "witch_actions": self.game_state.witch_action_history,
            "seer_checks": {
                str(player_id): results
                for player_id, results in self.game_state.seer_check_results.items()
            },
            "victory_reason": self.game_state.get_victory_reason(winner)
        }

        # 保存到文件
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(game_log, f, ensure_ascii=False, indent=2)
            print(f"\n✓ 游戏日志已保存：{filename}")
        except Exception as e:
            print(f"\n✗ 保存游戏日志失败：{e}")

    async def end_game(self, winner: str):
        """游戏结束，显示详细总结"""

        print(f"\n[DEBUG] 游戏实例 ID: {self.instance_id} 结束")
        print("\n" + "=" * 50)
        print("  游戏结束")
        print("=" * 50)

        # 显示胜利方
        print(f"\n🎉 {winner} 获得胜利！\n")

        # 显示详细的胜利原因
        victory_reason = self.game_state.get_victory_reason(winner)
        print(victory_reason)

        # 显示游戏统计
        print("\n【游戏统计】")
        print(f"游戏轮数：{self.game_state.round_number}轮")
        print(f"总玩家数：{len(self.game_state.all_players)}人")
        print(f"存活人数：{len(self.game_state.alive_players)}人")
        print(f"死亡人数：{len(self.game_state.dead_players)}人")

        # 显示玩家身份揭晓
        print("\n【玩家身份揭晓】")
        from roles.base_role import RoleCamp
        for player in self.game_state.all_players:
            status = "✓存活" if player.is_alive else "✗死亡"
            camp_emoji = "🐺" if player.role.camp == RoleCamp.WEREWOLF else "👤"
            print(f"{player.id}号 {player.name} [{status}] - {camp_emoji} {player.role.role_type.value}")

        # 保存游戏日志（新增）
        await self.save_game_log(winner)

        print("\n" + "=" * 50)


async def main():
    """主函数"""
    try:
        # 验证配置
        settings.validate()

        # 创建游戏
        game = WolfkillGame()

        # 设置游戏
        await game.setup_game()

        # 运行游戏
        await game.run_game()

    except KeyboardInterrupt:
        print("\n\n游戏被中断。")
    except Exception as e:
        print(f"\n游戏出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*15 + "狼人杀游戏 v1.0")
    print(" "*10 + "Powered by DeepSeek AI")
    print("="*60 + "\n")

    asyncio.run(main())
