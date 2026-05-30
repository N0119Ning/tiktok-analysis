# agent-pipeline

Agent 在 ReAct 循环中自主调用 10 个 pipeline 工具 + 5 个 query 工具，从原始 CSV 到最终报告全流程自主完成。

## 工具清单

### Pipeline 工具 (10 个)
1. `inspect_data` — 读 CSV，返回数据结构摘要
2. `clean_data` — 清洗+过滤，参数 min_words/language 可调
3. `generate_embeddings` — 文本向量化（可选）
4. `classify_comments` — 9 类关键词分类
5. `split_subproblems` — LLM 拆子问题
6. `analyze_subproblem` — LLM 生成结构化分析
7. `review_analysis` — LLM 自检质量
8. `retry_analysis` — 重分析低质量子问题
9. `get_pipeline_status` — 查询当前进度
10. `finalize_report` — 完成分析，写 result.json

### Query 工具 (5 个，复用 agent_chat.py)
`get_overall_stats`, `get_category_list`, `get_category_detail`, `search_comments`, `compare_categories`

## 行为

### Agent 决策权利
- 自主决定分析路径（先清洗还是先分类？做不做 embedding？）
- 自主决定参数（min_words 用 1 还是 2？）
- 自主决定哪些类别需要深入分析（评论数 > 20 的才拆子问题）
- 自主决定何时重试、何时放弃

### Agent 约束
- 最多 30 轮工具调用
- 连续 3 次相同 tool+相同参数 → 强制停止
- review 发现 low 必须 retry，但每个子问题最多 retry 2 次
- 不要跳过 inspect_data 和 clean_data

### 模式共存
- "一键分析"模式（原固定 pipeline）保留
- "Agent 自主分析"模式（新）让 Agent 自主决策
- 两种模式共享同 result.json 格式，报告页复用
