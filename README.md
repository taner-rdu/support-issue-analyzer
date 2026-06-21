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
3. Search Slack for related discussions via the Slack MCP server
4. Search GitHub for related issues via the GitHub MCP server (and offer to file one if nothing matches)
5. Generate a structured summary with AI-powered root cause analysis
6. Write the output to `issues/PARLE-1/summary.md`

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
- Slack discussions table
- GitHub issues table
- Existing comments

## Setup

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- [uv](https://github.com/astral-sh/uv) installed (`brew install uv` on macOS)
- [Node.js](https://nodejs.org/) (for `npx`, used by the Slack and GitHub MCP servers)
- A Jira Cloud account with API access
- A Slack app/bot token with access to the channels you want searched
- A GitHub personal access token with `repo` scope (for searching and filing issues)

### 1. Configure MCP servers

Create a local `.mcp.json` in the project root (never commit this — it's already in `.gitignore`):

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
    },
    "slack": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_TEAM_ID": "your-team-id"
      }
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_github_token"
      }
    }
  }
}
```

- Generate a Jira API token at: https://id.atlassian.com/manage-profile/security/api-tokens
- Create a Slack bot at https://api.slack.com/apps and install it to your workspace. Invite the bot to every channel you want it to search (it can only read channels it's a member of). At minimum it needs the `channels:history`, `channels:read`, `groups:history`, `groups:read`, `search:read.public`, and `search:read.private` scopes — add `users:read` and `users.profile:read` too if you want author names resolved instead of raw user IDs.
- Generate a GitHub personal access token at: https://github.com/settings/tokens

After adding or changing `.mcp.json`, restart Claude Code so it picks up the new servers.

### 2. Run

```bash
claude
```

Then use the command:

```
/support "PARLE-1"
```

## Roadmap

- **Phase 1** ✅ Jira issue fetch + related issue search + AI summary
- **Phase 2** ✅ Slack discussion search
- **Phase 3** ✅ GitHub issues search — match escalation to filed bugs, offer to file new ones
- **Phase 4** 🔜 Local repo analysis — identify relevant files and recent commits
