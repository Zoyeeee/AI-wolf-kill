"""
角色工厂 - 创建和分配角色
"""
import random
from typing import List, Dict
from roles.base_role import BaseRole
from roles.werewolf import Werewolf
from roles.villager import Villager
from roles.seer import Seer
from roles.witch import Witch
from roles.hunter import Hunter
from config.game_config import GameConfig


class RoleFactory:
    """
    角色工厂类

    职责：
    1. 根据配置创建角色实例
    2. 随机分配角色
    3. 验证角色配置的合理性
    """

    # 角色类映射
    ROLE_MAP = {
        "werewolf": Werewolf,
        "villager": Villager,
        "seer": Seer,
        "witch": Witch,
        "hunter": Hunter,
    }

    @staticmethod
    def create_role(role_name: str) -> BaseRole:
        """
        创建单个角色实例

        Args:
            role_name: 角色名称（如 "werewolf", "seer"）

        Returns:
            BaseRole: 角色实例

        Raises:
            ValueError: 如果角色名称不存在
        """
        role_class = RoleFactory.ROLE_MAP.get(role_name)
        if not role_class:
            raise ValueError(f"Unknown role: {role_name}")
        return role_class()

    @staticmethod
    def create_roles_by_config(config_name: str) -> List[BaseRole]:
        """
        根据配置创建所有角色

        Args:
            config_name: 配置名称（如 "basic", "standard"）

        Returns:
            List[BaseRole]: 角色列表

        Example:
            >>> roles = RoleFactory.create_roles_by_config("basic")
            >>> len(roles)
            9
        """
        # 获取角色配置
        composition = GameConfig.get_role_composition(config_name)

        roles = []
        for role_name, count in composition.items():
            for _ in range(count):
                roles.append(RoleFactory.create_role(role_name))

        return roles

    @staticmethod
    def distribute_roles(
        config_name: str,
        shuffle: bool = True
    ) -> List[BaseRole]:
        """
        创建并分配角色

        Args:
            config_name: 配置名称
            shuffle: 是否随机打乱角色顺序

        Returns:
            List[BaseRole]: 已打乱的角色列表

        Example:
            >>> roles = RoleFactory.distribute_roles("basic")
            >>> roles[0]  # 第一个玩家的角色
            <Werewolf: 狼人>
        """
        roles = RoleFactory.create_roles_by_config(config_name)

        if shuffle:
            random.shuffle(roles)

        return roles

    @staticmethod
    def validate_composition(composition: Dict[str, int]) -> bool:
        """
        验证角色配置是否合理

        Args:
            composition: 角色组成字典

        Returns:
            bool: True表示配置合理

        验证规则：
        1. 狼人数量 < 好人数量
        2. 至少有1个狼人
        3. 至少有1个好人
        """
        werewolf_count = composition.get("werewolf", 0)
        villager_count = sum(
            count for role, count in composition.items()
            if role != "werewolf"
        )

        # 检查基本条件
        if werewolf_count == 0:
            return False
        if villager_count == 0:
            return False

        # 狼人数量不能过多
        if werewolf_count >= villager_count:
            return False

        return True

    @staticmethod
    def get_role_summary(roles: List[BaseRole]) -> Dict[str, int]:
        """
        获取角色分布摘要

        Args:
            roles: 角色列表

        Returns:
            Dict[str, int]: 角色名称到数量的映射

        Example:
            >>> roles = RoleFactory.distribute_roles("basic")
            >>> RoleFactory.get_role_summary(roles)
            {'狼人': 3, '村民': 3, '预言家': 1, '女巫': 1, '猎人': 1}
        """
        summary = {}
        for role in roles:
            role_name = role.role_type.value
            summary[role_name] = summary.get(role_name, 0) + 1
        return summary

    @staticmethod
    def get_camp_summary(roles: List[BaseRole]) -> Dict[str, int]:
        """
        获取阵营分布摘要

        Args:
            roles: 角色列表

        Returns:
            Dict[str, int]: 阵营名称到数量的映射

        Example:
            >>> roles = RoleFactory.distribute_roles("basic")
            >>> RoleFactory.get_camp_summary(roles)
            {'狼人阵营': 3, '好人阵营': 6}
        """
        summary = {}
        for role in roles:
            camp_name = role.camp.value
            summary[camp_name] = summary.get(camp_name, 0) + 1
        return summary
