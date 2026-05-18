"""Keyword-rule-based intent classifier for WhatsApp inbound messages.

Docs: docs/whatsapp-execution-model.md §10 — Intent Detection + Auto-Classification

Design:
- No ML required. Rule-based keyword matching against normalized message body.
- Ordered by specificity: payment_query > follow_up_response > lead_inquiry > support_request.
- First match wins. No match → out_of_scope.
- Keyword lists are tenant-extendable via FeatureFlag config (future).
- Classification result is stored as `intent` on the message event — immutable after write.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Intent = Literal[
    "lead_inquiry",
    "payment_query",
    "follow_up_response",
    "support_request",
    "out_of_scope",
]

# ── Keyword lists ──────────────────────────────────────────────────────────────
# Each keyword is a whole-word pattern (matched case-insensitively).
# Order of rules determines priority — first matching rule wins.

_RULES: list[tuple[Intent, list[str]]] = [
    # payment_query: highest specificity — financial signals
    ("payment_query", [
        "paid", "payment", "send money", "transferred", "jazzcash", "easypaisa",
        "bank", "received", "amount", "receipt", "transaction", "bhej diya",
        "pay kar", "paisa", "rupay", "rupees",
    ]),
    # follow_up_response: responses to existing outbound messages
    ("follow_up_response", [
        "yes", "ok", "okay", "confirmed", "done", "will do", "call me",
        "meeting", "agreed", "haan", "theek", "theek hai", "thik hai",
        "zaroor", "bilkul", "ready", "available",
    ]),
    # lead_inquiry: expressions of commercial interest
    ("lead_inquiry", [
        "price", "rate", "quote", "product", "available", "interested",
        "info", "information", "details", "cost", "charges", "package",
        "service", "buy", "purchase", "kitna", "kya", "offer", "deal",
        "discount", "demo",
    ]),
    # support_request: problem / complaint signals
    ("support_request", [
        "problem", "issue", "not working", "help", "complaint", "broken",
        "error", "fail", "failed", "wrong", "incorrect", "mushkil",
        "masla", "kharab", "nahi chal",
    ]),
]

# Pre-compile word-boundary patterns for performance
_COMPILED_RULES: list[tuple[Intent, list[re.Pattern[str]]]] = [
    (intent, [re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE) for kw in keywords])
    for intent, keywords in _RULES
]


@dataclass(frozen=True)
class ClassificationResult:
    intent: Intent
    matched_keyword: str | None   # the keyword that triggered the match, or None
    confidence: str               # "rule_match" | "no_match"


def classify_intent(
    message_body: str,
    has_media_attachment: bool = False,
    linked_invoice_id: str | None = None,
) -> ClassificationResult:
    """Classify inbound message body into a canonical intent.

    Args:
        message_body:          Raw text of the inbound WhatsApp message.
        has_media_attachment:  True if the message contains an image/document.
        linked_invoice_id:     Set if this conversation is linked to an open invoice.

    Returns:
        ClassificationResult with intent, matched keyword, and confidence.
    """
    normalized = message_body.strip()

    # Special case: media attachment on an invoice conversation → likely payment proof
    if has_media_attachment and linked_invoice_id:
        return ClassificationResult(
            intent="payment_query",
            matched_keyword="<media_attachment_on_invoice>",
            confidence="rule_match",
        )

    for intent, patterns in _COMPILED_RULES:
        for pattern in patterns:
            match = pattern.search(normalized)
            if match:
                return ClassificationResult(
                    intent=intent,
                    matched_keyword=match.group(0).lower(),
                    confidence="rule_match",
                )

    return ClassificationResult(
        intent="out_of_scope",
        matched_keyword=None,
        confidence="no_match",
    )
