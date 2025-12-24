"""
自定义异常类
"""

class WolfkillException(Exception):
    """狼人杀游戏基础异常"""
    pass


class GameNotStartedException(WolfkillException):
    """游戏未开始异常"""
    pass


class InvalidActionException(WolfkillException):
    """无效行动异常"""
    pass


class PlayerNotFoundException(WolfkillException):
    """玩家未找到异常"""
    pass


class ConfigurationException(WolfkillException):
    """配置错误异常"""
    pass
