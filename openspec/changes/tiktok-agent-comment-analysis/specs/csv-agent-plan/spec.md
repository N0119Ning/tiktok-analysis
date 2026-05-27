## ADDED Requirements

### Requirement: Agent auto-detects CSV structure
The system SHALL automatically detect text column, score column, and language (Chinese/English/Mixed) from uploaded CSV files.

#### Scenario: Chinese comment CSV uploaded
- **WHEN** user uploads a CSV with column `评论内容` containing Chinese text and `评分` containing numeric scores
- **THEN** the system identifies `评论内容` as text column, `评分` as score column, and language as `chinese`

#### Scenario: No score column present
- **WHEN** user uploads a CSV without a score/rating column
- **THEN** the system still proceeds with analysis, noting "评分列: 无"

### Requirement: Agent generates analysis plan
The system SHALL generate an analysis plan including suggested cluster count, cleaning strategy, and language-specific strategies.

#### Scenario: Small dataset
- **WHEN** CSV has fewer than 100 rows
- **THEN** the system recommends 3 clusters and warns about stability risks

#### Scenario: Plan explained to user
- **WHEN** plan is generated
- **THEN** the system displays human-readable plan summary before executing
