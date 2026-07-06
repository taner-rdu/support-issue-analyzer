import asyncio
import logging
import subprocess
import time

from mcp_servers.summary_validator import validate_summary
from tests.fixtures.jira_fixtures import create_jira_issue, delete_jira_issue
from tests.fixtures.github_fixtures import create_github_issue, delete_github_issue
from tests.fixtures.slack_fixtures import post_slack_message, delete_slack_message

logger = logging.getLogger(__name__)


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

# Written to read like an organic engineer report that predates the ticket:
# no issue key, symptom keywords only. If it restates the ticket or is posted
# after it, the analyzer flags it as seed data instead of corroboration.
SLACK_RELATED_MESSAGE = (
    "seeing a bunch of user reports that translation just spins forever "
    "on long paragraphs — short stuff works fine. anyone else seeing "
    "DeepL requests hang on big payloads?"
)

SLACK_UNRELATED_MESSAGE = (
    "anyone know why the staging deploy is stuck on the auth-service "
    "build? been sitting at 80% for like 20 minutes"
)


def test_support_skill_correlates_related_issues():
    # Slack messages go out first so the "discussion" predates the ticket
    slack_related = post_slack_message(text=SLACK_RELATED_MESSAGE, username="alex.chen")
    slack_unrelated = post_slack_message(text=SLACK_UNRELATED_MESSAGE, username="priya.nair")
    logger.info(
        f"Posted Slack messages: related ts={slack_related['ts']}, "
        f"unrelated ts={slack_unrelated['ts']} in channel {slack_related['channel']}"
    )

    jira_key = create_jira_issue(summary=JIRA_SUMMARY, description=JIRA_DESCRIPTION)
    logger.info(f"Created Jira issue {jira_key}")

    github_related = create_github_issue(title=GITHUB_RELATED_TITLE, body=GITHUB_RELATED_BODY)
    github_unrelated = create_github_issue(title=GITHUB_UNRELATED_TITLE, body=GITHUB_UNRELATED_BODY)
    logger.info(
        f"Created GitHub issues: related #{github_related['number']}, "
        f"unrelated #{github_unrelated['number']}"
    )

    try:
        logger.info(f"Running /support {jira_key} via claude CLI (this can take a few minutes)")
        start = time.monotonic()
        result = subprocess.run(
            ["claude", "-p", f"/support {jira_key}", "--dangerously-skip-permissions"],
            capture_output=True,
            text=True,
        )
        logger.info(
            f"claude exited with code {result.returncode} after {time.monotonic() - start:.0f}s"
        )
        logger.info(f"claude output:\n{result.stdout.strip()}")
        if result.stderr.strip():
            logger.warning(f"claude stderr:\n{result.stderr.strip()}")
        assert result.returncode == 0, f"Support skill failed:\n{result.stderr}"

        data = asyncio.run(validate_summary(jira_key))
        logger.info(
            f"Validation result: valid={data.get('valid')}, "
            f"word_count={data.get('word_count')}, "
            f"missing_sections={data.get('missing_sections')}"
        )
        assert data["valid"] is True, f"Summary invalid: {data.get('missing_sections') or data.get('error')}"

    finally:
        logger.info(f"Cleaning up fixtures for {jira_key}")
        delete_jira_issue(jira_key)
        delete_github_issue(github_related["node_id"])
        delete_github_issue(github_unrelated["node_id"])
        delete_slack_message(slack_related["channel"], slack_related["ts"])
        delete_slack_message(slack_unrelated["channel"], slack_unrelated["ts"])
        logger.info("Cleanup complete")