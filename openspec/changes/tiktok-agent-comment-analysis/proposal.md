## Why

App 产品每天产生海量用户评论，PM/运营需要从中快速提取可行动的洞察。传统方式（Excel 手工分析、通用 LLM 单次对话）无法处理万级评论量，且结论不可追溯。需要一个 AI Agent 驱动的分析工具，自动完成从数据上传到可交互报告的全流程。

## What Changes

- **新增** Streamlit Web 前端，提供上传、报告、追问三页交互
- **新增** Agent Plan 模块：自动检测 CSV 数据结构（文本列、评分列、语言），生成分析计划
- **新增** Pipeline 执行引擎：数据清洗 → 向量化 → 关键词分类 → LLM 子问题拆分 → 结构化分析
- **新增** Agent Review 模块：LLM 自检每个子问题质量，输出置信度标签，低质量自动重试
- **新增** ReAct Agent 追问模块：5 个工具（全局统计/类别列表/类别详情/关键词搜索/类别对比），LLM 自主决定调用链路
- **新增** 数据可视化：Altair 环形图 + 柱状图，展示情绪分布、类别分布、均分对比
- **新增** Pipeline 检查点：每步后显示质量指标，低质量子问题自动重试
- **废弃** 原静态 HTML 报告（step4_html.py），由 Streamlit 替代

## Capabilities

### New Capabilities
- `csv-agent-plan`: Agent 自动检查上传的 CSV，检测数据结构，生成分析计划
- `pipeline-execution`: 数据清洗+向量化+分类+LLM分析的可视化流水线
- `agent-review`: LLM 自检分析质量，置信度标签，低质量自动重试
- `react-chat`: ReAct Agent 追问，5 工具自主调用，推理过程可见
- `data-visualization`: Altair 图表仪表板（情绪环形图、类别分布、均分柱状图）
- `ui-state-feedback`: 全流程状态提示（加载中→检查中→分析中→完成）

### Modified Capabilities
- 无（新项目，无已存在的 capability 需要修改）

## Impact

- 受影响的文件：`app.py`, `agent_plan.py`, `agent_review.py`, `agent_chat.py`, `scripts/step1_embedding.py`, `scripts/step3_summary.py`
- 依赖：DeepSeek API (`deepseek-chat`), Streamlit, Altair, SentenceTransformer, PaddleOCR (备选)
- 废弃：`scripts/step4_html.py`, `scripts/step2_clustering.py`
