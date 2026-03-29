"""API contracts for campaign + segment management."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import (
    Campaign,
    CampaignContactLink,
    CampaignLeadLink,
    CampaignNotFoundError,
    CampaignStateError,
    SegmentDefinition,
    SegmentNotFoundError,
    SegmentValidationError,
)
from .segmentation import serialize_segment
from .services import CampaignService
from .workspace import build_marketing_workspace


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_campaigns": {"method": "GET", "path": "/api/v1/campaigns"},
    "create_campaign": {"method": "POST", "path": "/api/v1/campaigns"},
    "get_campaign": {"method": "GET", "path": "/api/v1/campaigns/{campaign_id}"},
    "update_campaign": {"method": "PATCH", "path": "/api/v1/campaigns/{campaign_id}"},
    "delete_campaign": {"method": "DELETE", "path": "/api/v1/campaigns/{campaign_id}"},
    "activate_campaign": {"method": "POST", "path": "/api/v1/campaigns/{campaign_id}/activations"},
    "complete_campaign": {"method": "POST", "path": "/api/v1/campaigns/{campaign_id}/completions"},
    "list_segments": {"method": "GET", "path": "/api/v1/segments"},
    "create_segment": {"method": "POST", "path": "/api/v1/segments"},
    "get_segment": {"method": "GET", "path": "/api/v1/segments/{segment_id}"},
    "update_segment": {"method": "PATCH", "path": "/api/v1/segments/{segment_id}"},
    "delete_segment": {"method": "DELETE", "path": "/api/v1/segments/{segment_id}"},
    "link_campaign_lead": {"method": "POST", "path": "/api/v1/campaigns/{campaign_id}/leads"},
    "link_campaign_contact": {"method": "POST", "path": "/api/v1/campaigns/{campaign_id}/contacts"},
    "get_marketing_workspace": {"method": "GET", "path": "/api/v1/marketing/workspace"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class CampaignApi:
    def __init__(self, service: CampaignService) -> None:
        self._service = service

    def list_campaigns(self, request_id: str) -> dict[str, Any]:
        return success([asdict(campaign) for campaign in self._service.list_campaigns()], request_id)

    def create_campaign(self, campaign: Campaign, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.create_campaign(campaign)), request_id)
        except (CampaignStateError, SegmentNotFoundError) as exc:
            return error("validation_error", str(exc), request_id)

    def get_campaign(self, campaign_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.get_campaign(campaign_id)), request_id)
        except CampaignNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def update_campaign(self, campaign_id: str, changes: dict[str, object], request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.update_campaign(campaign_id, **changes)), request_id)
        except CampaignNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except CampaignStateError as exc:
            return error("validation_error", str(exc), request_id)

    def delete_campaign(self, campaign_id: str, request_id: str) -> dict[str, Any]:
        try:
            self._service.delete_campaign(campaign_id)
            return success({"deleted": True}, request_id)
        except CampaignNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def activate_campaign(self, campaign_id: str, activated_at: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.activate_campaign(campaign_id, activated_at)), request_id)
        except CampaignNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except CampaignStateError as exc:
            return error("conflict", str(exc), request_id)

    def complete_campaign(self, campaign_id: str, completed_at: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.complete_campaign(campaign_id, completed_at)), request_id)
        except CampaignNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except CampaignStateError as exc:
            return error("conflict", str(exc), request_id)

    def list_segments(self, request_id: str) -> dict[str, Any]:
        return success([serialize_segment(segment) for segment in self._service.list_segments()], request_id)

    def create_segment(self, segment: SegmentDefinition, request_id: str) -> dict[str, Any]:
        try:
            created = self._service.create_segment(segment)
            return success(serialize_segment(created), request_id)
        except SegmentValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def get_segment(self, segment_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(serialize_segment(self._service.get_segment(segment_id)), request_id)
        except SegmentNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def update_segment(self, segment_id: str, changes: dict[str, object], request_id: str) -> dict[str, Any]:
        try:
            updated = self._service.update_segment(segment_id, **changes)
            return success(serialize_segment(updated), request_id)
        except SegmentNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except SegmentValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def delete_segment(self, segment_id: str, request_id: str) -> dict[str, Any]:
        try:
            self._service.delete_segment(segment_id)
            return success({"deleted": True}, request_id)
        except SegmentNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def link_campaign_lead(self, link: CampaignLeadLink, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.link_lead(link)), request_id)
        except (CampaignNotFoundError, CampaignStateError) as exc:
            return error("validation_error", str(exc), request_id)

    def get_marketing_workspace(self, request_id: str) -> dict[str, Any]:
        workspace = build_marketing_workspace()
        return success(
            {
                "workspace_id": workspace.workspace_id,
                "title": workspace.title,
                "workflow_name": workspace.workflow_name,
                "campaign_flow": list(workspace.campaign_flow),
                "views": [
                    {
                        "view_id": view.view_id,
                        "title": view.title,
                        "route": view.route,
                        "purpose": view.purpose,
                        "metric_bindings": [
                            {
                                "metric_id": binding.metric_id,
                                "label": binding.label,
                                "read_model": binding.read_model,
                                "field": binding.field,
                            }
                            for binding in view.metric_bindings
                        ],
                    }
                    for view in workspace.views
                ],
                "interaction_patterns": [
                    {
                        "pattern_id": pattern.pattern_id,
                        "name": pattern.name,
                        "trigger": pattern.trigger,
                        "response": pattern.response,
                    }
                    for pattern in workspace.interaction_patterns
                ],
            },
            request_id,
        )

    def link_campaign_contact(self, link: CampaignContactLink, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.link_contact(link)), request_id)
        except (CampaignNotFoundError, CampaignStateError) as exc:
            return error("validation_error", str(exc), request_id)
