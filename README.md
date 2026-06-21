# Support Issue Analyzer

A Claude Code skill that analyzes Jira support escalation issues and generates structured developer briefings.

When a customer issue is escalated from Zendesk to Jira, developers need context fast. This tool fetches the Jira issue, searches for related tickets, and produces a markdown summary with root cause analysis and investigation steps — all from a single command.

## How It Works

```
/support "PARLE-1"
```

Claude Code will:
1. Fetch the Jira issue via the Atlassian MCP server
2. Search for related issues in the same project using keyword matching
3. Generate a structured summary with AI-powered root cause analysis
4. Write the output to `issues/PARLE-1/summary.md`

## Output

```
issues/
└── PARLE-1/
    └── summary.md
```

Each summary includes:
- Issue metadata (status, priority, reporter, assignee)
- Full description
- AI-generated analysis with likely root causes and investigation steps
- Related issues table
- Existing comments

## Setup

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- [uv](https://github.com/astral-sh/uv) installed (`brew install uv` on macOS)
- A Jira Cloud account with API access

### 1. Clone the repo

```bash
git clone git@github.com:taner-rdu/support-issue-analyzer.git
cd support-issue-analyzer
mkdir issues
```

### 2. Configure Jira credentials

Create a local `.mcp.json` in the project root (never commit this):

```json
{
  "mcpServers": {
    "atlassian": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://your-instance.atlassian.net",
        "JIRA_USERNAME": "your@email.com",
        "JIRA_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

### 3. Run

```bash
claude
```

Then use the command:

```
/support "PARLE-1"
```

## Roadmap

- **Phase 1** ✅ Jira issue fetch + related issue search + AI summary
- **Phase 2** 🔜 GitHub issues search — match escalation to filed bugs
- **Phase 3** 🔜 Local repo analysis — identify relevant files and recent commits
