## ADDED Requirements

### Requirement: LLM quality self-check
The system SHALL use LLM to review each sub-problem's analysis quality, assigning confidence labels (high/medium/low) with specific issues and strengths.

#### Scenario: Low confidence detected
- **WHEN** more than 2 sub-problems are rated low confidence
- **THEN** the system auto-retries analysis for those sub-problems (max 2 rounds, 60s timeout per round)

### Requirement: Confidence distribution display
The system SHALL display the confidence distribution after analysis: "高:X 中:Y 低:Z" and list low-confidence items for transparency.
