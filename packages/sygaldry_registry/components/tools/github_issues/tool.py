"""GitHub Issues Tool for managing and searching GitHub issues.

This tool provides functions to search, create, update, and manage GitHub issues
using the GitHub REST API. Requires a GitHub personal access token.
"""

from __future__ import annotations

import os
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class GitHubLabel(BaseModel):
    """GitHub issue label."""

    name: str = Field(..., description="Label name")
    color: str = Field(..., description="Label color (hex)")
    description: Optional[str] = Field(None, description="Label description")


class GitHubUser(BaseModel):
    """GitHub user information."""

    login: str = Field(..., description="GitHub username")
    id: int = Field(..., description="User ID")
    avatar_url: str = Field(..., description="Avatar URL")
    html_url: str = Field(..., description="Profile URL")


class GitHubIssue(BaseModel):
    """GitHub issue representation."""

    number: int = Field(..., description="Issue number")
    title: str = Field(..., description="Issue title")
    body: Optional[str] = Field(None, description="Issue body/description")
    state: Literal["open", "closed"] = Field(..., description="Issue state")
    labels: list[GitHubLabel] = Field(default_factory=list, description="Issue labels")
    assignees: list[GitHubUser] = Field(default_factory=list, description="Assigned users")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    closed_at: Optional[str] = Field(None, description="Close timestamp")
    html_url: str = Field(..., description="Issue URL")
    user: GitHubUser = Field(..., description="Issue creator")
    comments: int = Field(..., description="Number of comments")
    milestone: Optional[str] = Field(None, description="Milestone title")


class GitHubComment(BaseModel):
    """GitHub issue comment."""

    id: int = Field(..., description="Comment ID")
    body: str = Field(..., description="Comment text")
    user: GitHubUser = Field(..., description="Comment author")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    html_url: str = Field(..., description="Comment URL")


def _get_github_headers() -> dict[str, str]:
    """Get headers for GitHub API requests."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Sygaldry-GitHub-Tool"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def search_issues(
    repo: str,
    query: str = "",
    state: Literal["open", "closed", "all"] = "open",
    labels: Optional[list[str]] = None,
    assignee: Optional[str] = None,
    creator: Optional[str] = None,
    max_results: int = 30,
    sort: Literal["created", "updated", "comments"] = "created",
    direction: Literal["asc", "desc"] = "desc"
) -> list[GitHubIssue]:
    """
    Search for issues in a GitHub repository.

    Args:
        repo: Repository in format "owner/repo" (e.g., "facebook/react")
        query: Additional search query (GitHub search syntax)
        state: Filter by state (open, closed, all)
        labels: Filter by labels
        assignee: Filter by assignee username
        creator: Filter by creator username
        max_results: Maximum number of results to return
        sort: Sort field
        direction: Sort direction

    Returns:
        List of GitHubIssue objects

    Example:
        ```python
        # Search for open bugs
        issues = search_issues(
            repo="facebook/react",
            query="is:open label:bug",
            max_results=10
        )

        # Search by creator
        issues = search_issues(
            repo="microsoft/vscode",
            creator="octocat",
            state="all"
        )
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for github_issues tool. Install with: pip install httpx")

    # Build query parameters
    params = {
        "state": state,
        "per_page": min(max_results, 100),
        "sort": sort,
        "direction": direction
    }

    if labels:
        params["labels"] = ",".join(labels)
    if assignee:
        params["assignee"] = assignee
    if creator:
        params["creator"] = creator

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = _get_github_headers()

    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    # Convert to GitHubIssue objects
    issues = []
    for item in data[:max_results]:
        # Skip pull requests (they appear in issues API)
        if "pull_request" in item:
            continue

        issue = GitHubIssue(
            number=item["number"],
            title=item["title"],
            body=item.get("body"),
            state=item["state"],
            labels=[
                GitHubLabel(
                    name=label["name"],
                    color=label["color"],
                    description=label.get("description")
                )
                for label in item.get("labels", [])
            ],
            assignees=[
                GitHubUser(
                    login=assignee["login"],
                    id=assignee["id"],
                    avatar_url=assignee["avatar_url"],
                    html_url=assignee["html_url"]
                )
                for assignee in item.get("assignees", [])
            ],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            closed_at=item.get("closed_at"),
            html_url=item["html_url"],
            user=GitHubUser(
                login=item["user"]["login"],
                id=item["user"]["id"],
                avatar_url=item["user"]["avatar_url"],
                html_url=item["user"]["html_url"]
            ),
            comments=item.get("comments", 0),
            milestone=item["milestone"]["title"] if item.get("milestone") else None
        )
        issues.append(issue)

    return issues


def get_issue(repo: str, issue_number: int) -> GitHubIssue:
    """
    Get a specific issue by number.

    Args:
        repo: Repository in format "owner/repo"
        issue_number: Issue number

    Returns:
        GitHubIssue object

    Example:
        ```python
        issue = get_issue("facebook/react", 12345)
        print(f"Title: {issue.title}")
        print(f"State: {issue.state}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for github_issues tool. Install with: pip install httpx")

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = _get_github_headers()

    with httpx.Client() as client:
        response = client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        item = response.json()

    return GitHubIssue(
        number=item["number"],
        title=item["title"],
        body=item.get("body"),
        state=item["state"],
        labels=[
            GitHubLabel(
                name=label["name"],
                color=label["color"],
                description=label.get("description")
            )
            for label in item.get("labels", [])
        ],
        assignees=[
            GitHubUser(
                login=assignee["login"],
                id=assignee["id"],
                avatar_url=assignee["avatar_url"],
                html_url=assignee["html_url"]
            )
            for assignee in item.get("assignees", [])
        ],
        created_at=item["created_at"],
        updated_at=item["updated_at"],
        closed_at=item.get("closed_at"),
        html_url=item["html_url"],
        user=GitHubUser(
            login=item["user"]["login"],
            id=item["user"]["id"],
            avatar_url=item["user"]["avatar_url"],
            html_url=item["user"]["html_url"]
        ),
        comments=item.get("comments", 0),
        milestone=item["milestone"]["title"] if item.get("milestone") else None
    )


def create_issue(
    repo: str,
    title: str,
    body: Optional[str] = None,
    labels: Optional[list[str]] = None,
    assignees: Optional[list[str]] = None,
    milestone: Optional[int] = None
) -> GitHubIssue:
    """
    Create a new issue in a repository.

    Args:
        repo: Repository in format "owner/repo"
        title: Issue title
        body: Issue description/body
        labels: List of label names to apply
        assignees: List of usernames to assign
        milestone: Milestone number

    Returns:
        Created GitHubIssue object

    Example:
        ```python
        issue = create_issue(
            repo="myorg/myrepo",
            title="Bug: Login fails on mobile",
            body="Detailed description of the bug...",
            labels=["bug", "mobile"],
            assignees=["developer1"]
        )
        print(f"Created issue #{issue.number}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for github_issues tool. Install with: pip install httpx")

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = _get_github_headers()

    payload = {"title": title}
    if body:
        payload["body"] = body
    if labels:
        payload["labels"] = labels
    if assignees:
        payload["assignees"] = assignees
    if milestone:
        payload["milestone"] = milestone

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        item = response.json()

    return GitHubIssue(
        number=item["number"],
        title=item["title"],
        body=item.get("body"),
        state=item["state"],
        labels=[
            GitHubLabel(name=label["name"], color=label["color"], description=label.get("description"))
            for label in item.get("labels", [])
        ],
        assignees=[
            GitHubUser(login=a["login"], id=a["id"], avatar_url=a["avatar_url"], html_url=a["html_url"])
            for a in item.get("assignees", [])
        ],
        created_at=item["created_at"],
        updated_at=item["updated_at"],
        closed_at=item.get("closed_at"),
        html_url=item["html_url"],
        user=GitHubUser(
            login=item["user"]["login"],
            id=item["user"]["id"],
            avatar_url=item["user"]["avatar_url"],
            html_url=item["user"]["html_url"]
        ),
        comments=item.get("comments", 0),
        milestone=item["milestone"]["title"] if item.get("milestone") else None
    )


def update_issue(
    repo: str,
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    state: Optional[Literal["open", "closed"]] = None,
    labels: Optional[list[str]] = None,
    assignees: Optional[list[str]] = None
) -> GitHubIssue:
    """
    Update an existing issue.

    Args:
        repo: Repository in format "owner/repo"
        issue_number: Issue number to update
        title: New title (optional)
        body: New body (optional)
        state: New state (optional)
        labels: New labels (replaces existing)
        assignees: New assignees (replaces existing)

    Returns:
        Updated GitHubIssue object
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for github_issues tool. Install with: pip install httpx")

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = _get_github_headers()

    payload = {}
    if title is not None:
        payload["title"] = title
    if body is not None:
        payload["body"] = body
    if state is not None:
        payload["state"] = state
    if labels is not None:
        payload["labels"] = labels
    if assignees is not None:
        payload["assignees"] = assignees

    with httpx.Client() as client:
        response = client.patch(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        item = response.json()

    return get_issue(repo, issue_number)


def list_issue_comments(repo: str, issue_number: int, max_results: int = 30) -> list[GitHubComment]:
    """
    List comments on an issue.

    Args:
        repo: Repository in format "owner/repo"
        issue_number: Issue number
        max_results: Maximum number of comments to return

    Returns:
        List of GitHubComment objects
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for github_issues tool. Install with: pip install httpx")

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = _get_github_headers()
    params = {"per_page": min(max_results, 100)}

    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    comments = []
    for item in data[:max_results]:
        comment = GitHubComment(
            id=item["id"],
            body=item["body"],
            user=GitHubUser(
                login=item["user"]["login"],
                id=item["user"]["id"],
                avatar_url=item["user"]["avatar_url"],
                html_url=item["user"]["html_url"]
            ),
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            html_url=item["html_url"]
        )
        comments.append(comment)

    return comments


def add_issue_comment(repo: str, issue_number: int, body: str) -> GitHubComment:
    """
    Add a comment to an issue.

    Args:
        repo: Repository in format "owner/repo"
        issue_number: Issue number
        body: Comment text

    Returns:
        Created GitHubComment object
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for github_issues tool. Install with: pip install httpx")

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = _get_github_headers()
    payload = {"body": body}

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        item = response.json()

    return GitHubComment(
        id=item["id"],
        body=item["body"],
        user=GitHubUser(
            login=item["user"]["login"],
            id=item["user"]["id"],
            avatar_url=item["user"]["avatar_url"],
            html_url=item["user"]["html_url"]
        ),
        created_at=item["created_at"],
        updated_at=item["updated_at"],
        html_url=item["html_url"]
    )
