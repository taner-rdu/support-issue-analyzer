---
name: jira-support-analyzer
description: Analyze a Jira support escalation issue and generate a structured summary. Use this skill whenever the user runs /support followed by a Jira issue key (e.g. /support "PARLE-1"), or asks to analyze, summarize, or investigate a Jira issue. Also triggers when the user wants to understand the context of a support escalation, find related issues, or generate a summary file for a Jira ticket.
---

# Jira Support Issue Analyzer

Analyzes a Jira support escalation issue, searches for related issues, and writes a structured markdown summary to the local filesystem.

## Trigger

User runs:
```
/support "ISSUE-KEY"
```
Example: `/support "PARLE-1"`

## Steps

### 1. Fetch the target issue

Use the Atlassian MCP to fetch the issue by key. Extract:
- Summary (title)
- Description
- Status
- Priority
- Reporter
- Assignee
- Created date
- Labels
- Comments (if any)

### 2. Search for related issues

Run a JQL keyword search against the same project to find related issues. Use 3-5 significant keywords extracted from the issue summary and description.

Example JQL:
```
project = PARLE AND text ~ "keyword1 keyword2" AND key != ISSUE-KEY ORDER BY created DESC
```

Limit to 5 most relevant results. For each related issue, capture: key, summary, status.

### 3. Search Slack for related discussions

Use the Slack MCP to search for messages related to the issue. Use 2-3 keywords from the issue title and description.

Search both public and private channels. For each relevant result, capture:
- Channel name
- Message text (snippet)
- Author
- Timestamp

Limit to 5 most relevant results.

### 4. Search GitHub for related issues

Use the GitHub MCP to search for open and closed issues in the relevant repository that match keywords from the Jira issue.

Search query example: `login password reset repo:org/repo`

For each relevant result, capture:
- Issue number
- Title
- Status (open/closed)
- URL

Limit to 5 most relevant results.

If no related issues are found, offer to create a new GitHub issue based on the Jira analysis.

### 5. Generate the summary

Write a structured markdown summary with the following sections:

```markdown
# [ISSUE-KEY] Issue Title

## Overview
- **Status:** 
- **Priority:** 
- **Reporter:** 
- **Assignee:** 
- **Created:** 

## Description
[Full issue description]

## Analysis
[2-3 paragraph Claude-generated analysis of the issue. Include: likely root cause based on description, impact assessment, suggested investigation steps for the dev team.]

## Related Issues
| Key | Summary | Status |
|-----|---------|--------|
| PARLE-X | ... | ... |

## Slack Discussions
| Channel | Author | Date | Snippet |
|---------|--------|------|---------|
| #channel | username | date | message snippet |

## GitHub Issues
| # | Title | Status | URL |
|---|-------|--------|-----|
| 123 | Fix login after reset | open | https://... |

## Comments
[Include any existing comments on the issue]
```

### 6. Write output

Create the directory and file:
```
issues/ISSUE-KEY/summary.md
```

Example: `issues/PARLE-1/summary.md`

If the directory already exists, overwrite the summary file.

Confirm to the user when done with the file path.

## Notes

- Always search for related issues even if the issue seems straightforward — context matters for devs
- If no related issues are found, say so explicitly in the Related Issues section
- Keep the Analysis section practical and dev-focused, not generic
- Do not include the Jira URL or API credentials in the output file
- If no Slack results are found, say so explicitly in the Slack Discussions section
- Search Slack even if no related Jira issues are found — engineers often discuss issues there before filing tickets
- GitHub repository: taner-rdu/parlez
- When searching GitHub issues, always search taner-rdu/parlez
- When offering to create a GitHub issue, create it in taner-rdu/parlez
