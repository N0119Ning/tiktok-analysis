## ADDED Requirements

### Requirement: Initial loading indicator
The system SHALL display a styled loading banner ("正在初始化 AI 评论分析引擎...") with spinning animation immediately after page load, clearing it once content renders.

#### Scenario: Page initial load
- **WHEN** user opens the app URL
- **THEN** a blue loading banner with spinner is immediately visible, replaced by the main title after initialization

### Requirement: Pipeline status visibility
The system SHALL show each pipeline step with progress messages and checkpoint metrics inside an expandable status widget.

#### Scenario: Pipeline running
- **WHEN** user confirms analysis plan
- **THEN** status widget shows each step with checkpoints, and completion message persists after rerun

### Requirement: Agent plan completion feedback
The system SHALL show "计划生成完毕！确认后即可开始分析。" after agent plan generation, and "分析已完成！点击上方「分析报告」查看结果" after pipeline completion.
