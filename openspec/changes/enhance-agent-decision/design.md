# 技术设计: Agent 决策能力增强

## 1. LLM Agent Plan

### 当前逻辑 (`build_plan`)
```python
if total < 100:      n_clusters = 3
elif total < 500:    n_clusters = 5
elif total < 2000:   n_clusters = 6
else:                n_clusters = 8
```
完全是硬编码规则，没有数据理解。

### 新方案

`agent_plan.py` 新增 `llm_build_plan()` 函数：

**Step 1: 采样**
从 CSV 随机抽取 50 条评论作为样本（按评分分层采样，保证各分数段都有代表）

**Step 2: 构建 LLM prompt**
```
你是资深产品分析师。请阅读以下用户评论样本，制定分析策略。

[数据摘要]
- 总评论数、评分分布、语言、评论文本长度分布

[评论样本]
- 50 条随机评论

请输出 JSON:
{
  "n_clusters": <建议聚类数 3-10>,
  "analysis_angle": "<产品体验|运营效率|技术质量|安全合规>",
  "focus_areas": ["<重点关注话题1>", "<话题2>"],
  "anomalies": ["<异常模式>"] 或 [],
  "cleaning_strategy": "<standard|lenient|strict>",
  "reasoning": "<简短解释为什么这样规划>"
}
```

**Step 3: 解析 + 展示**
LLM 返回 JSON → 解析 → 合并到 `plan` 字典 → 用户确认

### 向后兼容
保留 `build_plan()` 作为 fallback：如果 LLM 调用失败，回退到原规则逻辑。

---

## 2. 自适应 Pipeline

### 新增 `agent_pipeline.py`

Pipeline Agent 在关键检查点调用 DeepSeek，决定下一步动作：

```
Checkpoint 1 (Step1 后):
  输入: 过滤率、平均词数、原始/清洗后条数
  决策: 清洗质量 OK？→ 继续 / 调整 min_words 重洗 / 跳过

Checkpoint 2 (Step3 后):
  输入: 类别数、各类严重度、子问题数
  决策: 分类满意？→ 进入 review / 合并小类别 / 拆分大类

Checkpoint 3 (Review 后):
  输入: 置信度分布、低质量子问题数、前一轮改善情况
  决策: 质量达标？→ 停止 / 继续重试 / 换角度重分析
```

### Agent 循环协议

```python
def pipeline_agent_step(checkpoint_name, metrics, comments_sample):
    """调用 LLM 做 pipeline 决策"""
    prompt = f"""
你是 Pipeline 质检员。当前在 {checkpoint_name}。
观察以下指标，决定下一步。

[指标]
{json.dumps(metrics)}

[上下文样本]
{comments_sample[:3]}

输出 JSON:
{{"action": "continue|retry|adjust|skip|stop",
  "reason": "<决策理由>",
  "params": {{}}"adjust"时附带调整参数}}
"""
    response = client.chat.completions.create(...)
    return json.loads(response.choices[0].message.content)
```

### Review 动态终止

当前：固定 `max_retry_rounds = 2`

改为：
```python
while True:
    reviewed = review_all_categories(...)
    low_count = reviewed['low_confidence']
    
    if low_count == 0:
        break  # 完美，停止
    
    improvement = previous_low - low_count
    if improvement <= 0 and consecutive_no_improvement >= 2:
        break  # 连续无改善，停止
    
    consecutive_no_improvement = 0 if improvement > 0 else consecutive_no_improvement + 1
    previous_low = low_count
    
    if round >= 5:
        break  # 最多 5 轮兜底
```

---

## 文件变更汇总

| 文件 | 动作 |
|------|------|
| `agent_plan.py` | 新增 `llm_build_plan()`，保留 `build_plan()` 作 fallback |
| `agent_pipeline.py` | **新建** — Pipeline Agent 决策函数 |
| `app.py` | pipeline 段插入 Agent checkpoints；plan 按钮调用 `llm_build_plan` |
| `agent_review.py` | `review_all_categories` 改为动态终止 |
