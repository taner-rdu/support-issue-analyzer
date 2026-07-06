import asyncio
import importlib.util
import subprocess
from pathlib import Path

from tests.fixtures.jira_fixtures import create_jira_issue, delete_jira_issue
from tests.fixtures.github_fixtures import create_github_issue, delete_github_issue
from tests.fixtures.slack_fixtures import post_slack_message, delete_slack_message

# mcp-servers/summary-validator.py isn't an importable package path, so load it by file
_spec = importlib.util.spec_from_file_location(
    "summary_validator",
    Path(__file__).resolve().parent.parent / "mcp-servers" / "summary-validator.py",
)
summary_validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(summary_validator)


JIRA_SUMMARY = "Translation fails for long paragraphs in DeepL integration"

JIRA_DESCRIPTION = (
    "Users report that submitting long blocks of text for translation "
    "causes the request to hang and eventually time out. Short sentences "
    "translate fine, but anything over a few hundred words consistently "
    "fails. No error is shown to the user — the UI just spins indefinitely."
)

GITHUB_RELATED_TITLE = "API requests hang when payload exceeds size threshold"

GITHUB_RELATED_BODY = (
    "Noticed that calls to the external translation provider never "
    "return when the input is large. Smaller inputs work as expected. "
    "Suspect we're hitting a timeout or size limit on the provider side "
    "and not handling it gracefully — the request just hangs instead of "
    "failing fast."
)

GITHUB_UNRELATED_TITLE = "Google OAuth redirect loop on logout"

GITHUB_UNRELATED_BODY = (
    "After logging out, users are redirected back to the Google OAuth "
    "consent screen and then immediately back to the logout page, "
    "repeating indefinitely. Happens in Chrome and Firefox. Workaround "
    "is clearing cookies manually."
)

SLACK_UNRELATED_MESSAGE = (
    "anyone know why the staging deploy is stuck on the auth-service "
    "build? been sitting at 80% for like 20 minutes"
)


def slack_related_message(jira_key: str) -> str:
    return (
        f"hey did anyone look into {jira_key} yet? users are reporting "
        "translations just hang forever on longer text, seems pretty bad"
    )


def test_support_skill_correlates_related_issues():
    jira_key = create_jira_issue(summary=JIRA_SUMMARY, description=JIRA_DESCRIPTION)

    github_related = create_github_issue(title=GITHUB_RELATED_TITLE, body=GITHUB_RELATED_BODY)
    github_unrelated = create_github_issue(title=GITHUB_UNRELATED_TITLE, body=GITHUB_UNRELATED_BODY)

    slack_related = post_slack_message(text=slack_related_message(jira_key))
    slack_unrelated = post_slack_message(text=SLACK_UNRELATED_MESSAGE)

    try:
        result = subprocess.run(
            ["claude", "-p", f"/support {jira_key}", "--dangerously-skip-permissions"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Support skill failed:\n{result.stderr}"

        data = asyncio.run(summary_validator.validate_summary(jira_key))
        assert data["valid"] is True, f"Summary invalid: {data.get('missing_sections') or data.get('error')}"

    finally:
        delete_jira_issue(jira_key)
        delete_github_issue(github_related["node_id"])
        delete_github_issue(github_unrelated["node_id"])
        delete_slack_message(slack_related["channel"], slack_related["ts"])
        delete_slack_message(slack_unrelated["channel"], slack_unrelated["ts"])