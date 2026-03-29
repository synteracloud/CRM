"""API contracts for Contract Lifecycle Management."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import Contract, ContractNotFoundError, ContractStateError, ContractTerm
from .services import ContractService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_contracts": {"method": "GET", "path": "/api/v1/contracts"},
    "create_contract": {"method": "POST", "path": "/api/v1/contracts"},
    "get_contract": {"method": "GET", "path": "/api/v1/contracts/{contract_id}"},
    "submit_for_review": {"method": "POST", "path": "/api/v1/contracts/{contract_id}/review"},
    "approve_contract": {"method": "POST", "path": "/api/v1/contracts/{contract_id}/approvals"},
    "activate_contract": {"method": "POST", "path": "/api/v1/contracts/{contract_id}/activations"},
    "mark_renewal_pending": {"method": "POST", "path": "/api/v1/contracts/{contract_id}/renewal-pending"},
    "renew_contract": {"method": "POST", "path": "/api/v1/contracts/{contract_id}/renewals"},
    "terminate_contract": {"method": "POST", "path": "/api/v1/contracts/{contract_id}/terminations"},
    "add_contract_term": {"method": "POST", "path": "/api/v1/contracts/{contract_id}/terms"},
    "upsert_links": {"method": "PUT", "path": "/api/v1/contracts/{contract_id}/links"},
    "contracts_with_renewal_alerts": {"method": "GET", "path": "/api/v1/contracts/renewal-alerts"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": []},
        "meta": {"request_id": request_id},
    }


class ContractApi:
    def __init__(self, service: ContractService) -> None:
        self._service = service

    def list_contracts(self, request_id: str) -> dict[str, Any]:
        return success([asdict(contract) for contract in self._service.list_contracts()], request_id)

    def create_contract(self, contract: Contract, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.create_contract(contract)), request_id)
        except ContractStateError as exc:
            return error("conflict", str(exc), request_id)

    def get_contract(self, contract_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.get_contract(contract_id)), request_id)
        except ContractNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def submit_for_review(self, contract_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.submit_for_review(contract_id)), request_id)
        except ContractNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except ContractStateError as exc:
            return error("conflict", str(exc), request_id)

    def approve_contract(self, contract_id: str, approved_at: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.approve_contract(contract_id, approved_at)), request_id)
        except ContractNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except ContractStateError as exc:
            return error("conflict", str(exc), request_id)

    def activate_contract(self, contract_id: str, activated_at: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.activate_contract(contract_id, activated_at)), request_id)
        except ContractNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except ContractStateError as exc:
            return error("conflict", str(exc), request_id)

    def mark_renewal_pending(self, contract_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.mark_renewal_pending(contract_id)), request_id)
        except ContractNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except ContractStateError as exc:
            return error("conflict", str(exc), request_id)

    def renew_contract(self, contract_id: str, next_renewal_at: str, term: ContractTerm, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.renew_contract(contract_id, next_renewal_at, term)), request_id)
        except ContractNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except ContractStateError as exc:
            return error("conflict", str(exc), request_id)

    def terminate_contract(self, contract_id: str, terminated_at: str, reason: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.terminate_contract(contract_id, terminated_at, reason)), request_id)
        except ContractNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except ContractStateError as exc:
            return error("conflict", str(exc), request_id)

    def add_contract_term(self, contract_id: str, term: ContractTerm, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.add_contract_term(contract_id, term)), request_id)
        except ContractNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except ContractStateError as exc:
            return error("conflict", str(exc), request_id)

    def upsert_links(
        self,
        contract_id: str,
        account_id: str,
        order_id: str | None,
        subscription_id: str | None,
        invoice_summary_id: str | None,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            updated = self._service.upsert_links(
                contract_id,
                account_id=account_id,
                order_id=order_id,
                subscription_id=subscription_id,
                invoice_summary_id=invoice_summary_id,
            )
            return success(asdict(updated), request_id)
        except ContractNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except ContractStateError as exc:
            return error("conflict", str(exc), request_id)

    def contracts_with_renewal_alerts(self, as_of: str, request_id: str) -> dict[str, Any]:
        return success([asdict(c) for c in self._service.contracts_with_renewal_alerts(as_of)], request_id)
