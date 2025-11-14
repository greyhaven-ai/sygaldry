"""Helpdesk Integration Tool for managing Zendesk support tickets.

This tool provides functions to search, create, update, and manage Zendesk support tickets
using the Zendesk REST API v2. Requires Zendesk API credentials.
"""

from __future__ import annotations

import os
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional
from base64 import b64encode

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class TicketRequester(BaseModel):
    """Zendesk ticket requester/user information."""

    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")


class TicketStatus(BaseModel):
    """Zendesk ticket status representation."""

    value: Literal["new", "open", "pending", "hold", "solved", "closed"] = Field(
        ..., description="Ticket status value"
    )
    label: str = Field(..., description="Human-readable status label")


class Comment(BaseModel):
    """Zendesk ticket comment."""

    id: int = Field(..., description="Comment ID")
    body: str = Field(..., description="Comment text")
    author_id: int = Field(..., description="Comment author ID")
    created_at: str = Field(..., description="Creation timestamp")
    public: bool = Field(..., description="Whether comment is public")


class Ticket(BaseModel):
    """Zendesk ticket representation."""

    id: int = Field(..., description="Ticket ID")
    subject: str = Field(..., description="Ticket subject")
    description: Optional[str] = Field(None, description="Ticket description")
    status: Literal["new", "open", "pending", "hold", "solved", "closed"] = Field(
        ..., description="Ticket status"
    )
    priority: Literal["low", "normal", "high", "urgent"] = Field(
        ..., description="Ticket priority"
    )
    ticket_type: Optional[Literal["problem", "incident", "question", "task"]] = Field(
        None, description="Ticket type"
    )
    tags: list[str] = Field(default_factory=list, description="Ticket tags")
    requester_id: int = Field(..., description="Requester user ID")
    assignee_id: Optional[int] = Field(None, description="Assignee user ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    url: str = Field(..., description="Ticket URL")


def _get_zendesk_config() -> tuple[str, str]:
    """
    Get Zendesk API configuration from environment variables.

    Returns:
        Tuple of (base_url, auth_header)

    Raises:
        ValueError: If required environment variables are not set
    """
    subdomain = os.getenv("ZENDESK_SUBDOMAIN")
    email = os.getenv("ZENDESK_EMAIL")
    api_token = os.getenv("ZENDESK_API_TOKEN")

    if not subdomain:
        raise ValueError("ZENDESK_SUBDOMAIN environment variable is required")
    if not email:
        raise ValueError("ZENDESK_EMAIL environment variable is required")
    if not api_token:
        raise ValueError("ZENDESK_API_TOKEN environment variable is required")

    base_url = f"https://{subdomain}.zendesk.com/api/v2"

    # Zendesk uses email/token authentication
    credentials = f"{email}/token:{api_token}"
    encoded_credentials = b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"

    return base_url, auth_header


def _get_headers(auth_header: str) -> dict[str, str]:
    """Get headers for Zendesk API requests."""
    return {
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def search_tickets(
    query: str = "",
    status: Literal["new", "open", "pending", "hold", "solved", "closed", "all"] = "open",
    priority: Optional[Literal["low", "normal", "high", "urgent"]] = None,
    ticket_type: Optional[Literal["problem", "incident", "question", "task"]] = None,
    tags: Optional[list[str]] = None,
    max_results: int = 30,
    sort_by: Literal["created_at", "updated_at", "priority", "status"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
) -> list[Ticket]:
    """
    Search for tickets in Zendesk.

    Args:
        query: Search query text (searches subject and description)
        status: Filter by ticket status
        priority: Filter by priority level
        ticket_type: Filter by ticket type
        tags: Filter by tags (tickets must have all specified tags)
        max_results: Maximum number of results to return
        sort_by: Field to sort by
        sort_order: Sort order (ascending or descending)

    Returns:
        List of Ticket objects

    Example:
        ```python
        # Search for open high-priority tickets
        tickets = search_tickets(
            query="login issue",
            status="open",
            priority="high",
            max_results=10
        )

        # Search by tags
        tickets = search_tickets(
            tags=["bug", "customer-reported"],
            status="all"
        )
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError(
            "httpx is required for helpdesk_integration tool. Install with: pip install httpx"
        )

    base_url, auth_header = _get_zendesk_config()
    headers = _get_headers(auth_header)

    # Build search query
    search_parts = []

    if query:
        search_parts.append(f'"{query}"')

    if status != "all":
        search_parts.append(f"status:{status}")

    if priority:
        search_parts.append(f"priority:{priority}")

    if ticket_type:
        search_parts.append(f"type:{ticket_type}")

    if tags:
        for tag in tags:
            search_parts.append(f"tags:{tag}")

    # Combine search parts
    search_query = " ".join(search_parts) if search_parts else "type:ticket"

    # Build request URL
    url = f"{base_url}/search.json"
    params = {
        "query": search_query,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    # Convert to Ticket objects
    tickets = []
    for item in data.get("results", [])[:max_results]:
        # Only process actual tickets (search can return other objects)
        if item.get("result_type") != "ticket":
            continue

        ticket = Ticket(
            id=item["id"],
            subject=item.get("subject", ""),
            description=item.get("description"),
            status=item["status"],
            priority=item.get("priority", "normal"),
            ticket_type=item.get("type"),
            tags=item.get("tags", []),
            requester_id=item["requester_id"],
            assignee_id=item.get("assignee_id"),
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            url=item["url"],
        )
        tickets.append(ticket)

    return tickets


def get_ticket(ticket_id: int) -> Ticket:
    """
    Get a specific ticket by ID.

    Args:
        ticket_id: Ticket ID

    Returns:
        Ticket object

    Example:
        ```python
        ticket = get_ticket(12345)
        print(f"Subject: {ticket.subject}")
        print(f"Status: {ticket.status}")
        print(f"Priority: {ticket.priority}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError(
            "httpx is required for helpdesk_integration tool. Install with: pip install httpx"
        )

    base_url, auth_header = _get_zendesk_config()
    headers = _get_headers(auth_header)

    url = f"{base_url}/tickets/{ticket_id}.json"

    with httpx.Client() as client:
        response = client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    item = data["ticket"]
    return Ticket(
        id=item["id"],
        subject=item.get("subject", ""),
        description=item.get("description"),
        status=item["status"],
        priority=item.get("priority", "normal"),
        ticket_type=item.get("type"),
        tags=item.get("tags", []),
        requester_id=item["requester_id"],
        assignee_id=item.get("assignee_id"),
        created_at=item["created_at"],
        updated_at=item["updated_at"],
        url=item["url"],
    )


def create_ticket(
    subject: str,
    description: str,
    requester_name: Optional[str] = None,
    requester_email: Optional[str] = None,
    priority: Literal["low", "normal", "high", "urgent"] = "normal",
    ticket_type: Optional[Literal["problem", "incident", "question", "task"]] = None,
    tags: Optional[list[str]] = None,
    assignee_id: Optional[int] = None,
) -> Ticket:
    """
    Create a new ticket in Zendesk.

    Args:
        subject: Ticket subject/title
        description: Ticket description/body
        requester_name: Name of the person requesting support
        requester_email: Email of the requester (required if requester not authenticated)
        priority: Ticket priority level
        ticket_type: Type of ticket
        tags: List of tags to apply
        assignee_id: ID of user to assign the ticket to

    Returns:
        Created Ticket object

    Example:
        ```python
        ticket = create_ticket(
            subject="Cannot login to account",
            description="User reports unable to login after password reset",
            requester_email="user@example.com",
            priority="high",
            ticket_type="problem",
            tags=["login", "authentication"]
        )
        print(f"Created ticket #{ticket.id}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError(
            "httpx is required for helpdesk_integration tool. Install with: pip install httpx"
        )

    base_url, auth_header = _get_zendesk_config()
    headers = _get_headers(auth_header)

    url = f"{base_url}/tickets.json"

    # Build ticket payload
    ticket_data = {
        "subject": subject,
        "comment": {"body": description},
        "priority": priority,
    }

    if ticket_type:
        ticket_data["type"] = ticket_type

    if tags:
        ticket_data["tags"] = tags

    if assignee_id:
        ticket_data["assignee_id"] = assignee_id

    # Set requester
    if requester_email:
        ticket_data["requester"] = {"email": requester_email}
        if requester_name:
            ticket_data["requester"]["name"] = requester_name

    payload = {"ticket": ticket_data}

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    item = data["ticket"]
    return Ticket(
        id=item["id"],
        subject=item.get("subject", ""),
        description=item.get("description"),
        status=item["status"],
        priority=item.get("priority", "normal"),
        ticket_type=item.get("type"),
        tags=item.get("tags", []),
        requester_id=item["requester_id"],
        assignee_id=item.get("assignee_id"),
        created_at=item["created_at"],
        updated_at=item["updated_at"],
        url=item["url"],
    )


def update_ticket(
    ticket_id: int,
    status: Optional[Literal["new", "open", "pending", "hold", "solved", "closed"]] = None,
    priority: Optional[Literal["low", "normal", "high", "urgent"]] = None,
    comment: Optional[str] = None,
    tags: Optional[list[str]] = None,
    assignee_id: Optional[int] = None,
    public_comment: bool = True,
) -> Ticket:
    """
    Update an existing ticket.

    Args:
        ticket_id: Ticket ID to update
        status: New status
        priority: New priority
        comment: Comment to add to the ticket
        tags: New tags (replaces existing tags)
        assignee_id: New assignee user ID
        public_comment: Whether the comment is public (visible to requester)

    Returns:
        Updated Ticket object

    Example:
        ```python
        # Update status and add comment
        ticket = update_ticket(
            ticket_id=12345,
            status="pending",
            comment="Waiting for more information from user",
            public_comment=True
        )

        # Assign ticket and change priority
        ticket = update_ticket(
            ticket_id=12345,
            assignee_id=67890,
            priority="urgent"
        )
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError(
            "httpx is required for helpdesk_integration tool. Install with: pip install httpx"
        )

    base_url, auth_header = _get_zendesk_config()
    headers = _get_headers(auth_header)

    url = f"{base_url}/tickets/{ticket_id}.json"

    # Build update payload
    ticket_data = {}

    if status is not None:
        ticket_data["status"] = status

    if priority is not None:
        ticket_data["priority"] = priority

    if tags is not None:
        ticket_data["tags"] = tags

    if assignee_id is not None:
        ticket_data["assignee_id"] = assignee_id

    if comment is not None:
        ticket_data["comment"] = {"body": comment, "public": public_comment}

    payload = {"ticket": ticket_data}

    with httpx.Client() as client:
        response = client.put(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    item = data["ticket"]
    return Ticket(
        id=item["id"],
        subject=item.get("subject", ""),
        description=item.get("description"),
        status=item["status"],
        priority=item.get("priority", "normal"),
        ticket_type=item.get("type"),
        tags=item.get("tags", []),
        requester_id=item["requester_id"],
        assignee_id=item.get("assignee_id"),
        created_at=item["created_at"],
        updated_at=item["updated_at"],
        url=item["url"],
    )


def list_ticket_comments(ticket_id: int, max_results: int = 30) -> list[Comment]:
    """
    List comments on a ticket.

    Args:
        ticket_id: Ticket ID
        max_results: Maximum number of comments to return

    Returns:
        List of Comment objects

    Example:
        ```python
        comments = list_ticket_comments(ticket_id=12345)
        for comment in comments:
            print(f"Author {comment.author_id}: {comment.body}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError(
            "httpx is required for helpdesk_integration tool. Install with: pip install httpx"
        )

    base_url, auth_header = _get_zendesk_config()
    headers = _get_headers(auth_header)

    url = f"{base_url}/tickets/{ticket_id}/comments.json"
    params = {"per_page": min(max_results, 100)}

    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    comments = []
    for item in data.get("comments", [])[:max_results]:
        comment = Comment(
            id=item["id"],
            body=item["body"],
            author_id=item["author_id"],
            created_at=item["created_at"],
            public=item.get("public", True),
        )
        comments.append(comment)

    return comments


def add_ticket_comment(
    ticket_id: int, body: str, public: bool = True
) -> Comment:
    """
    Add a comment to a ticket.

    Args:
        ticket_id: Ticket ID
        body: Comment text
        public: Whether comment is public (visible to requester)

    Returns:
        Created Comment object

    Example:
        ```python
        comment = add_ticket_comment(
            ticket_id=12345,
            body="I've escalated this to our engineering team.",
            public=True
        )
        print(f"Added comment #{comment.id}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError(
            "httpx is required for helpdesk_integration tool. Install with: pip install httpx"
        )

    base_url, auth_header = _get_zendesk_config()
    headers = _get_headers(auth_header)

    url = f"{base_url}/tickets/{ticket_id}.json"
    payload = {"ticket": {"comment": {"body": body, "public": public}}}

    with httpx.Client() as client:
        response = client.put(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        # Note: Zendesk doesn't return the comment in the response,
        # so we need to fetch the comments to get the latest one
        comments = list_ticket_comments(ticket_id, max_results=1)
        if comments:
            return comments[0]

    # Fallback if no comments found
    return Comment(
        id=0,
        body=body,
        author_id=0,
        created_at=datetime.utcnow().isoformat(),
        public=public,
    )


def add_ticket_tags(ticket_id: int, tags: list[str]) -> Ticket:
    """
    Add tags to a ticket without replacing existing tags.

    Args:
        ticket_id: Ticket ID
        tags: List of tags to add

    Returns:
        Updated Ticket object

    Example:
        ```python
        ticket = add_ticket_tags(
            ticket_id=12345,
            tags=["escalated", "vip-customer"]
        )
        print(f"Tags: {ticket.tags}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError(
            "httpx is required for helpdesk_integration tool. Install with: pip install httpx"
        )

    # First get the current ticket to retrieve existing tags
    current_ticket = get_ticket(ticket_id)
    existing_tags = set(current_ticket.tags)
    new_tags = existing_tags.union(set(tags))

    # Update with combined tags
    return update_ticket(ticket_id, tags=list(new_tags))
