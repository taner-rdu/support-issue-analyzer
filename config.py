import os

from dotenv import load_dotenv

load_dotenv()

# Maps the old AWS Secrets Manager paths to the environment variables that
# now hold the same values (local .env file, or GitHub Actions secrets in CI).
_ENV_VAR_MAP = {
    "support-analyzer/anthropic-api-key": "ANTHROPIC_API_KEY",
    "support-analyzer/jira-url": "JIRA_URL",
    "support-analyzer/jira-username": "JIRA_USERNAME",
    "support-analyzer/jira-token": "JIRA_API_TOKEN",
    "support-analyzer/jira-project-key": "JIRA_PROJECT_KEY",
    "support-analyzer/slack-bot-token": "SLACK_BOT_TOKEN",
    "support-analyzer/slack-team-id": "SLACK_TEAM_ID",
    "support-analyzer/slack-channel": "SLACK_CHANNEL",
    "support-analyzer/github-token": "SUPPORT_GITHUB_TOKEN",
    "support-analyzer/github-test-issue-repo": "GITHUB_TEST_ISSUE_REPO",
}


def get_secret(name: str) -> str:
    env_var = _ENV_VAR_MAP.get(name)
    if env_var is None:
        raise KeyError(f"No environment variable mapped for secret {name!r}")

    value = os.environ.get(env_var)
    if not value:
        raise KeyError(f"Missing required environment variable: {env_var}")

    return value
