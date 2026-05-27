## ADDED Requirements

### Requirement: ReAct Agent with 5 tools
The system SHALL provide a ReAct loop where LLM autonomously selects from 5 tools (get_overall_stats, get_category_list, get_category_detail, search_comments, compare_categories) to answer user questions.

#### Scenario: LLM calls tool chain
- **WHEN** user asks "最严重的问题是什么"
- **THEN** the Agent calls get_category_list → reviews severity → answers with data

#### Scenario: Max 8 tool call rounds
- **WHEN** LLM has made 8 rounds of tool calls without answering
- **THEN** the system forces a final answer from collected data

### Requirement: Thinking process visible
The system SHALL display each tool call and result in an expandable panel inside the chat message, showing the reasoning chain.

#### Scenario: User expands thinking panel
- **WHEN** user clicks "查看 AI 推理过程" expander
- **THEN** each tool call (name, arguments, result preview) is shown with full data available
