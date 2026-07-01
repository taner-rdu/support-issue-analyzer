import json

from aws import get_secret

# To generate .mcp.json file -> uv run python generate_mcp_config.py

config = {
    "mcpServers": {
        "atlassian": {
            "type": "stdio",
            "command": "uvx",
            "args": ["mcp-atlassian"],
            "env": {
                "JIRA_URL": get_secret("support-analyzer/jira-url"),
                "JIRA_USERNAME": get_secret("support-analyzer/jira-username"),
                "JIRA_API_TOKEN": get_secret("support-analyzer/jira-token"),
            },
        },
        "slack": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": {
                "SLACK_BOT_TOKEN": get_secret("support-analyzer/slack-bot-token"),
                "SLACK_TEAM_ID": get_secret("support-analyzer/slack-team-id"),
            },
        },
        "github": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_TOKEN": get_secret("support-analyzer/github-token"),
            },
        },
        "summary-validator": {
            "type": "stdio",
            "command": "uv",
            "args": ["run", "python", "mcp-servers/summary-validator.py"],
        },
    }
}

with open(".mcp.json", "w") as f:
    json.dump(config, f, indent=2)
