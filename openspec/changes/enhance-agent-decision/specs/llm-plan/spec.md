# llm-plan

Agent 通过 LLM 抽样阅读评论后自主制定分析策略，不再使用硬编码规则。

## 行为

### 输入
- CSV 数据摘要（总条数、语言、评分分布、文本长度分布）
- 50 条按评分分层随机采样的评论

### LLM 决策输出
```json
{
  "n_clusters": <int>,
  "analysis_angle": "<产品体验|运营效率|技术质量|安全合规>",
  "focus_areas": ["<话题>"],
  "anomalies": ["<异常>"],
  "cleaning_strategy": "<standard|lenient|strict>",
  "reasoning": "<决策理由>"
}
```

### Fallback
- LLM 调用失败或 JSON 解析失败 → 回退到 `build_plan()` 规则逻辑
- 回退时界面提示"LLM 规划失败，已使用默认策略"

## 约束
- max_tokens=400，temperature=0.3
- 超时 20s
- 采样需按评分分层（1-5 星各 10 条，不足则全部取）
