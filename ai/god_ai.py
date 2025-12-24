"""
主持人AI - 游戏旁白和氛围营造
"""
from typing import List, TYPE_CHECKING
from ai.llm_client import llm_client
from ai.prompts import god_prompts

if TYPE_CHECKING:
    from players.player import Player


class GodAI:
    """
    主持人AI（上帝）

    职责：
    - 宣布游戏进展
    - 营造游戏氛围
    - 引导游戏流程
    """

    def __init__(self):
        self.llm = llm_client

    async def announce_night_start(self, round_num: int) -> str:
        """
        宣布夜晚开始

        Args:
            round_num: 回合数

        Returns:
            str: 宣布内容
        """
        prompt = god_prompts.NIGHT_START.format(round=round_num)
        message = await self.llm.generate(prompt)

        if not message:
            message = f"第{round_num}个夜晚开始了，天黑请闭眼..."

        return message

    async def announce_day_start(self, round_num: int, night_summary: str = "") -> str:
        """
        宣布白天开始

        Args:
            round_num: 回合数
            night_summary: 昨晚发生的事情总结

        Returns:
            str: 宣布内容
        """
        prompt = god_prompts.DAY_START.format(
            round=round_num,
            night_summary=night_summary or "一切看似平静"
        )
        message = await self.llm.generate(prompt)

        if not message:
            message = f"第{round_num}个白天到来了。"

        return message

    async def announce_death(self, victims: List['Player']) -> str:
        """
        宣布死亡消息

        Args:
            victims: 死亡的玩家列表

        Returns:
            str: 宣布内容
        """
        if not victims:
            return "昨晚是平安夜，没有人死亡。"

        victim_names = "、".join([f"{v.name}（{v.id}号）" for v in victims])
        prompt = god_prompts.ANNOUNCE_DEATH.format(
            victims=victim_names,
            victim_name=victims[0].name if len(victims) == 1 else victim_names
        )
        message = await self.llm.generate(prompt)

        if not message:
            message = f"昨晚，{victim_names} 死了。"

        return message

    async def announce_vote_result(self, exiled: 'Player', votes: int) -> str:
        """
        宣布投票结果

        Args:
            exiled: 被放逐的玩家
            votes: 得票数

        Returns:
            str: 宣布内容
        """
        prompt = god_prompts.ANNOUNCE_VOTE_RESULT.format(
            exiled_name=f"{exiled.name}（{exiled.id}号）",
            votes=votes
        )
        message = await self.llm.generate(prompt)

        if not message:
            message = f"{exiled.name}被投票放逐了。"

        return message

    async def announce_victory(self, winning_camp: str, rounds: int) -> str:
        """
        宣布游戏结束和获胜方

        Args:
            winning_camp: 获胜阵营
            rounds: 游戏轮数

        Returns:
            str: 宣布内容
        """
        prompt = god_prompts.ANNOUNCE_VICTORY.format(
            winning_camp=winning_camp,
            rounds=rounds
        )
        message = await self.llm.generate(prompt)

        if not message:
            message = f"游戏结束！{winning_camp}获胜！"

        return message

    async def narrate(self, message: str) -> str:
        """
        通用旁白

        Args:
            message: 原始消息

        Returns:
            str: 渲染后的消息
        """
        # 可以用AI润色，这里简化处理
        return message
