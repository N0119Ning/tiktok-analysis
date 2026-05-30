# 技术设计: Pipeline Tool 化

## Tool 定义 (OpenAI function calling 格式)

### `inspect_data`
```json
{
  "name": "inspect_data",
  "description": "读取CSV文件，返回列名、数据类型、样本、评分分布、语言检测结果",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```
**返回**: `{total_rows, columns, text_column, score_column, language, score_distribution, sample_comments}`

---

### `clean_data`
```json
{
  "name": "clean_data",
  "description": "清洗评论数据：去噪、拼写纠正、过滤低质量评论。如果过滤率太高或太低，可以调整参数重试",
  "parameters": {
    "type": "object",
    "properties": {
      "min_words": {"type": "integer", "description": "最小词数阈值，默认2。如果过滤太多短评可调到1"},
      "language": {"type": "string", "description": "数据语言，影响清洗策略。可选: chinese/english/mixed"}
    },
    "required": []
  }
}
```
**返回**: `{rows_in, rows_out, filter_rate, filter_breakdown: {by_length, by_emotion}, avg_words}`

---

### `generate_embeddings`
```json
{
  "name": "generate_embeddings",
  "description": "将清洗后的文本转为向量（SentenceTransformer all-MiniLM-L6-v2）。数据量大(>5000条)且需要聚类分析时调用",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```
**返回**: `{shape: [rows, dims], elapsed_ms}`

---

### `classify_comments`
```json
{
  "name": "classify_comments",
  "description": "将评论按9大类别(登录/内容/视频/广告/功能/性能/隐私/社交/UI)进行关键词分类",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```
**返回**: `{categories: [{id, label, count, pct}], total_classified}`

---

### `split_subproblems`
```json
{
  "name": "split_subproblems",
  "description": "对某个类别内的评论用LLM自动拆解为子问题。仅对评论数>20的类别调用",
  "parameters": {
    "type": "object",
    "properties": {
      "category_id": {"type": "string", "description": "类别ID，如 account/content/video/ads/feature/performance/privacy/social/ui"}
    },
    "required": ["category_id"]
  }
}
```
**返回**: `{subproblems: [{name, comment_count}]}`

---

### `analyze_subproblem`
```json
{
  "name": "analyze_subproblem",
  "description": "用LLM对一个子问题生成结构化分析：问题本质、用户场景、影响、短期方案、长期方案、验证指标",
  "parameters": {
    "type": "object",
    "properties": {
      "category_id": {"type": "string"},
      "subproblem_name": {"type": "string"}
    },
    "required": ["category_id", "subproblem_name"]
  }
}
```
**返回**: `{problem, scene, impact, short_term, long_term, metrics, keywords, representative_comments}`

---

### `review_analysis`
```json
{
  "name": "review_analysis",
  "description": "LLM自检某个子问题的分析质量，返回置信度标签(high/medium/low)和问题清单",
  "parameters": {
    "type": "object",
    "properties": {
      "category_id": {"type": "string"},
      "subproblem_name": {"type": "string"}
    },
    "required": ["category_id", "subproblem_name"]
  }
}
```
**返回**: `{confidence: "high|medium|low", issues: [], strengths: []}`

---

### `retry_analysis`
```json
{
  "name": "retry_analysis",
  "description": "对低质量子问题重新分析，使用不同的prompt角度。仅在review_analysis返回low时调用",
  "parameters": {
    "type": "object",
    "properties": {
      "category_id": {"type": "string"},
      "subproblem_name": {"type": "string"}
    },
    "required": ["category_id", "subproblem_name"]
  }
}
```
**返回**: 同 analyze_subproblem

---

### `get_pipeline_status`
```json
{
  "name": "get_pipeline_status",
  "description": "查看当前分析进度：已完成步骤、数据量、分类数、置信度分布",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```
**返回**: `{steps_completed: [], total_comments, cleaned_comments, categories_classified, subproblems_analyzed, low_confidence_count}`

---

### `finalize_report`
```json
{
  "name": "finalize_report",
  "description": "确认分析完成，生成最终报告JSON。调用后分析结束",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```
**返回**: `{success: true, result_path, summary}`

---

## Agent 循环

```python
SYSTEM_PROMPT = """你是评论分析Agent。你可以调用工具来完成从数据到报告的完整分析。

工作流程建议（但不必严格遵守，根据数据实际情况灵活调整）:
1. inspect_data → 了解数据
2. clean_data → 清洗
3. classify_comments → 分类
4. 对重要的类别 split_subproblems → analyze_subproblem
5. review_analysis → 低质量则 retry_analysis
6. finalize_report → 完成

规则:
- 每个工具调用前先思考: 此时调这个工具是否合理?
- 清洗后如果过滤率>30%，考虑调整min_words重新清洗
- analyze_subproblem之前必须先split_subproblems
- review_analysis发现low必须retry，但最多retry 2次
- 不要重复调用同一个工具用相同参数（死循环）
- 感觉分析OK了就finalize_report结束
"""
```

## 安全限制

- `MAX_TOOL_ROUNDS = 30` — 最多 30 轮工具调用
- 连续 3 次相同 tool+相同参数 → 强制停止
- 单次 tool 执行超时 60s
- 所有 LLM 调用用 `deepseek-flash-v4`

## 结果复用

Agent 生成的 result.json 结构复用现有格式，tab2 报告页无需改动。
