"""
显示格式化工具
"""
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from players.player import Player


class Display:
    """显示格式化工具类"""

    @staticmethod
    def format_player_list(players: List['Player'], show_role: bool = False) -> str:
        """
        格式化玩家列表

        Args:
            players: 玩家列表
            show_role: 是否显示角色

        Returns:
            str: 格式化后的字符串
        """
        lines = []
        for player in players:
            status = "✓存活" if player.is_alive else "✗死亡"
            role_info = f" - {player.role.role_type.value}" if show_role else ""
            lines.append(f"{player.id}号 {player.name} [{status}]{role_info}")

        return "\n".join(lines)

    @staticmethod
    def format_round_info(round_num: int, phase: str) -> str:
        """
        格式化回合信息

        Args:
            round_num: 回合数
            phase: 阶段名称

        Returns:
            str: 格式化后的字符串
        """
        return f"第{round_num}轮 - {phase}"

    @staticmethod
    def format_speech(player: 'Player', content: str) -> str:
        """
        格式化发言

        Args:
            player: 发言玩家
            content: 发言内容

        Returns:
            str: 格式化后的字符串
        """
        return f"【{player.name}（{player.id}号）】: {content}"

    @staticmethod
    def format_vote_result(votes_dict: dict) -> str:
        """
        格式化投票结果

        Args:
            votes_dict: 投票字典 {player: votes_count}

        Returns:
            str: 格式化后的字符串
        """
        lines = ["投票结果："]
        sorted_players = sorted(votes_dict.items(), key=lambda x: x[1], reverse=True)

        for player, votes in sorted_players:
            lines.append(f"  {player.name}（{player.id}号）: {votes}票")

        return "\n".join(lines)
