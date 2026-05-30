# adaptive-pipeline

Pipeline 不再固定三步直线执行，改为 Agent 在关键检查点观察结果、自主决定下一步。

## 行为

### 检查点 1 — 清洗后决策
- 输入: `{filter_rate, avg_words, rows_in, rows_out}`
- Action: `continue` → 进入下一步 / `adjust` → 调整 min_words 重洗 / `skip` → 跳过分类
- 约束: 最多 `adjust` 2 次

### 检查点 2 — 分类后决策
- 输入: `{category_count, subproblem_count, category_distribution}`
- Action: `continue` → 进入 review / `split` → 拆分大类 / `merge` → 合并小类
- 约束: `split`/`merge` 后重新分类，最多 1 次

### Review — 动态终止
- 条件 1: low_confidence == 0 → 立即停止
- 条件 2: 连续 2 轮 low_count 无改善 → 停止
- 条件 3: 达到 5 轮 → 停止（兜底）
- 每轮最多重试 5 个低置信度子问题（避免无限 LLM 调用）

## 约束
- 每个 check 有 action 上限
- 每次 LLM 决策用独立 prompt，temperature=0.1，max_tokens=200
- pipeline Agent 决策日志记录到 pipeline.log
