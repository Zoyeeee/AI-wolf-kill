"""
真人玩家实现
"""
from typing import Optional, List, Tuple, TYPE_CHECKING
from players.player import Player

if TYPE_CHECKING:
    from roles.base_role import BaseRole
    from core.game_state import GameState


class HumanPlayer(Player):
    """
    真人玩家

    通过CLI获取输入
    """

    def __init__(self, player_id: int, name: str, role: 'BaseRole'):
        super().__init__(player_id, name, role)

    async def make_speech(self, game_state: 'GameState') -> str:
        """真人玩家发言 - 通过CLI输入"""
        from ui.cli import CLI

        print(f"\n【轮到你发言了】")
        print(f"你是 {self.name}（{self.id}号），角色：{self.role.role_type.value}")

        speech = await CLI.get_input(
            f"请输入你的发言（直接回车跳过）: ",
            allow_empty=True
        )

        if not speech:
            speech = "我没什么要说的。"

        self.add_speech(speech)
        return speech

    async def vote(self, game_state: 'GameState') -> Optional['Player']:
        """真人玩家投票 - 通过CLI选择"""
        from ui.cli import CLI

        print(f"\n【投票阶段】")
        print(f"请选择你要投票放逐的玩家：")

        # 显示可选玩家
        alive_players = [p for p in game_state.alive_players if p.id != self.id]
        for i, player in enumerate(alive_players, 1):
            print(f"{i}. {player.name}（{player.id}号）")
        print(f"{len(alive_players) + 1}. 弃票")

        choice = await CLI.get_number_input(
            f"请输入序号（1-{len(alive_players) + 1}）: ",
            min_val=1,
            max_val=len(alive_players) + 1
        )

        if choice == len(alive_players) + 1:
            return None

        return alive_players[choice - 1]

    async def choose_target(
        self,
        game_state: 'GameState',
        available_targets: List['Player'],
        action_type: str
    ) -> Optional['Player']:
        """真人玩家选择目标"""
        from ui.cli import CLI

        action_names = {
            "kill": "杀死",
            "check": "查验",
            "poison": "毒死",
            "shoot": "射击"
        }

        action_name = action_names.get(action_type, action_type)

        print(f"\n【{action_name}目标选择】")
        print(f"请选择{action_name}的目标：")

        for i, target in enumerate(available_targets, 1):
            print(f"{i}. {target.name}（{target.id}号）")
        print(f"{len(available_targets) + 1}. 跳过")

        choice = await CLI.get_number_input(
            f"请输入序号（1-{len(available_targets) + 1}）: ",
            min_val=1,
            max_val=len(available_targets) + 1
        )

        if choice == len(available_targets) + 1:
            return None

        return available_targets[choice - 1]

    async def make_werewolf_discussion(
        self,
        game_state: 'GameState',
        round_idx: int
    ) -> str:
        """真人狼人在狼人频道发言"""
        from ui.cli import CLI

        print(f"\n【轮到你在狼人频道发言】（第{round_idx}轮）")

        # 显示当前狼人私聊历史
        private_history = game_state.get_private_conversation_history("werewolf")
        if private_history != "暂无私聊记录":
            print(f"\n之前的讨论：\n{private_history}\n")

        speech = await CLI.get_input(
            f"请输入你的发言（讨论杀人目标）: ",
            allow_empty=True
        )

        if not speech:
            speech = "我没意见，听大家的。"

        return speech

    async def choose_witch_action(
        self,
        game_state: 'GameState',
        witch_role: 'BaseRole'
    ) -> Optional[Tuple[str, 'Player']]:
        """女巫选择行动"""
        from ui.cli import CLI

        print(f"\n【女巫行动】")
        print(f"⚠️  规则：每晚只能使用一种药（解药或毒药），不能同时使用")
        print(f"剩余药水：{witch_role.get_remaining_potions()}\n")

        options = ["跳过"]
        option_idx = 1

        # 检查是否可以救人
        if witch_role.has_antidote and game_state.tonight_victim:
            victim = game_state.tonight_victim
            print(f"今晚的受害者是：{victim.name}（{victim.id}号）")
            options.append(f"使用解药救 {victim.name}")
            option_idx += 1

        # 检查是否可以毒人
        poison_idx = None
        if witch_role.has_poison:
            options.append("使用毒药")
            poison_idx = len(options)  # 修复: 使用当前options长度作为索引

        print(f"\n可用行动（只能选择一个）：")
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")

        choice = await CLI.get_number_input(
            f"请选择行动（1-{len(options)}）: ",
            min_val=1,
            max_val=len(options)
        )

        if choice == 1:  # 跳过
            return None

        if witch_role.has_antidote and choice == 2:  # 救人
            return ("save", game_state.tonight_victim)

        if witch_role.has_poison and choice == poison_idx:  # 毒人
            # 选择毒人目标
            alive_players = [p for p in game_state.alive_players if p.id != self.id]
            print(f"\n选择毒人目标：")
            for i, player in enumerate(alive_players, 1):
                print(f"{i}. {player.name}（{player.id}号）")

            target_choice = await CLI.get_number_input(
                f"请输入序号（1-{len(alive_players)}）: ",
                min_val=1,
                max_val=len(alive_players)
            )

            return ("poison", alive_players[target_choice - 1])

        return None

    async def decide_sheriff_candidacy(self, game_state: 'GameState') -> bool:
        """真人决定是否竞选警长"""
        from ui.cli import CLI

        print(f"\n【警长竞选】")
        print(f"你是 {self.name}（{self.id}号），角色：{self.role.role_type.value}")

        choice = await CLI.get_input("是否竞选警长？(y/n): ", allow_empty=False)
        return choice.lower() in ['y', 'yes', '是']

    async def make_sheriff_campaign_speech(self, game_state: 'GameState') -> str:
        """真人竞选宣言"""
        from ui.cli import CLI

        print(f"\n【竞选宣言】")
        speech = await CLI.get_input("请发表你的竞选宣言: ", allow_empty=True)

        if not speech:
            speech = "我希望成为警长，带领大家找出狼人。"

        return speech

    async def vote_for_sheriff(
        self,
        game_state: 'GameState',
        candidates: List['Player']
    ) -> Optional['Player']:
        """真人投票选举警长"""
        from ui.cli import CLI

        print(f"\n【警长选举投票】")
        print("候选人：")
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. {candidate.name}（{candidate.id}号）")
        print(f"{len(candidates) + 1}. 弃票")

        choice = await CLI.get_number_input(
            f"请选择（1-{len(candidates) + 1}）: ",
            min_val=1,
            max_val=len(candidates) + 1
        )

        if choice == len(candidates) + 1:
            return None

        return candidates[choice - 1]

    async def choose_speaking_direction(self, game_state: 'GameState') -> str:
        """真人警长选择发言方向"""
        from ui.cli import CLI

        print(f"\n【警长决定发言顺序】")
        print("1. 从死者右边开始（座位号增加方向）")
        print("2. 从死者左边开始（座位号减少方向）")

        choice = await CLI.get_number_input("请选择（1-2）: ", min_val=1, max_val=2)

        return "clockwise" if choice == 1 else "counterclockwise"

    async def choose_sheriff_successor(
        self,
        game_state: 'GameState'
    ) -> Optional['Player']:
        """真人警长选择继承人"""
        from ui.cli import CLI

        print(f"\n【警徽传递】")
        print("请选择警徽继承人：")

        candidates = [p for p in game_state.alive_players if p.id != self.id]
        for i, player in enumerate(candidates, 1):
            print(f"{i}. {player.name}（{player.id}号）")
        print(f"{len(candidates) + 1}. 撕毁警徽")

        choice = await CLI.get_number_input(
            f"请选择（1-{len(candidates) + 1}）: ",
            min_val=1,
            max_val=len(candidates) + 1
        )

        if choice == len(candidates) + 1:
            return None

        return candidates[choice - 1]
