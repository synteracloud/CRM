"""Aggregation and merge logic for unified customer profile."""

from __future__ import annotations

from dataclasses import asdict

from .entities import (
    AccountRecord,
    ActivityRecord,
    ContactRecord,
    CustomerProfileError,
    EntityNotFoundError,
    LeadRecord,
    MissingRelationError,
    UnifiedCustomerProfile,
    UnifiedIdentity,
)


class Customer360Service:
    """In-memory CDP aggregation service for Lead/Contact/Account/Activity."""

    def __init__(self) -> None:
        self._leads: dict[str, LeadRecord] = {}
        self._contacts: dict[str, ContactRecord] = {}
        self._accounts: dict[str, AccountRecord] = {}
        self._activities: dict[str, ActivityRecord] = {}
        self._lead_contact: dict[str, str] = {}
        self._lead_account: dict[str, str] = {}

    def upsert_lead(self, lead: LeadRecord) -> LeadRecord:
        self._leads[lead.lead_id] = lead
        return lead

    def upsert_contact(self, contact: ContactRecord) -> ContactRecord:
        self._contacts[contact.contact_id] = contact
        return contact

    def upsert_account(self, account: AccountRecord) -> AccountRecord:
        self._accounts[account.account_id] = account
        return account

    def add_activity(self, activity: ActivityRecord) -> ActivityRecord:
        self._activities[activity.activity_id] = activity
        return activity

    def link_lead(self, lead_id: str, contact_id: str | None = None, account_id: str | None = None) -> None:
        self._require(lead_id, self._leads, "lead")
        if contact_id is not None:
            self._require(contact_id, self._contacts, "contact")
            self._lead_contact[lead_id] = contact_id
        if account_id is not None:
            self._require(account_id, self._accounts, "account")
            self._lead_account[lead_id] = account_id

    def build_profile(
        self,
        *,
        tenant_id: str,
        profile_id: str,
        lead_id: str | None = None,
        contact_id: str | None = None,
        account_id: str | None = None,
    ) -> UnifiedCustomerProfile:
        lead_ids: set[str] = set()
        contact_ids: set[str] = set()
        account_ids: set[str] = set()

        if lead_id:
            lead = self._get_tenant_entity(lead_id, self._leads, tenant_id, "lead")
            lead_ids.add(lead.lead_id)
            linked_contact = self._lead_contact.get(lead_id)
            linked_account = self._lead_account.get(lead_id)
            if linked_contact:
                contact_ids.add(self._get_tenant_entity(linked_contact, self._contacts, tenant_id, "contact").contact_id)
            if linked_account:
                account_ids.add(self._get_tenant_entity(linked_account, self._accounts, tenant_id, "account").account_id)

        if contact_id:
            contact = self._get_tenant_entity(contact_id, self._contacts, tenant_id, "contact")
            contact_ids.add(contact.contact_id)
            if contact.account_id:
                account = self._accounts.get(contact.account_id)
                if not account:
                    raise MissingRelationError(
                        f"Contact {contact.contact_id} references missing account {contact.account_id}"
                    )
                if account.tenant_id != tenant_id:
                    raise MissingRelationError(
                        f"Contact {contact.contact_id} account {contact.account_id} does not belong to tenant {tenant_id}"
                    )
                account_ids.add(account.account_id)

        if account_id:
            account_ids.add(self._get_tenant_entity(account_id, self._accounts, tenant_id, "account").account_id)

        self._expand_by_identity(tenant_id, lead_ids, contact_ids)

        for resolved_contact_id in tuple(contact_ids):
            account_ref = self._contacts[resolved_contact_id].account_id
            if account_ref:
                account = self._accounts.get(account_ref)
                if not account:
                    raise MissingRelationError(
                        f"Contact {resolved_contact_id} references missing account {account_ref}"
                    )
                if account.tenant_id != tenant_id:
                    raise MissingRelationError(
                        f"Contact {resolved_contact_id} account {account_ref} does not belong to tenant {tenant_id}"
                    )
                account_ids.add(account.account_id)

        activity_ids = self._collect_activity_ids(tenant_id, lead_ids, contact_ids, account_ids)
        identity = self._merge_identity(lead_ids, contact_ids)

        return UnifiedCustomerProfile(
            profile_id=profile_id,
            tenant_id=tenant_id,
            lead_ids=tuple(sorted(lead_ids)),
            contact_ids=tuple(sorted(contact_ids)),
            account_ids=tuple(sorted(account_ids)),
            activity_ids=tuple(sorted(activity_ids)),
            identity=identity,
        )

    def _collect_activity_ids(
        self,
        tenant_id: str,
        lead_ids: set[str],
        contact_ids: set[str],
        account_ids: set[str],
    ) -> set[str]:
        resolved_ids: set[str] = set()
        for activity in self._activities.values():
            if activity.tenant_id != tenant_id:
                continue
            if (activity.entity_type == "lead" and activity.entity_id in lead_ids) or (
                activity.entity_type == "contact" and activity.entity_id in contact_ids
            ) or (activity.entity_type == "account" and activity.entity_id in account_ids):
                resolved_ids.add(activity.activity_id)
        return resolved_ids

    def _expand_by_identity(self, tenant_id: str, lead_ids: set[str], contact_ids: set[str]) -> None:
        keys = self._identity_keys_for_sets(lead_ids, contact_ids)
        if not keys:
            return

        for lead in self._leads.values():
            if lead.tenant_id != tenant_id:
                continue
            if self._identity_key(lead.email) in keys or self._identity_key(lead.phone) in keys:
                lead_ids.add(lead.lead_id)
                linked_contact = self._lead_contact.get(lead.lead_id)
                if linked_contact:
                    contact = self._contacts.get(linked_contact)
                    if contact and contact.tenant_id == tenant_id:
                        contact_ids.add(contact.contact_id)

        for contact in self._contacts.values():
            if contact.tenant_id != tenant_id:
                continue
            if self._identity_key(contact.email) in keys or self._identity_key(contact.phone) in keys:
                contact_ids.add(contact.contact_id)

    def _merge_identity(self, lead_ids: set[str], contact_ids: set[str]) -> UnifiedIdentity:
        email_seen: set[str] = set()
        phone_seen: set[str] = set()

        for lead_id in lead_ids:
            lead = self._leads[lead_id]
            email_key = self._identity_key(lead.email)
            phone_key = self._identity_key(lead.phone)
            if email_key:
                email_seen.add(email_key)
            if phone_key:
                phone_seen.add(phone_key)

        for contact_id in contact_ids:
            contact = self._contacts[contact_id]
            email_key = self._identity_key(contact.email)
            phone_key = self._identity_key(contact.phone)
            if email_key:
                email_seen.add(email_key)
            if phone_key:
                phone_seen.add(phone_key)

        sorted_emails = tuple(sorted(email_seen))
        sorted_phones = tuple(sorted(phone_seen))
        return UnifiedIdentity(
            primary_email=sorted_emails[0] if sorted_emails else None,
            primary_phone=sorted_phones[0] if sorted_phones else None,
            all_emails=sorted_emails,
            all_phones=sorted_phones,
        )

    @staticmethod
    def _identity_key(value: str | None) -> str:
        return (value or "").strip().lower()

    def _identity_keys_for_sets(self, lead_ids: set[str], contact_ids: set[str]) -> set[str]:
        keys: set[str] = set()
        for lead_id in lead_ids:
            lead = self._leads[lead_id]
            for value in (lead.email, lead.phone):
                key = self._identity_key(value)
                if key:
                    keys.add(key)
        for contact_id in contact_ids:
            contact = self._contacts[contact_id]
            for value in (contact.email, contact.phone):
                key = self._identity_key(value)
                if key:
                    keys.add(key)
        return keys

    @staticmethod
    def _require(entity_id: str, store: dict[str, object], entity_name: str) -> None:
        if entity_id not in store:
            raise EntityNotFoundError(f"{entity_name} not found: {entity_id}")

    @staticmethod
    def _get_tenant_entity(entity_id: str, store: dict[str, object], tenant_id: str, entity_name: str):
        entity = store.get(entity_id)
        if not entity:
            raise EntityNotFoundError(f"{entity_name} not found: {entity_id}")
        if getattr(entity, "tenant_id") != tenant_id:
            raise CustomerProfileError(f"{entity_name} {entity_id} does not belong to tenant {tenant_id}")
        return entity

    def dump_state(self) -> dict[str, object]:
        return {
            "leads": [asdict(v) for v in self._leads.values()],
            "contacts": [asdict(v) for v in self._contacts.values()],
            "accounts": [asdict(v) for v in self._accounts.values()],
            "activities": [asdict(v) for v in self._activities.values()],
        }
