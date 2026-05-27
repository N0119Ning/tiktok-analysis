## ADDED Requirements

### Requirement: 4-chart dashboard
The system SHALL render 4 Altair charts in a 2×2 grid: sentiment donut, category distribution donut, comment volume horizontal bar chart, and average score bar chart (sorted low-to-high).

#### Scenario: Charts render after analysis
- **WHEN** pipeline completes and user navigates to Tab2
- **THEN** all 4 charts display with consistent color scheme on light background

### Requirement: Empty data fallback
The system SHALL show "暂无分类数据" placeholder when chart data is empty instead of rendering broken charts.
