# 任务清单: Agent 决策能力增强

## Phase 1: LLM Agent Plan

- [ ] 1.1 `agent_plan.py` 新增 `sample_comments()` — 按评分分层随机采样 50 条
- [ ] 1.2 `agent_plan.py` 新增 `llm_build_plan(info, samples)` — 调用 DeepSeek 生成分析策略 JSON
- [ ] 1.3 `agent_plan.py` `agent_plan()` 主入口改为优先 `llm_build_plan`，失败回退 `build_plan`
- [ ] 1.4 `app.py` plan 生成按钮调用改为展示 LLM 的 `reasoning` 字段
- [ ] 1.5 测试：用 TikTok.csv 验证 LLM 能正确生成 plan JSON

## Phase 2: 自适应 Pipeline

- [ ] 2.1 新建 `agent_pipeline.py` — 实现 `pipeline_agent_step()` 决策函数
- [ ] 2.2 `app.py` 检查点 1 后插入 Agent 决策：清洗质量→继续/调整/重洗
- [ ] 2.3 `app.py` 检查点 2 后插入 Agent 决策：分类质量→继续/拆分/合并
- [ ] 2.4 `agent_review.py` 改 `review_all_categories` 为动态终止条件
- [ ] 2.5 测试：完整运行 pipeline，验证 Agent 在各检查点能做出合理决策

## Phase 3: 验证

- [ ] 3.1 用多种数据（中/英/混合）验证 plan 生成的合理性和稳定性
- [ ] 3.2 确认 LLM plan 失败时 fallback 到规则逻辑正常工作
- [ ] 3.3 确认 pipeline Agent 不会陷入无限循环（每个 check 上限 3 次 retry）
