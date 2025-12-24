# 狼人杀游戏 (Wolfkill Game)

基于Python和DeepSeek AI的命令行狼人杀游戏，支持单人vs AI模式。

## 项目状态

### ✅ 已完成模块

#### Phase 1: 基础设施
- ✅ 项目目录结构
- ✅ 配置管理 (`config/settings.py`, `config/game_config.py`)
- ✅ 环境变量配置 (`.env.example`)
- ✅ 依赖管理 (`requirements.txt`)

#### Phase 2: 角色系统（策略模式）
- ✅ 角色基类 (`roles/base_role.py`) - 策略模式核心
- ✅ 狼人 (`roles/werewolf.py`)
- ✅ 村民 (`roles/villager.py`)
- ✅ 预言家 (`roles/seer.py`)
- ✅ 女巫 (`roles/witch.py`)
- ✅ 猎人 (`roles/hunter.py`)
- ✅ 角色工厂 (`roles/role_factory.py`)

#### Phase 8: 行动系统
- ✅ 行动基类 (`actions/base_action.py`)
- ✅ 杀人行动 (`actions/kill_action.py`)
- ✅ 查验行动 (`actions/check_action.py`)
- ✅ 救人行动 (`actions/save_action.py`)
- ✅ 毒人行动 (`actions/poison_action.py`)
- ✅ 射击行动 (`actions/shoot_action.py`)
- ✅ 投票行动 (`actions/vote_action.py`)

### 🚧 待实现模块

#### Phase 3: 玩家系统
- ⏳ 玩家基类 (`players/player.py`)
- ⏳ 真人玩家 (`players/human_player.py`)
- ⏳ AI玩家 (`players/ai_player.py`)

#### Phase 4: AI模块
- ⏳ LLM客户端 (`ai/llm_client.py`)
- ⏳ 主持人AI (`ai/god_ai.py`)
- ⏳ 玩家AI (`ai/player_ai.py`)
- ⏳ 提示词模板 (`ai/prompts/`)

#### Phase 5: 存储层
- ⏳ Redis客户端 (`storage/redis_client.py`)
- ⏳ 游戏仓库 (`storage/game_repository.py`)

#### Phase 6: 游戏核心逻辑
- ⏳ 游戏状态 (`core/game_state.py`)
- ⏳ 游戏引擎 (`core/game_engine.py`)
- ⏳ 游戏流程 (`core/game_flow.py`)

#### Phase 7: 阶段系统
- ⏳ 阶段基类 (`phases/base_phase.py`)
- ⏳ 夜晚阶段 (`phases/night_phase.py`)
- ⏳ 白天阶段 (`phases/day_phase.py`)
- ⏳ 投票阶段 (`phases/vote_phase.py`)
- ⏳ 阶段管理器 (`phases/phase_manager.py`)

#### Phase 9: UI界面
- ⏳ CLI交互 (`ui/cli.py`)
- ⏳ 格式化显示 (`ui/display.py`)

#### Phase 10: 程序入口
- ⏳ 主程序 (`main.py`)

## 技术栈

- **语言**: Python 3.9+
- **AI模型**: DeepSeek (via LangChain OpenAI)
- **存储**: Redis (TTL: 24小时)
- **界面**: 命令行 (CLI)
- **架构**: 策略模式（角色扩展）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_actual_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Redis配置
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
REDIS_EXPIRE_TIME=86400
```

### 3. 运行游戏

```bash
python main.py
```

## 架构设计

### 策略模式（角色系统）

所有角色继承 `BaseRole` 基类，实现统一接口：

```python
class BaseRole(ABC):
    @abstractmethod
    def get_role_description(self) -> str:
        pass

    @abstractmethod
    async def perform_night_action(self, player, game_state):
        pass
```

**优势**：
- ✅ 易于扩展新角色
- ✅ 统一的调用接口
- ✅ 灵活配置

### 命令模式（行动系统）

所有行动继承 `BaseAction` 基类：

```python
class BaseAction(ABC):
    @abstractmethod
    async def execute(self, game_state) -> dict:
        pass

    @abstractmethod
    def can_execute(self, game_state) -> bool:
        pass
```

**优势**：
- ✅ 便于记录历史
- ✅ 可撤销操作
- ✅ 统一执行流程

### AI设计原则

1. **完整历史对话记录**：AI能看到所有玩家的历史发言
2. **自我认知**：AI知道自己说过的话，保持逻辑一致性
3. **阵营策略**：根据角色和阵营调整决策策略

## 添加新角色示例

```python
# roles/cupid.py
from roles.base_role import BaseRole, RoleType, RoleCamp

class Cupid(BaseRole):
    def __init__(self):
        super().__init__()
        self.role_type = RoleType.CUPID
        self.camp = RoleCamp.VILLAGER
        self.has_night_action = True
        self.action_priority = 0  # 第一晚最先行动

    def get_role_description(self) -> str:
        return "你是丘比特，可以在第一晚选择两名玩家成为情侣。"

    async def perform_night_action(self, player, game_state):
        # 实现逻辑...
        pass
```

然后在 `role_factory.py` 中注册：

```python
ROLE_MAP = {
    ...
    "cupid": Cupid,
}
```

## 继续开发指南

### 优先级 1: 完成核心流程

1. **玩家系统** (`players/`):
   - 实现玩家基类和真人/AI玩家
   - 关键方法：`make_speech()`, `vote()`, `choose_target()`

2. **AI模块** (`ai/`):
   - 实现LLM客户端（调用DeepSeek）
   - 实现玩家AI（生成发言、投票决策）
   - **重点**：提示词包含完整历史对话

3. **游戏状态** (`core/game_state.py`):
   - 管理存活/死亡玩家
   - **重点**：记录完整对话历史
   - 实现查询接口：`get_full_conversation_history()`

### 优先级 2: 完成游戏流程

4. **游戏引擎** (`core/game_engine.py`):
   - 初始化游戏
   - 分配角色
   - 启动主循环

5. **阶段系统** (`phases/`):
   - 实现夜晚、白天、投票阶段
   - 按优先级执行角色行动

### 优先级 3: 完善用户体验

6. **UI界面** (`ui/`):
   - CLI交互
   - 彩色输出
   - 格式化显示

7. **存储层** (`storage/`):
   - Redis客户端
   - 游戏数据持久化

## 关键实现要点

### 1. 历史对话记录

```python
# core/game_state.py
class GameState:
    def __init__(self):
        self.conversation_history = []

    def add_speech(self, round_num, player, content):
        self.conversation_history.append({
            "round": round_num,
            "phase": "day",
            "player_id": player.id,
            "content": content,
        })

    def get_full_conversation_history(self) -> str:
        # 返回格式化的对话历史
        pass
```

### 2. AI提示词模板

```python
# ai/prompts/player_prompts.py
WEREWOLF_SPEECH_PROMPT = """
你是玩家{player_name}（{player_id}号），角色是狼人。

【完整历史对话记录】
{full_conversation_history}

【你的历史发言总结】
{your_previous_speeches}
# 注意保持前后一致！

请生成发言（50-100字）。
"""
```

### 3. Redis数据结构

```python
# 键命名
game:{game_id}:info       # 游戏信息
game:{game_id}:players    # 玩家信息
game:{game_id}:state      # 游戏状态
game:{game_id}:history:{round}  # 历史记录

# 所有键自动过期（REDIS_EXPIRE_TIME）
```

## 测试

```bash
# 运行测试
pytest tests/

# 测试特定模块
pytest tests/test_roles/
```

## 文档参考

详细的实施计划见：`~/.claude/plans/lazy-squishing-stream.md`

## 贡献指南

1. 遵循策略模式添加新角色
2. 所有行动继承 `BaseAction`
3. 保持代码风格一致
4. 添加单元测试

## 许可证

MIT License
