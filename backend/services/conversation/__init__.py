"""Conversational CRM package."""

from .entities import (
    ChatActionResult,
    ChatMessage,
    CommandIntent,
    CommandParseResult,
    ConversationActivityEvent,
    ConversationContext,
)
from .parser import BasicCommandParser
from .service import ConversationalCRMService

__all__ = [
    "BasicCommandParser",
    "ChatActionResult",
    "ChatMessage",
    "CommandIntent",
    "CommandParseResult",
    "ConversationActivityEvent",
    "ConversationContext",
    "ConversationalCRMService",
]
