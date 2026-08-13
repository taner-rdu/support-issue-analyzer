import httpx

from config import get_secret

JIRA_URL = get_secret("support-analyzer/jira-url")
JIRA_EMAIL = get_secret("support-analyzer/jira-username")
JIRA_TOKEN = get_secret("support-analyzer/jira-token")
JIRA_PROJECT_KEY = get_secret("support-analyzer/jira-project-key")


def create_jira_issue(summary: str, description: str) -> str:
    resp = httpx.post(
        f"{JIRA_URL}/rest/api/3/issue",
        auth=(JIRA_EMAIL, JIRA_TOKEN),
        json={
            "fields": {
                "project": {"key": JIRA_PROJECT_KEY},
                "summary": summary,
                "issuetype": {"name": "Bug"},
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}],
                        }
                    ],
                },
            }
        },
    )
    resp.raise_for_status()
    return resp.json()["key"]


def delete_jira_issue(issue_key: str) -> None:
    resp = httpx.delete(
        f"{JIRA_URL}/rest/api/3/issue/{issue_key}",
        auth=(JIRA_EMAIL, JIRA_TOKEN),
    )
    resp.raise_for_status()
