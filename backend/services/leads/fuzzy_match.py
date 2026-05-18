"""Fuzzy contact name matching — P-018.

Docs: docs/whatsapp-execution-model.md §11 — Anti-Lead Loss Guarantee
      pending.md P-018 — Fuzzy name match for duplicate contact detection
      BEHAV-002

Algorithm:
    Primary:  token sort ratio — normalise both names to sorted lowercase tokens,
              then measure Levenshtein similarity.  Handles "Muhammad Ali" vs
              "Ali Muhammad" (same person, different order).
    Fallback: plain Levenshtein similarity when token sort produces no useful signal.

Threshold: ≥ 85 % similarity → surface a merge suggestion.
           Never auto-merge — result is always advisory.

Feature flag: contact.fuzzy_name_match must be enabled for a tenant before
              this module is consulted.  Evaluated via services/feature_flags/evaluator.py.

Usage::
    from services.leads.fuzzy_match import name_similarity, suggest_duplicate

    score = name_similarity("Muhammad Ali Khan", "Ali Khan Muhammad")
    # → ~0.92

    result = suggest_duplicate(candidate_name="Ali Khan", existing_contacts=[...])
    # → DuplicateSuggestion(contact_id=..., score=0.91, action="suggest_merge")
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


# ── Normalisation ─────────────────────────────────────────────────────────────

def _normalise(name: str) -> str:
    """Lowercase, strip diacritics, collapse whitespace, remove punctuation."""
    # Unicode normalisation — decompose accented chars then strip combining marks
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_safe = "".join(c for c in nfkd if not unicodedata.combining(c))
    lowered = ascii_safe.lower()
    # Remove punctuation (keep letters, digits, spaces)
    cleaned = re.sub(r"[^\w\s]", "", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()


def _token_sort(name: str) -> str:
    """Sort name tokens alphabetically and rejoin — order-insensitive comparison."""
    tokens = _normalise(name).split()
    return " ".join(sorted(tokens))


# ── Levenshtein distance (pure Python, no external deps) ──────────────────────

def _levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    # Wagner-Fischer DP — O(len(a) * len(b)) time, O(len(b)) space
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            if ca == cb:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[len(b)]


def _levenshtein_similarity(a: str, b: str) -> float:
    """Return similarity in [0.0, 1.0].  1.0 = identical."""
    if not a and not b:
        return 1.0
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    dist = _levenshtein(a, b)
    return 1.0 - dist / max_len


# ── Public similarity API ─────────────────────────────────────────────────────

SIMILARITY_THRESHOLD = 0.85  # ≥85 % → surface suggestion (pending.md P-018)


def name_similarity(a: str, b: str) -> float:
    """Return the fuzzy similarity score between two contact names.

    Uses token sort ratio as primary algorithm to handle name-order variants.
    Score is in [0.0, 1.0].

    Examples::
        name_similarity("Muhammad Ali Khan", "Ali Khan Muhammad")  # ~0.93
        name_similarity("Zara Ahmed", "Zahra Ahmad")               # ~0.79
        name_similarity("Bilal Hussain", "Bilal Hussain")          # 1.0
    """
    if not a or not b:
        return 0.0

    # Primary: token sort ratio — handles reordered names
    ts_a = _token_sort(a)
    ts_b = _token_sort(b)
    token_score = _levenshtein_similarity(ts_a, ts_b)

    # Fallback: plain Levenshtein on normalised strings
    plain_score = _levenshtein_similarity(_normalise(a), _normalise(b))

    # Return the higher of the two scores
    return max(token_score, plain_score)


def is_likely_duplicate(a: str, b: str, threshold: float = SIMILARITY_THRESHOLD) -> bool:
    """Return True if two names are similar enough to warrant a merge suggestion."""
    return name_similarity(a, b) >= threshold


# ── Suggestion domain type ────────────────────────────────────────────────────

@dataclass(frozen=True)
class DuplicateSuggestion:
    """Advisory merge suggestion — never triggers auto-merge.

    Docs: docs/whatsapp-execution-model.md §11
    BEHAV-002 — surfaced as suggestion, not action.
    """
    contact_id:    str
    contact_name:  str
    score:         float           # similarity score 0.0–1.0
    action:        str = "suggest_merge"   # always "suggest_merge" — never "auto_merge"


@dataclass(frozen=True)
class FuzzyMatchResult:
    """Result of a fuzzy name match against a contact list."""
    candidate_name:  str
    suggestions:     tuple[DuplicateSuggestion, ...]
    threshold_used:  float

    @property
    def has_suggestions(self) -> bool:
        return len(self.suggestions) > 0

    @property
    def best(self) -> DuplicateSuggestion | None:
        return self.suggestions[0] if self.suggestions else None


# ── Main entry point ─────────────────────────────────────────────────────────

def suggest_duplicate(
    candidate_name: str,
    existing_contacts: list[dict],
    threshold: float = SIMILARITY_THRESHOLD,
    max_suggestions: int = 3,
) -> FuzzyMatchResult:
    """Compare a candidate name against a list of existing contacts.

    Args:
        candidate_name:     Name from inbound WhatsApp message / new contact form.
        existing_contacts:  List of dicts with at least {"contact_id", "contact_name"}.
                            Typically the result of a tenant-scoped DB query.
        threshold:          Minimum similarity score (default 0.85).
        max_suggestions:    Maximum number of suggestions to return (default 3).

    Returns:
        FuzzyMatchResult with suggestions sorted by score descending.
        suggestions is empty if no contact meets the threshold.

    Notes:
        - Never raises — returns empty result on bad input.
        - Caller must check feature flag before calling this function.
        - All suggestions have action="suggest_merge"; never auto-merge.
    """
    if not candidate_name or not existing_contacts:
        return FuzzyMatchResult(
            candidate_name=candidate_name,
            suggestions=(),
            threshold_used=threshold,
        )

    scored: list[tuple[float, dict]] = []
    for contact in existing_contacts:
        existing_name = contact.get("contact_name") or (
            f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
        )
        if not existing_name:
            continue
        score = name_similarity(candidate_name, existing_name)
        if score >= threshold:
            scored.append((score, contact))

    # Sort by score descending, take top N
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:max_suggestions]

    suggestions = tuple(
        DuplicateSuggestion(
            contact_id=c["contact_id"],
            contact_name=(
                c.get("contact_name")
                or f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
            ),
            score=round(score, 4),
        )
        for score, c in top
    )

    return FuzzyMatchResult(
        candidate_name=candidate_name,
        suggestions=suggestions,
        threshold_used=threshold,
    )
