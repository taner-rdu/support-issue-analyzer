# Support Issue Analyzer

An agentic Claude Code toolkit that turns a Jira support escalation into a fully-researched developer briefing — correlating Jira, Slack, and GitHub in one command.

When a customer issue gets escalated, developers waste time hunting across Jira, Slack, and GitHub just to figure out if this has happened before. This project automates that legwork: it fetches the Jira issue, correlates it against related Jira tickets, Slack threads, and GitHub issues, and writes out a structured markdown briefing with AI-generated root cause analysis — ready for a developer to act on immediately.

It's built as a small suite of Claude Code skills backed by MCP servers, with a custom-built validator server and an end-to-end test suite that exercises the whole pipeline against real Jira/Slack/GitHub fixtures.

## How It Works

```
/support "PARLE-1"
```

Claude Code will:

1. Fetch the Jira issue via the Atlassian MCP server
2. Search for related issues in the same project via JQL keyword search
3. Search Slack for related discussions via the Slack MCP server
4. Search GitHub for related issues via the GitHub MCP server, correlating on symptom and root cause rather than shared keywords — and offer to file a new issue if nothing matches
5. Generate a structured summary with AI-powered root cause analysis
6. Write the output to `issues/PARLE-1/summary.md`

Each summary includes issue metadata, the full description, AI-generated analysis (likely root cause, impact, investigation steps), tables of related Jira/Slack/GitHub findings, existing comments, and an append-only update log — so re-running `/support` on an issue that's since changed status or picked up new comments produces a diff-aware update instead of a duplicate report.

```
/validate "PARLE-1"
```

A second skill, backed by a custom `summary-validator` MCP server, checks a generated summary for structural completeness (all required sections present) and reports word count. It's also used as the pass/fail gate in the e2e test suite.

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
| `support-analyzer/github-test-issue-repo` | GitHub repo to search/file issues against, and used for e2e test fixtures (e.g. `your-org/your-repo`) |

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

The e2e test creates real Jira, GitHub, and Slack fixtures (an issue, two candidate GitHub issues — one related, one not — and two Slack messages), runs the `/support` skill against them, then validates the output via the `/validate` skill's `summary-validator` MCP server, which checks that the generated summary has all required sections.

```bash
uv run pytest tests/ -v
```

CI runs on every pull request (and on demand via manual dispatch) using GitHub Actions with OIDC authentication to AWS — no long-lived credentials stored in GitHub. All secrets are fetched from AWS Secrets Manager at runtime. The pipeline also runs markdown linting and secret scanning (TruffleHog) on every PR.

## Tech Stack

Python · [Model Context Protocol](https://modelcontextprotocol.io/) (Atlassian, Slack, GitHub MCP servers + a custom-built validator server) · Claude Code skills · AWS Secrets Manager · GitHub Actions (OIDC) · pytest

## Roadmap

- **Phase 1** ✅ Jira issue fetch + related issue search + AI summary
- **Phase 2** ✅ Slack discussion search
- **Phase 3** ✅ GitHub issues search — match escalation to filed bugs, offer to file new ones
- **Phase 4** ✅ E2E testing with real fixtures and CI via GitHub Actions
- **Phase 5** Analyze local code base
