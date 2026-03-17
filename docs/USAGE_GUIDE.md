# DA-Agent 使用指南

## 方法 1: Python CLI（推荐，最简单）

### 基本用法

```bash
cd ~/da-agent
python cli.py analyze
```

### 交互式流程

CLI 会引导你完成 8 个步骤：

1. **业务问题** - 输入你想回答的问题
2. **数据源** - 指定数据文件位置
3. **分析类型** - 选择分析方法（Top N / 分组聚合）
4. **复杂度评分** - 自动评估任务复杂度
5. **代码生成** - 自动生成 Python 代码
6. **用户审批** - 查看代码并确认执行
7. **执行** - 运行分析代码
8. **知识库** - 保存任务记录

### 示例

```bash
$ python cli.py analyze

🎯 DA-Agent: Data Analysis Session
============================================================

📊 Step 1: Business Question
------------------------------------------------------------

What business question are you trying to answer?
> Which users generate the most revenue?

✓ Question: Which users generate the most revenue?

📁 Step 2: Data Source
------------------------------------------------------------

Where is your data file? (e.g., users.csv)
> test_users.csv

✓ File validated: /Users/niupian/da-agent/test_users.csv

🔍 Step 3: Analysis Type
------------------------------------------------------------

Choose analysis type:
1) Top N records by column
2) Group by and aggregate

Your choice (1-2): 1
Sort by which column? revenue
How many top records? (default: 10) 5

📈 Step 4: Complexity Scoring
------------------------------------------------------------

  Score: 2/10
  Mode: AUTO
  Reasoning: Simple single-table aggregation

💻 Step 5: Code Generation
------------------------------------------------------------

✓ Generated 523 characters of code

...

✅ Step 6: Execution
------------------------------------------------------------

Execute this code? (y/n): y

⚙️  Executing...

============================================================
📊 RESULTS
============================================================
 user_id    name signup_date     channel  revenue
      5     Eve  2026-01-19 paid_search      420
     10    Jack  2026-01-24     organic      400
      8   Henry  2026-01-22 paid_search      350
      3 Charlie  2026-01-17      social      320
      7   Grace  2026-01-21     organic      280
```

---

## 方法 2: Claude Code Integration

### 前提条件

- Claude Code v2.1.77+
- DA-Agent 插件已安装（运行 `./install-local.sh`）
- **已重启 Claude Code**

### 使用 Skill Tool

Claude Code 不支持 `/da:analyze` 这样的斜杠命令。正确的做法是通过 **Skill tool** 调用：

#### 在对话中请求

直接告诉 Claude 你想分析数据，它会自动调用相关技能：

```
用户: "我想分析一下 test_users.csv，找出收入最高的 10 个用户"

Claude 会自动:
1. 识别这是数据分析任务
2. 调用 da-agent:analyze-request skill
3. 引导你完成结构化对话
4. 自动执行分析流程
```

#### 技能工作流程

DA-Agent 提供两个核心技能：

1. **`analyze-request`** - 理解分析请求
   - 结构化对话收集需求
   - 复杂度评分和路由
   - 用户确认
   - 知识库记录

2. **`execute-auto`** - 自动执行（简单任务）
   - 代码生成
   - 安全验证
   - 执行输出
   - 结果展示

### 为什么找不到 `/da:analyze` 命令？

**Claude Code v2.1.77+ 架构变化：**

- ❌ **旧方式**: 斜杠命令 `/da:analyze`（已弃用）
- ✅ **新方式**: Skills 通过 Skill tool 调用

**背景：**
- 斜杠命令（commands）在 Claude Code 中已经被标记为 deprecated
- 官方插件（如 superpowers）也都移除了 commands 字段
- 现代插件使用 skills，通过对话自然触发或 Skill tool 显式调用

---

## 方法 3: Python 模块直接使用

### 导入并使用核心模块

```python
from pathlib import Path
from lib.security_wrapper import SecureFileAccess, SecurityError
from lib.complexity_scorer import ComplexityScorer
from lib.knowledge_store import KnowledgeStore
from lib.code_generator import CodeGenerator
from lib.executor import Executor

# 1. 安全检查
workspace = Path.cwd()
security = SecureFileAccess(workspace)

try:
    safe_path = security.validate_path("test_users.csv")
    print(f"✓ 文件验证通过: {safe_path}")
except SecurityError as e:
    print(f"❌ 安全错误: {e}")
    exit(1)

# 2. 复杂度评分
structured_req = {
    "question": "找出收入最高的用户",
    "data_sources": ["test_users.csv"],
    "analysis_type": "aggregation",
    "requires_join": False,
    "statistical_methods": []
}

scorer = ComplexityScorer()
result = scorer.score_with_rules(structured_req)
print(f"复杂度: {result.score}/10")
print(f"模式: {result.mode}")
print(f"原因: {result.reasoning}")

# 3. 代码生成
task = {
    "analysis_type": "aggregation",
    "data_source": "test_users.csv",
    "operation": "top_n",
    "sort_by": "revenue",
    "limit": 10
}

generator = CodeGenerator(Path(__file__).parent / "assets" / "sql_templates")
code = generator.generate(task)
print(f"✓ 生成了 {len(code)} 字符的代码")

# 4. 执行
executor = Executor(workspace)
output = executor.execute(code, timeout=30)
print("结果:")
print(output)

# 5. 保存到知识库
kb_dir = Path.home() / ".da-agent" / "knowledge"
kb_dir.mkdir(parents=True, exist_ok=True)
kb = KnowledgeStore(str(kb_dir / "kb.db"))

task_id = kb.save_task(
    description=structured_req["question"],
    structured_req=structured_req,
    complexity_score=result.score,
    execution_mode=result.mode
)
print(f"✓ 任务已保存 (ID: {task_id})")
```

---

## 测试和验证

### 运行完整测试套件

```bash
# 安装测试依赖
pip install -e .

# 运行所有测试
pytest -v

# 运行带覆盖率的测试
pytest --cov=lib --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 运行 Phase 1 演示

```bash
python tests/demo_phase1.py
```

这会运行 4 个演示：
1. Security Wrapper - 工作区安全验证
2. Complexity Scorer - LLM + 规则评分
3. Knowledge Store - SQLite 数据库操作
4. End-to-End - 完整分析流程

---

## 故障排除

### Python CLI 无法运行

```bash
# 确认安装
pip install -e .

# 确认依赖
pip list | grep -E "pandas|jinja2|requests"

# 查看详细错误
python cli.py analyze
```

### Claude Code 找不到技能

1. **检查插件注册**

```bash
cat ~/.claude/plugins/installed_plugins.json | grep da-agent
```

应该看到:
```json
"da-agent@local": [{
  "scope": "user",
  "installPath": "/Users/niupian/.claude/plugins/cache/da-agent-local",
  ...
}]
```

2. **检查目录结构**

```bash
ls ~/.claude/plugins/cache/da-agent-local/.claude-plugin/
# 应该有 plugin.json

ls ~/.claude/plugins/cache/da-agent-local/skills/
# 应该有 analyze-request/ 和 execute-auto/
```

3. **重新安装**

```bash
cd ~/da-agent
./install-local.sh
# 然后完全退出并重启 Claude Code
```

### 技能不响应

**记住**: 不要使用 `/da:analyze` 命令！

正确做法：
- 在对话中描述你的数据分析需求
- Claude 会自动识别并调用相关技能
- 或者让 Claude 明确调用 Skill tool

---

## 当前能力（Phase 1）

✅ **支持的分析类型：**
- Top N 查询（按列排序取前 N 条）
- 分组聚合（group by + sum/mean/count/min/max/std/median）

✅ **支持的数据格式：**
- CSV 文件（pandas 可读）

✅ **执行模式：**
- Auto 模式（复杂度 < 3）- 完全自动执行

⏳ **即将支持（Phase 2）：**
- Collaborative 模式（复杂度 3-7）- 人机协作
- Advisory 模式（复杂度 > 7）- 专家指导
- 多表 JOIN
- 时间序列分析
- 统计建模
- 可视化图表

---

## 更多文档

- [Quick Start](QUICKSTART.md)
- [Architecture](ARCHITECTURE.md)
- [Design Spec](../docs/superpowers/specs/2026-03-17-da-agent-design.md)
- [Implementation Plan](../docs/superpowers/plans/2026-03-17-da-agent-phase1-foundation.md)
