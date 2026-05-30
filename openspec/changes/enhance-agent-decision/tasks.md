# 任务清单: Pipeline Tool 化

## Phase 1: 工具定义 + 实现

- [ ] 1.1 新建 `agent_pipeline.py`，定义 10 个 pipeline tool 的 schema（OpenAI function calling 格式）
- [ ] 1.2 实现 `inspect_data` — 封装 `agent_plan.inspect_csv()`
- [ ] 1.3 实现 `clean_data` — 封装 `step1_embedding.filter_low_quality()`，参数化 min_words
- [ ] 1.4 实现 `generate_embeddings` — 封装 `step1_embedding.main()` 中 embedding 部分
- [ ] 1.5 实现 `classify_comments` — 封装 `step3_summary` 分类逻辑
- [ ] 1.6 实现 `split_subproblems` — 封装 `step3_summary.split_subproblems_with_llm()`
- [ ] 1.7 实现 `analyze_subproblem` — 封装 `step3_summary.generate_complete_analysis_with_llm()`
- [ ] 1.8 实现 `review_analysis` — 封装 `agent_review.review_single_subproblem()`
- [ ] 1.9 实现 `retry_analysis` — 封装 `agent_review.retry_subproblem_analysis()`
- [ ] 1.10 实现 `get_pipeline_status` — 返回当前进度、过滤率、分类数、置信度分布
- [ ] 1.11 实现 `finalize_report` — 汇总结果写入 result.json

## Phase 2: Agent 循环

- [ ] 2.1 实现 Agent ReAct 主循环 — system prompt 引导 Agent 自主规划分析路径
- [ ] 2.2 Agent 循环增加安全限制：max_rounds=30，单步超时=60s，防止无限循环或挂死
- [ ] 2.3 进度实时展示 — 每步 tool call 在 Streamlit status widget 中显示

## Phase 3: app.py 集成

- [ ] 3.1 新增"Agent 自主分析"模式按钮（与"一键分析"并列）
- [ ] 3.2 Agent 完成后的 result.json 复用现有报告页（tab2 无需改动）
- [ ] 3.3 保留"一键分析"按钮作快速模式

## Phase 4: 验证

- [ ] 4.1 用 TikTok.csv 跑 Agent 模式，检查能自主完成完整分析
- [ ] 4.2 用不同数据验证 Agent 能做出合理路径选择（短评多→调 min_words，中文→调 language）
- [ ] 4.3 验证 max_rounds 和安全限制生效
