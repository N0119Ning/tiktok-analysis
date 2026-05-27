## ADDED Requirements

### Requirement: Data cleaning with quality checkpoint
The system SHALL clean uploaded CSV data (spell correction, emoji removal, low-quality filtering) and display a quality checkpoint showing original vs cleaned row count and average word count.

#### Scenario: Normal dataset
- **WHEN** step1 completes successfully
- **THEN** the system displays checkpoint: "清洗完成 — N→M条 (过滤X.X%) | 平均Y.Y词/条"

### Requirement: LLM-powered category analysis
The system SHALL classify comments into 9 categories (account, content, video, ads, feature, performance, privacy, social, ui) and use LLM to split each category into sub-problems with structured analysis.

#### Scenario: Category analysis complete
- **WHEN** step3 completes successfully
- **THEN** output contains structured sub-problems with problem, scene, impact, short-term solution, long-term solution, and metrics

### Requirement: Pipeline timeout handling
The system SHALL enforce timeouts for subprocess calls (step1: 900s, step3: 600s) and display clear error messages on failure.
