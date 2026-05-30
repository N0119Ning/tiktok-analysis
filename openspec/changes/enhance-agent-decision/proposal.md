## Why

当前项目的 Agent 能力名不副实：

1. **Agent Plan 是假 Agent** — `agent_plan.py` 的 `build_plan()` 只有几行 if-else，n_clusters 根据行数机械匹配（<100 条=3 类，>2000 条=8 类），完全没有"智能"。LLM 从未参与规划决策。
2. **Pipeline 是固定流水线** — 三步直线执行（清洗→分类→分析），没有分支、没有自适应、没有"观察结果后决定下一步"的 Agent 循环。
3. **Review 只有一次 retry** — 固定最多 2 轮，每轮对所有低置信度子问题无差别重试，不会根据重试效果调整策略。

用户看到的是一个自动化脚本，不是 Agent。

## What Changes

### 改动 1: LLM Agent Plan — 真正的智能规划

- **`agent_plan.py`** 重写：`build_plan()` 不再用 if-else 规则，改为调用 DeepSeek LLM
- LLM 输入：CSV 数据摘要 + 50 条随机评论样本
- LLM 自主决策输出：n_clusters、清洗策略、分析角度（产品/运营/技术/安全）、关注焦点（特定话题/评分区间/时间模式）
- 人工可确认/修改：LLM 规划结果仍展示给用户确认

### 改动 2: 自适应 Pipeline — 分支决策 + 多轮自改进

- **`app.py`** pipeline 改为 Agent 循环：每步执行后，Agent 观察输出质量，决定下一步
- 新增 `agent_pipeline.py`：Pipeline Agent，在关键节点做决策
  - Step1 后：数据清洗质量是否达标？是否需要调整过滤策略？
  - Step3 后：分类结果是否符合预期？是否需要拆分/合并类别？
  - Review 后：当前低置信度子问题是否需要换分析角度重试？是否该停止？
- Review 改为动态终止：不再固定 2 轮，改为"连续 N 轮无改善 → 停止"，或"低置信度占比 < 阈值 → 停止"

## Capabilities

### New Capabilities
- `llm-plan`: LLM 抽样阅读评论后自主制定分析策略（聚类数、分析角度、关注焦点、异常检测）
- `adaptive-pipeline`: Pipeline Agent 在关键检查点观察质量指标，自主决定是否调整策略、重新执行或进入下一阶段

### Modified Capabilities
- `agent-review`: 多轮自改进从固定 2 轮改为动态终止条件

## Impact

- 受影响的文件：`agent_plan.py`(重写), `app.py`(pipeline 改为 Agent 循环), 新增 `agent_pipeline.py`
- 依赖：DeepSeek API（多一轮 LLM 调用用于 plan 生成）
- 向后兼容：用户仍可查看和确认 Agent 生成的 plan
- 废弃：`build_plan()` 中的硬编码规则逻辑
