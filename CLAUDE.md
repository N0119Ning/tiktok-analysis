# AI 评论分析 Agent — CLAUDE.md

## 启动

```bash
cd E:\pycharm_project2\tiktok_project
..\.venv\Scripts\streamlit run app.py --server.port 8502
```

## 架构

```
用户上传 CSV
    → [Agent Plan]  检查数据→决定参数→展示计划
    → [Pipeline]    清洗+向量化 + 检查点
                    分类+LLM分析 + 检查点
    → [Agent Review] LLM自检→置信度标签+低质量重试
    → [Streamlit]    Tab1 上传/规划 | Tab2 报告+图表 | Tab3 ReAct追问
```

## 关键文件

| 文件 | 角色 |
|------|------|
| `app.py` | Streamlit 主应用（UI、CSS、Altair图表、Pipeline编排） |
| `agent_plan.py` | CSV 检查 → 语言/列检测 → 分析计划 |
| `agent_review.py` | LLM 自检 + 低质量重试 |
| `agent_chat.py` | ReAct Agent（5工具自主调用） |
| `scripts/step1_embedding.py` | 清洗 + all-MiniLM-L6-v2 向量化 |
| `scripts/step3_summary.py` | 9类关键词分类 + LLM子问题拆分 |
| `PRD.md` | 产品需求文档（竞品分析、评估指标等） |

## 技术栈

- Streamlit + Altair | DeepSeek-chat | all-MiniLM-L6-v2 (384维) 本地

## 坑

- `HF_HUB_OFFLINE=1` 必须在 subprocess env 设置（不能在脚本内 import 之后设）
- 10000条评论CPT约5-10分钟，timeout 900s
- Google Fonts 国内屏蔽 → 系统字体
