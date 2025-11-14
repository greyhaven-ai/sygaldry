"""Helpdesk Integration Tool - Manage and search Zendesk support tickets."""

from .tool import (
    Ticket,
    TicketStatus,
    Comment,
    TicketRequester,
    search_tickets,
    get_ticket,
    create_ticket,
    update_ticket,
    list_ticket_comments,
    add_ticket_comment,
    add_ticket_tags,
)

__all__ = [
    "Ticket",
    "TicketStatus",
    "Comment",
    "TicketRequester",
    "search_tickets",
    "get_ticket",
    "create_ticket",
    "update_ticket",
    "list_ticket_comments",
    "add_ticket_comment",
    "add_ticket_tags",
]
