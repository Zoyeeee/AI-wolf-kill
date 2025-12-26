"""
CLI命令行交互界面
"""
import asyncio
from typing import Optional


class CLI:
    """命令行交互工具类"""

    @staticmethod
    def clear_input_buffer():
        """清空标准输入缓冲区,丢弃所有待处理的输入"""
        import sys
        import platform

        # 跨平台实现
        try:
            if platform.system() == 'Windows':
                # Windows 系统
                import msvcrt
                while msvcrt.kbhit():
                    msvcrt.getch()
            else:
                # Unix/Linux/MacOS 系统 - 使用简化的实现
                import termios

                # 直接刷新输入缓冲区
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            # 如果清空失败,静默忽略(不影响正常游戏)
            pass

    @staticmethod
    async def get_input(prompt: str, allow_empty: bool = False) -> str:
        """
        获取用户输入

        Args:
            prompt: 提示信息
            allow_empty: 是否允许空输入

        Returns:
            str: 用户输入
        """
        loop = asyncio.get_event_loop()
        while True:
            try:
                user_input = await loop.run_in_executor(None, input, prompt)
                user_input = user_input.strip()

                if user_input or allow_empty:
                    return user_input

                print("输入不能为空，请重新输入。")
            except EOFError:
                print("\n检测到输入流关闭（EOF），游戏将退出。")
                raise SystemExit(0)
            except KeyboardInterrupt:
                print("\n检测到用户中断（Ctrl+C），游戏将退出。")
                raise SystemExit(0)

    @staticmethod
    async def get_number_input(
        prompt: str,
        min_val: int = 1,
        max_val: int = 100
    ) -> int:
        """
        获取数字输入

        Args:
            prompt: 提示信息
            min_val: 最小值
            max_val: 最大值

        Returns:
            int: 用户输入的数字
        """
        loop = asyncio.get_event_loop()
        while True:
            try:
                user_input = await loop.run_in_executor(None, input, prompt)
                number = int(user_input.strip())

                if min_val <= number <= max_val:
                    return number

                print(f"请输入{min_val}到{max_val}之间的数字。")
            except EOFError:
                print("\n检测到输入流关闭（EOF），游戏将退出。")
                raise SystemExit(0)
            except KeyboardInterrupt:
                print("\n检测到用户中断（Ctrl+C），游戏将退出。")
                raise SystemExit(0)
            except ValueError:
                print("输入无效，请输入数字。")

    @staticmethod
    def print_header(text: str):
        """打印标题"""
        print(f"\n{'='*50}")
        print(f"  {text}")
        print(f"{'='*50}\n")

    @staticmethod
    def print_section(title: str):
        """打印章节标题"""
        print(f"\n--- {title} ---\n")

    @staticmethod
    def print_message(message: str):
        """打印普通消息"""
        print(message)

    @staticmethod
    def print_error(message: str):
        """打印错误消息"""
        print(f"❌ 错误: {message}")

    @staticmethod
    def print_success(message: str):
        """打印成功消息"""
        print(f"✅ {message}")
