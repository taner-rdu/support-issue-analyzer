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
- Update log (append-only across re-runs)

## Setup

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- [uv](https://github.com/astral-sh/uv) installed (`brew install uv` on macOS)
- [Node.js](https://nodejs.org/) (for `npx`, used by the Slack and GitHub MCP servers)
- A Jira Cloud account with API access
- A Slack app/bot token with access to the channels you want searched
- A GitHub personal access token with `repo` scope (for searching and filing issues)

### 1. Add secrets to AWS Secrets Manager

All credentials are stored in AWS Secrets Manager under the `support-analyzer/` prefix. Create the following secrets before running the tool:

| Secret name | Value |
| --- | --- |
| `support-analyzer/anthropic-api-key` | Anthropic API key — generate at https://console.anthropic.com |
| `support-analyzer/jira-url` | Your Jira instance URL (e.g. `https://your-org.atlassian.net`) |
| `support-analyzer/jira-username` | Your Jira account email |
| `support-analyzer/jira-token` | Jira API token — generate at https://id.atlassian.com/manage-profile/security/api-tokens |
| `support-analyzer/jira-project-key` | Jira project key to search (e.g. `MYPROJECT`) |
| `support-analyzer/slack-bot-token` | Slack bot token (`xoxb-...`) — create a bot at https://api.slack.com/apps |
| `support-analyzer/slack-team-id` | Slack workspace team ID |
| `support-analyzer/slack-channel` | Slack channel name to search (e.g. `support`) |
| `support-analyzer/github-token` | GitHub personal access token with `repo` scope — generate at https://github.com/settings/tokens |
| `support-analyzer/github-test-issue-repo` | GitHub repo used for e2e test issues (e.g. `your-org/your-repo`) |

For the Slack bot, invite it to the channel you want it to search and grant it at minimum the `channels:history`, `channels:read`, `groups:history`, `groups:read`, `search:read.public`, and `search:read.private` scopes. Add `users:read` and `users.profile:read` if you want author names resolved instead of raw user IDs.

### 2. Generate MCP config

Run the setup script to generate `.mcp.json` automatically from your secrets:

```bash
uv run python generate_mcp_config.py
```

This writes `.mcp.json` to the project root (gitignored). You need valid AWS credentials in your environment — an IAM role, a named profile (`AWS_PROFILE`), or `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` env vars will all work.

After running it, restart Claude Code so it picks up the new servers.

### 3. Run

```bash
claude
```

Then use the command:

```
/support "PARLE-1"
```

## Testing

The e2e test creates real Jira, GitHub, and Slack fixtures, runs the `/support` skill, then validates the output using the `/validate` skill backed by the `summary-validator` MCP server.

```bash
uv run pytest tests/ -v
```

CI runs on every push via GitHub Actions using OIDC authentication to AWS — no long-lived credentials stored in GitHub. All secrets are fetched from AWS Secrets Manager at runtime.

## Roadmap

- **Phase 1** ✅ Jira issue fetch + related issue search + AI summary
- **Phase 2** ✅ Slack discussion search
- **Phase 3** ✅ GitHub issues search — match escalation to filed bugs, offer to file new ones
- **Phase 4** ✅ E2E testing with real fixtures and CI via GitHub Actions
