---
name: summary-validator
description: Validate a generated support issue summary using the summary-validator MCP tool. Use when the user runs /validate followed by a Jira issue key (e.g. /validate "PARLE-1").
---

# Summary Validator

## Trigger

User runs:
```
/validate "ISSUE-KEY"
```

## Steps

### 1. Call the validator

Use the `validate_summary` MCP tool with the given issue key.

### 2. Output the result

Output the raw JSON returned by the tool. No markdown, no code blocks, no additional text.
