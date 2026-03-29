"""API adapters for CPQ pricing and approval rule orchestration."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from typing import Any

from .cpq_rules import CPQLineItemInput, CPQQuoteInput, CPQRulesEngine

CPQ_API_ENDPOINTS: dict[str, dict[str, str]] = {
    "evaluate_quote": {"method": "POST", "path": "/api/v1/cpq/quotes/evaluations"},
    "advance_approval": {"method": "POST", "path": "/api/v1/cpq/quotes/{quote_id}/approval-transitions"},
}


class CPQRulesApi:
    def __init__(self, engine: CPQRulesEngine) -> None:
        self._engine = engine

    def evaluate_quote(self, payload: dict[str, Any], request_id: str) -> dict[str, Any]:
        quote = CPQQuoteInput(
            quote_id=payload["quote_id"],
            tenant_id=payload["tenant_id"],
            currency=payload["currency"],
            line_items=tuple(
                CPQLineItemInput(
                    line_id=line["line_id"],
                    product_id=line["product_id"],
                    quantity=int(line["quantity"]),
                    list_price=Decimal(str(line["list_price"])),
                    requested_discount_percent=Decimal(str(line.get("requested_discount_percent", "0"))),
                )
                for line in payload.get("line_items", [])
            ),
            requested_quote_discount_percent=Decimal(str(payload.get("requested_quote_discount_percent", "0"))),
        )
        result = self._engine.evaluate_quote(quote)
        return _success(asdict(result), request_id)

    def advance_approval(self, quote_id: str, current_status: str, action: str, request_id: str) -> dict[str, Any]:
        transition = self._engine.apply_approval_transition(quote_id=quote_id, current_status=current_status, action=action)
        return _success(asdict(transition), request_id)


def _success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}
