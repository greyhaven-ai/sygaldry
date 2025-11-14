# Helpdesk Integration Tool

## Overview

Zendesk helpdesk integration tool for managing support tickets via the Zendesk REST API v2. Search, create, update tickets, manage comments and tags for comprehensive customer support automation.

## Features

- Search tickets with advanced filters (status, priority, tags, type)
- Get detailed ticket information
- Create new support tickets
- Update existing tickets (status, priority, assignee)
- List and add comments to tickets
- Manage ticket tags
- Full Pydantic model validation
- Support for public and private comments

## Installation

```bash
sygaldry add helpdesk_integration
pip install httpx
```

## Authentication

Set your Zendesk API credentials as environment variables:

```bash
export ZENDESK_SUBDOMAIN="mycompany"  # For mycompany.zendesk.com
export ZENDESK_EMAIL="admin@mycompany.com"
export ZENDESK_API_TOKEN="your_api_token_here"
```

### Generating an API Token

1. Log in to your Zendesk account as an admin
2. Navigate to Admin > Channels > API
3. Enable "Token Access" if not already enabled
4. Click the '+' button to add a new API token
5. Give it a descriptive name and copy the token
6. Set it as the `ZENDESK_API_TOKEN` environment variable

## Quick Start

```python
from helpdesk_integration import (
    search_tickets,
    get_ticket,
    create_ticket,
    update_ticket,
    add_ticket_comment
)

# Search for open high-priority tickets
tickets = search_tickets(
    query="login issue",
    status="open",
    priority="high",
    max_results=10
)

# Get specific ticket details
ticket = get_ticket(12345)
print(f"Subject: {ticket.subject}")
print(f"Status: {ticket.status}")
print(f"Priority: {ticket.priority}")

# Create a new support ticket
new_ticket = create_ticket(
    subject="Cannot login to account",
    description="User reports unable to login after password reset. Error message: 'Invalid credentials'",
    requester_email="user@example.com",
    requester_name="John Doe",
    priority="high",
    ticket_type="problem",
    tags=["login", "authentication", "password-reset"]
)
print(f"Created ticket #{new_ticket.id}")

# Update ticket status and add comment
updated_ticket = update_ticket(
    ticket_id=12345,
    status="pending",
    comment="We're investigating this issue. Will update you shortly.",
    public_comment=True
)

# Add a follow-up comment
add_ticket_comment(
    ticket_id=12345,
    body="Issue has been resolved. Please try logging in again.",
    public=True
)
```

## Functions

### search_tickets()

Search for tickets with advanced filtering options.

**Parameters:**
- `query` (str): Search query text (searches subject and description)
- `status` (str): Filter by status - "new", "open", "pending", "hold", "solved", "closed", or "all"
- `priority` (str, optional): Filter by priority - "low", "normal", "high", or "urgent"
- `ticket_type` (str, optional): Filter by type - "problem", "incident", "question", or "task"
- `tags` (list[str], optional): Filter by tags (tickets must have all specified tags)
- `max_results` (int): Maximum number of results (default: 30)
- `sort_by` (str): Sort field - "created_at", "updated_at", "priority", or "status" (default: "created_at")
- `sort_order` (str): Sort order - "asc" or "desc" (default: "desc")

**Returns:** List of `Ticket` objects

**Example:**
```python
# Search for bugs reported by customers
tickets = search_tickets(
    query="bug",
    tags=["customer-reported"],
    status="open",
    priority="high"
)

# Find all pending tickets
pending = search_tickets(
    status="pending",
    sort_by="updated_at",
    sort_order="asc"
)
```

### get_ticket()

Get detailed information about a specific ticket.

**Parameters:**
- `ticket_id` (int): Ticket ID

**Returns:** `Ticket` object

**Example:**
```python
ticket = get_ticket(12345)
print(f"Subject: {ticket.subject}")
print(f"Status: {ticket.status}")
print(f"Tags: {', '.join(ticket.tags)}")
```

### create_ticket()

Create a new support ticket.

**Parameters:**
- `subject` (str): Ticket subject/title
- `description` (str): Ticket description/body
- `requester_name` (str, optional): Name of the person requesting support
- `requester_email` (str, optional): Email of the requester
- `priority` (str): Priority level - "low", "normal", "high", or "urgent" (default: "normal")
- `ticket_type` (str, optional): Ticket type - "problem", "incident", "question", or "task"
- `tags` (list[str], optional): List of tags to apply
- `assignee_id` (int, optional): ID of user to assign the ticket to

**Returns:** Created `Ticket` object

**Example:**
```python
ticket = create_ticket(
    subject="Payment processing error",
    description="Customer unable to complete checkout. Transaction ID: TX-12345",
    requester_email="customer@example.com",
    requester_name="Jane Smith",
    priority="urgent",
    ticket_type="incident",
    tags=["payment", "checkout", "urgent"]
)
```

### update_ticket()

Update an existing ticket.

**Parameters:**
- `ticket_id` (int): Ticket ID to update
- `status` (str, optional): New status - "new", "open", "pending", "hold", "solved", or "closed"
- `priority` (str, optional): New priority - "low", "normal", "high", or "urgent"
- `comment` (str, optional): Comment to add to the ticket
- `tags` (list[str], optional): New tags (replaces existing tags)
- `assignee_id` (int, optional): New assignee user ID
- `public_comment` (bool): Whether the comment is public (default: True)

**Returns:** Updated `Ticket` object

**Example:**
```python
# Update status and add public comment
ticket = update_ticket(
    ticket_id=12345,
    status="solved",
    comment="Issue resolved. Database connection restored.",
    public_comment=True
)

# Assign and escalate
ticket = update_ticket(
    ticket_id=12345,
    assignee_id=67890,
    priority="urgent",
    comment="Escalating to senior support engineer",
    public_comment=False
)
```

### list_ticket_comments()

List all comments on a ticket.

**Parameters:**
- `ticket_id` (int): Ticket ID
- `max_results` (int): Maximum number of comments to return (default: 30)

**Returns:** List of `Comment` objects

**Example:**
```python
comments = list_ticket_comments(ticket_id=12345)
for comment in comments:
    print(f"Author {comment.author_id}: {comment.body}")
    print(f"Public: {comment.public}")
```

### add_ticket_comment()

Add a comment to a ticket.

**Parameters:**
- `ticket_id` (int): Ticket ID
- `body` (str): Comment text
- `public` (bool): Whether comment is public (visible to requester) (default: True)

**Returns:** Created `Comment` object

**Example:**
```python
# Add public comment
comment = add_ticket_comment(
    ticket_id=12345,
    body="Thank you for reporting this issue. We're looking into it.",
    public=True
)

# Add internal note
comment = add_ticket_comment(
    ticket_id=12345,
    body="Customer has premium support plan - prioritize this ticket",
    public=False
)
```

### add_ticket_tags()

Add tags to a ticket without replacing existing tags.

**Parameters:**
- `ticket_id` (int): Ticket ID
- `tags` (list[str]): List of tags to add

**Returns:** Updated `Ticket` object

**Example:**
```python
ticket = add_ticket_tags(
    ticket_id=12345,
    tags=["escalated", "vip-customer", "needs-followup"]
)
print(f"All tags: {ticket.tags}")
```

## Data Models

### Ticket

Represents a Zendesk support ticket.

**Fields:**
- `id` (int): Ticket ID
- `subject` (str): Ticket subject
- `description` (str, optional): Ticket description
- `status` (str): Ticket status (new/open/pending/hold/solved/closed)
- `priority` (str): Priority level (low/normal/high/urgent)
- `ticket_type` (str, optional): Ticket type (problem/incident/question/task)
- `tags` (list[str]): Ticket tags
- `requester_id` (int): Requester user ID
- `assignee_id` (int, optional): Assignee user ID
- `created_at` (str): Creation timestamp
- `updated_at` (str): Last update timestamp
- `url` (str): Ticket URL

### Comment

Represents a ticket comment.

**Fields:**
- `id` (int): Comment ID
- `body` (str): Comment text
- `author_id` (int): Comment author ID
- `created_at` (str): Creation timestamp
- `public` (bool): Whether comment is public

### TicketStatus

Represents ticket status with value and label.

**Fields:**
- `value` (str): Status value
- `label` (str): Human-readable label

### TicketRequester

Represents ticket requester information.

**Fields:**
- `id` (int): User ID
- `name` (str): User name
- `email` (str): User email

## Integration Examples

### Customer Support Agent

```python
from helpdesk_integration import search_tickets, update_ticket, add_ticket_comment

# Get all open urgent tickets
urgent_tickets = search_tickets(
    status="open",
    priority="urgent",
    max_results=50
)

for ticket in urgent_tickets:
    print(f"Urgent: #{ticket.id} - {ticket.subject}")

    # Add automated response
    add_ticket_comment(
        ticket_id=ticket.id,
        body="This ticket has been flagged as urgent and assigned to our priority queue.",
        public=True
    )
```

### Bug Triage Workflow

```python
from helpdesk_integration import search_tickets, update_ticket, add_ticket_tags

# Find bug reports
bugs = search_tickets(
    query="bug",
    status="new",
    tags=["customer-reported"]
)

for bug in bugs:
    # Triage and categorize
    update_ticket(
        ticket_id=bug.id,
        status="open",
        priority="high"
    )

    # Add engineering tags
    add_ticket_tags(
        ticket_id=bug.id,
        tags=["engineering", "bug-triage", "needs-investigation"]
    )
```

### Automated Ticket Routing

```python
from helpdesk_integration import search_tickets, update_ticket

# Route billing tickets to billing team
billing_tickets = search_tickets(
    tags=["billing"],
    status="new"
)

BILLING_TEAM_ID = 12345

for ticket in billing_tickets:
    update_ticket(
        ticket_id=ticket.id,
        assignee_id=BILLING_TEAM_ID,
        status="open",
        comment="Routing to billing team for review",
        public_comment=False
    )
```

## Error Handling

The tool raises exceptions for common error scenarios:

```python
from helpdesk_integration import get_ticket

try:
    ticket = get_ticket(99999)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        print("Ticket not found")
    elif e.response.status_code == 401:
        print("Authentication failed - check your credentials")
    else:
        print(f"API error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Rate Limits

Zendesk API has rate limits based on your plan:
- **Standard**: 200 requests per minute
- **Professional**: 400 requests per minute
- **Enterprise**: 700 requests per minute

The tool uses reasonable defaults but you may need to implement rate limiting for high-volume operations.

## Use Cases

- **Customer Support Automation**: Automatically create, route, and update support tickets
- **Bug Tracking Integration**: Link bug reports from customers to engineering workflows
- **SLA Monitoring**: Track ticket response times and escalate overdue tickets
- **Support Analytics**: Analyze ticket volumes, resolution times, and customer satisfaction
- **Chatbot Integration**: Enable chatbots to create and update support tickets
- **Email-to-Ticket**: Process support emails and create tickets programmatically
- **Multi-Channel Support**: Integrate with other tools to provide omnichannel support

## License

MIT
