## 1. Agent 架构搭建

- [x] 1.1 创建 `agent_plan.py` — CSV 检查 + 语言检测 + 分析计划生成
- [x] 1.2 创建 `agent_review.py` — LLM 自检 + 置信度标签 + 低质量重试
- [x] 1.3 创建 `agent_chat.py` — ReAct Agent + 5 工具函数 + function calling
- [x] 1.4 创建 `app.py` — Streamlit 三页前端（上传/报告/追问）

## 2. Pipeline 改造

- [x] 2.1 `step1_embedding.py` — 加 HF_HUB_OFFLINE 离线模式
- [x] 2.2 `step3_summary.py` — 中文输出适配
- [x] 2.3 废弃 `step4_html.py`（由 Streamlit 替代）
- [x] 2.4 废弃 `step2_clustering.py`（由关键词分类替代）

## 3. 数据可视化

- [x] 3.1 Altair 情绪环形图
- [x] 3.2 Altair 类别分布环形图
- [x] 3.3 Altair 评论量水平柱状图
- [x] 3.4 Altair 均分柱状图（升序）

## 4. UI 状态与体验

- [x] 4.1 初始加载态（蓝色加载条 + 旋转动画）
- [x] 4.2 Pipeline 检查点显示（step1 后 + step3 后）
- [x] 4.3 Agent Plan 完成提示
- [x] 4.4 Pipeline 完成后持久提示
- [x] 4.5 ReAct 推理过程折叠面板
- [x] 4.6 Google Fonts 砍掉 → 系统字体（避免白屏）

## 5. 文档

- [x] 5.1 PRD.md — 产品需求文档
- [x] 5.2 CLAUDE.md — 项目技术文档
