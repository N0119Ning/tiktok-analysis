## Why

当前项目的 Agent 能力名不副实——pipeline 是固定三步直线执行，完全没有"观察数据→决定策略→调用工具→观察结果→决定下一步"的 Agent 循环。

## What Changes

### P0: Pipeline Tool 化 — Agent 自主调工具

把 `step1_embedding.py` + `step3_summary.py` + `agent_review.py` 的每一步拆成独立 tool（OpenAI function calling 格式），Agent 在 ReAct 循环中自主决定调用什么工具、什么顺序、什么参数。

### 工具集 (15 个)

**Pipeline 工具 (9 个) — 新增**

| 工具 | 来源 | 功能 |
|------|------|------|
| `inspect_data` | `agent_plan.inspect_csv` | 读 CSV，返回列名/类型/样本/评分分布/语言 |
| `clean_data` | `step1_embedding` | 清洗+拼写纠正，参数: min_words, language |
| `generate_embeddings` | `step1_embedding` | 文本转向量（可选，Agent 判断是否需要） |
| `classify_comments` | `step3_summary` | 9 类关键词分类，返回各类计数 |
| `split_subproblems` | `step3_summary` | LLM 拆子问题，参数: category_id |
| `analyze_subproblem` | `step3_summary` | LLM 生成 problem/scene/impact/solution |
| `review_analysis` | `agent_review` | LLM 自检质量，返回 confidence |
| `retry_analysis` | `agent_review` | 重分析低质量子问题 |
| `get_pipeline_status` | **新建** | 返回当前进度: {step, counts, quality} |

**Query 工具 (5 个) — 已有，保留**
`get_overall_stats`, `get_category_list`, `get_category_detail`, `search_comments`, `compare_categories`

**Agent 决策工具 (1 个) — 新增**

| 工具 | 功能 |
|------|------|
| `finalize_report` | Agent 确认分析完成，汇总结果 |

### Agent 循环

```
用户: "分析这份CSV"

Agent: → inspect_data → "1万条英文评论，评分1-5分布均匀，98%有效文本"
       → clean_data(min_words=2) → "过滤8%，保留9200条"
       → classify_comments → "9类分布：性能320条，账号280条..."
       → split_subproblems("performance") → "3个子问题"
       → split_subproblems("account") → "2个子问题"
       → analyze_subproblem("performance", "启动卡顿") → "完成"
       → analyze_subproblem("performance", "视频加载慢") → "完成"
       → ...
       → review_analysis → "2个低质量，重试"
       → retry_analysis("account", "登录失败") → "改进了"
       → finalize_report → "分析完成"
```

### 回退兼容

`app.py` 保留现有的固定 pipeline 按钮（"一键分析"），新增"Agent 自主分析"模式。用户可选两种模式。

## Capabilities

### New
- `agent-pipeline`: Agent 在 ReAct 循环中自主调用 15 个工具完成从数据到报告的全流程
- `pipeline-status`: 进度状态查询，Agent 据此决定下一步

### Modified
- `agent-plan`: 从 `build_plan()` 规则逻辑改为 `inspect_data` tool
- `agent-review`: 不再作为独立阶段，而是 Agent 在分析后自主调用的工具
- `react-chat`: 追问工具集保持不变

## Impact

- 新增: `agent_pipeline.py` (Agent 循环 + 15 个 tool 定义 + tool 实现)
- 改动: `app.py` (增加 "Agent 自主分析" 模式入口)
- 保留: `agent_chat.py` (追问 tab 不变)
- 保留: `scripts/step1_embedding.py`, `scripts/step3_summary.py`, `agent_review.py` (被 tool 封装调用，不删除)
