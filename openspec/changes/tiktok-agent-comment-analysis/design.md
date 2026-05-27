## Context

TikTok 评论分析项目最初是固定 pipeline（CSV → HTML 报告），后改造为 Agent 包裹层架构。核心技术栈：Python + Streamlit + DeepSeek API + SentenceTransformer。

## Goals / Non-Goals

**Goals:**
- Agent 包裹层而非全量重写——复用已有 pipeline，外层加智能决策
- 推理链可追溯：Dashboard → 类别 → 子问题 → 典型评论
- 支持中英文评论数据
- ReAct Agent 追问交互，Agent 自主选择工具调用链路
- Pipeline 检查点可见 + 低质量自动重试

**Non-Goals:**
- 不支持注册登录（本地单机工具）
- 不支持多用户协作
- 不支持实时流式分析
- 不替换 DeepSeek API（成本优先）

## Decisions

| 决策 | 选型 | 备选 | 理由 |
|------|------|------|------|
| 架构模式 | Agent 包裹层 | 全量重写 | 复用已有 pipeline，降低风险 |
| 前端 | Streamlit | Gradio / Vue | 最快出活，Python 生态统一 |
| LLM | DeepSeek-chat | GPT-4 / Qwen | 已有配置，中文好，成本低 |
| Embedding | all-MiniLM-L6-v2 | BGE-M3 | 轻量，本地运行，英文评论为主 |
| ReAct 实现 | OpenAI function calling | 手动解析 | DeepSeek 兼容，结构化可靠 |
| 图表 | Altair | Plotly / Matplotlib | 已安装在 venv，声明式语法 |
| 向量化 | SentenceTransformer | OpenAI Embedding | 本地免费，不需 API |
| 检查点 | app.py 内 Python 逻辑 | 子进程回调 | 简单可控，避免跨进程通信 |
| 重试策略 | 最多 2 轮，60s 超时 | 循环到满意 | 平衡质量与时间 |

## Risks / Trade-offs

- [LLM 幻觉] → Agent Review 自检 + 置信度标签 + 低质量重试 + 可追溯原始评论
- [状态感知不足] → Pipeline 检查点可见 + 各阶段 spinner + 完成态持久提示
- [step1 超时] → timeout 900s，纯 CPU embedding
- [国内网络] → HF_HUB_OFFLINE 离线模式 + Google Fonts 砍掉用系统字体
- [DeepSeek API 不稳定] → 3 次重试机制，缓存高频查询
