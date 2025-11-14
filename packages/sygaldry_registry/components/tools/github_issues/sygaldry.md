# GitHub Issues Tool

## Overview

GitHub Issues management tool for searching, creating, updating, and managing issues via the GitHub REST API.

## Features

- Search issues with advanced filters
- Get issue details
- Create new issues
- Update existing issues
- List and add comments
- Support for labels, assignees, milestones

## Installation

```bash
sygaldry add github_issues
pip install httpx
```

## Authentication

Set your GitHub personal access token:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

## Quick Start

```python
from github_issues import search_issues, create_issue

# Search for bugs
issues = search_issues(
    repo="facebook/react",
    labels=["bug"],
    state="open",
    max_results=10
)

# Create issue
issue = create_issue(
    repo="myorg/myrepo",
    title="Bug: Login fails",
    body="Description...",
    labels=["bug"]
)
```

## Functions

### search_issues()
Search for issues with filters.

### get_issue()
Get specific issue by number.

### create_issue()
Create a new issue.

### update_issue()
Update existing issue.

### list_issue_comments()
List comments on an issue.

### add_issue_comment()
Add comment to an issue.

## License

MIT
