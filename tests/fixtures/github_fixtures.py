import httpx

from config import get_secret

GITHUB_TOKEN = get_secret("SUPPORT_GITHUB_TOKEN")
GITHUB_REPO = get_secret("GITHUB_TEST_ISSUE_REPO")
GITHUB_API = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def create_github_issue(title: str, body: str) -> dict:
    resp = httpx.post(
        f"{GITHUB_API}/repos/{GITHUB_REPO}/issues",
        headers=HEADERS,
        json={"title": title, "body": body},
    )
    resp.raise_for_status()
    data = resp.json()
    return {"number": data["number"], "node_id": data["node_id"]}


def delete_github_issue(node_id: str) -> None:
    query = """
    mutation($issueId: ID!) {
      deleteIssue(input: { issueId: $issueId }) {
        clientMutationId
      }
    }
    """
    resp = httpx.post(
        f"{GITHUB_API}/graphql",
        headers=HEADERS,
        json={"query": query, "variables": {"issueId": node_id}},
    )
    resp.raise_for_status()
    result = resp.json()
    if "errors" in result:
        raise RuntimeError(f"GraphQL deleteIssue failed: {result['errors']}")
