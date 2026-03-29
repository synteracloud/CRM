"""Services for Contract lifecycle orchestration and renewal alerting."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .entities import Contract, ContractNotFoundError, ContractStateError, ContractTerm


class ContractService:
    """In-memory contract service for deterministic lifecycle + renewal management."""

    def __init__(self) -> None:
        self._store: dict[str, Contract] = {}

    def list_contracts(self) -> list[Contract]:
        return list(self._store.values())

    def create_contract(self, contract: Contract) -> Contract:
        if contract.contract_id in self._store:
            raise ContractStateError(f"Contract already exists: {contract.contract_id}")
        if contract.status != "draft":
            raise ContractStateError("Contracts must be created in draft status.")
        if not contract.terms:
            raise ContractStateError("Contract must include at least one contract term on create.")
        self._store[contract.contract_id] = contract
        return contract

    def get_contract(self, contract_id: str) -> Contract:
        contract = self._store.get(contract_id)
        if not contract:
            raise ContractNotFoundError(f"Contract not found: {contract_id}")
        return contract

    def submit_for_review(self, contract_id: str) -> Contract:
        contract = self.get_contract(contract_id)
        if contract.status != "draft":
            raise ContractStateError(f"Only draft contracts can move to review. current={contract.status}")
        updated = contract.patch(status="review")
        self._store[contract_id] = updated
        return updated

    def approve_contract(self, contract_id: str, approved_at: str) -> Contract:
        contract = self.get_contract(contract_id)
        if contract.status != "review":
            raise ContractStateError(f"Only review contracts can be approved. current={contract.status}")
        updated = contract.patch(status="approved", approved_at=approved_at)
        self._store[contract_id] = updated
        return updated

    def activate_contract(self, contract_id: str, activated_at: str) -> Contract:
        contract = self.get_contract(contract_id)
        if contract.status != "approved":
            raise ContractStateError(f"Only approved contracts can be activated. current={contract.status}")
        updated = contract.patch(status="active", activated_at=activated_at)
        self._store[contract_id] = updated
        return updated

    def mark_renewal_pending(self, contract_id: str) -> Contract:
        contract = self.get_contract(contract_id)
        if contract.status != "active":
            raise ContractStateError(f"Only active contracts can move to renewal_pending. current={contract.status}")
        updated = contract.patch(status="renewal_pending")
        self._store[contract_id] = updated
        return updated

    def renew_contract(self, contract_id: str, next_renewal_at: str, term: ContractTerm) -> Contract:
        contract = self.get_contract(contract_id)
        if contract.status != "renewal_pending":
            raise ContractStateError(f"Only renewal_pending contracts can renew. current={contract.status}")
        if term.version <= max(existing.version for existing in contract.terms):
            raise ContractStateError("Renewal term version must increment over existing term versions.")
        updated = contract.patch(
            status="active",
            next_renewal_at=next_renewal_at,
            term_start_at=term.effective_from,
            term_end_at=term.effective_to,
            terms=(*contract.terms, term),
        )
        self._store[contract_id] = updated
        return updated

    def terminate_contract(self, contract_id: str, terminated_at: str, reason: str) -> Contract:
        contract = self.get_contract(contract_id)
        if contract.status not in {"active", "renewal_pending"}:
            raise ContractStateError(
                f"Only active or renewal_pending contracts can be terminated. current={contract.status}"
            )
        updated = contract.patch(status="terminated", terminated_at=terminated_at, termination_reason=reason)
        self._store[contract_id] = updated
        return updated

    def upsert_links(
        self,
        contract_id: str,
        *,
        account_id: str,
        order_id: str | None,
        subscription_id: str | None,
        invoice_summary_id: str | None,
    ) -> Contract:
        contract = self.get_contract(contract_id)
        if not account_id:
            raise ContractStateError("account_id is required for contract linkage consistency.")
        updated = contract.patch(
            account_id=account_id,
            order_id=order_id,
            subscription_id=subscription_id,
            invoice_summary_id=invoice_summary_id,
        )
        self._store[contract_id] = updated
        return updated

    def add_contract_term(self, contract_id: str, term: ContractTerm) -> Contract:
        contract = self.get_contract(contract_id)
        if contract.status in {"active", "terminated"}:
            raise ContractStateError(f"Cannot add draft/review terms when contract status={contract.status}")
        versions = {t.version for t in contract.terms}
        if term.version in versions:
            raise ContractStateError(f"Term version already exists: {term.version}")
        updated = contract.patch(terms=(*contract.terms, term), term_end_at=term.effective_to)
        self._store[contract_id] = updated
        return updated

    def contracts_with_renewal_alerts(self, as_of: str) -> list[Contract]:
        now = _parse_rfc3339(as_of)
        alerted: list[Contract] = []
        for contract in self._store.values():
            if contract.status not in {"active", "renewal_pending"}:
                continue
            renewal_at = _parse_rfc3339(contract.next_renewal_at)
            alert_at = renewal_at - timedelta(days=contract.renewal_alert_days)
            if now >= alert_at:
                alerted.append(contract)
        return alerted


def _parse_rfc3339(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
