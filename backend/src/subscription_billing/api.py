"""API contracts for subscription billing workflows."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import PlanChange, PlanChangeError, Subscription, SubscriptionNotFoundError, SubscriptionStateError
from .services import LIFECYCLE_TRANSITIONS, SubscriptionBillingService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_subscriptions": {"method": "GET", "path": "/api/v1/subscriptions"},
    "create_subscription": {"method": "POST", "path": "/api/v1/subscriptions"},
    "get_subscription": {"method": "GET", "path": "/api/v1/subscriptions/{subscription_id}"},
    "transition_subscription": {"method": "POST", "path": "/api/v1/subscriptions/{subscription_id}/transitions"},
    "request_plan_change": {"method": "POST", "path": "/api/v1/subscriptions/{subscription_id}/plan-changes"},
    "renew_subscription": {"method": "POST", "path": "/api/v1/subscriptions/{subscription_id}/renewals"},
    "list_invoice_hooks": {"method": "GET", "path": "/api/v1/subscriptions/{subscription_id}/invoice-hooks"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class SubscriptionBillingApi:
    def __init__(self, service: SubscriptionBillingService) -> None:
        self._service = service

    def list_subscriptions(self, request_id: str) -> dict[str, Any]:
        return success([asdict(item) for item in self._service.list_subscriptions()], request_id)

    def create_subscription(self, subscription: Subscription, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.create_subscription(subscription)), request_id)
        except SubscriptionStateError as exc:
            return error("validation_error", str(exc), request_id)

    def get_subscription(self, subscription_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.get_subscription(subscription_id)), request_id)
        except SubscriptionNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def transition_subscription(
        self,
        subscription_id: str,
        *,
        to_status: str,
        at_time: str,
        request_id: str,
    ) -> dict[str, Any]:
        if to_status not in LIFECYCLE_TRANSITIONS:
            return error("validation_error", f"Unknown status: {to_status}", request_id)
        try:
            updated = self._service.transition_subscription(subscription_id, to_status=to_status, at_time=at_time)
            return success(asdict(updated), request_id)
        except SubscriptionNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except SubscriptionStateError as exc:
            return error("conflict", str(exc), request_id)

    def request_plan_change(self, change: PlanChange, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.request_plan_change(change)), request_id)
        except SubscriptionNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except PlanChangeError as exc:
            return error("validation_error", str(exc), request_id)

    def renew_subscription(
        self,
        subscription_id: str,
        *,
        renewal_date: str,
        next_end_date: str,
        hook_id: str,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            updated = self._service.renew_subscription(
                subscription_id,
                renewal_date=renewal_date,
                next_end_date=next_end_date,
                hook_id=hook_id,
            )
            return success(asdict(updated), request_id)
        except SubscriptionNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except SubscriptionStateError as exc:
            return error("conflict", str(exc), request_id)

    def list_invoice_hooks(self, subscription_id: str, request_id: str) -> dict[str, Any]:
        try:
            self._service.get_subscription(subscription_id)
        except SubscriptionNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        return success([asdict(hook) for hook in self._service.list_invoice_hooks(subscription_id)], request_id)
