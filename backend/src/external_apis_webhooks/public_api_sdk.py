"""Public API exposure layer and basic SDK scaffolding for external developers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4


PUBLIC_API_ENDPOINTS: dict[str, dict[str, str]] = {
    "create_developer_application": {"method": "POST", "path": "/api/v1/developer-applications"},
    "issue_access_token": {"method": "POST", "path": "/api/v1/developer-access-tokens"},
    "list_public_integrations": {"method": "GET", "path": "/api/v1/public-integrations"},
}


@dataclass(frozen=True)
class DeveloperApplication:
    application_id: str
    developer_id: str
    app_name: str
    client_id: str
    client_secret: str
    scopes: tuple[str, ...]
    created_at: str


@dataclass(frozen=True)
class DeveloperAccessToken:
    token: str
    token_type: str
    expires_in: int
    scope: str


class ExternalDeveloperAuthError(ValueError):
    """Raised when external developer authentication fails."""


class ExternalDeveloperAuthService:
    def __init__(self) -> None:
        self._applications: dict[str, DeveloperApplication] = {}
        self._tokens: dict[str, tuple[str, set[str]]] = {}

    def register_application(self, developer_id: str, app_name: str, scopes: tuple[str, ...], created_at: str) -> DeveloperApplication:
        if not developer_id or not app_name:
            raise ExternalDeveloperAuthError("developer_id and app_name are required")
        if not scopes:
            raise ExternalDeveloperAuthError("at least one scope is required")

        application_id = f"dapp_{uuid4().hex[:24]}"
        client_id = f"cid_{uuid4().hex[:24]}"
        client_secret = f"csec_{uuid4().hex[:32]}"
        application = DeveloperApplication(
            application_id=application_id,
            developer_id=developer_id,
            app_name=app_name,
            client_id=client_id,
            client_secret=client_secret,
            scopes=tuple(sorted(set(scopes))),
            created_at=created_at,
        )
        self._applications[client_id] = application
        return application

    def issue_access_token(self, client_id: str, client_secret: str, requested_scopes: tuple[str, ...]) -> DeveloperAccessToken:
        application = self._applications.get(client_id)
        if not application or application.client_secret != client_secret:
            raise ExternalDeveloperAuthError("invalid_client_credentials")

        granted_scope_set = set(application.scopes)
        requested_scope_set = set(requested_scopes)
        if not requested_scope_set.issubset(granted_scope_set):
            raise ExternalDeveloperAuthError("requested scopes exceed granted application scopes")

        token = f"pat_{uuid4().hex}"
        scopes = requested_scope_set or granted_scope_set
        self._tokens[token] = (application.developer_id, scopes)
        return DeveloperAccessToken(token=token, token_type="Bearer", expires_in=3600, scope=" ".join(sorted(scopes)))

    def authorize(self, authorization_header: str | None, required_scope: str) -> str:
        if not authorization_header:
            raise ExternalDeveloperAuthError("missing_authorization_header")
        token_type, _, token = authorization_header.partition(" ")
        if token_type != "Bearer" or not token:
            raise ExternalDeveloperAuthError("invalid_authorization_header")

        token_record = self._tokens.get(token)
        if not token_record:
            raise ExternalDeveloperAuthError("invalid_token")

        developer_id, scopes = token_record
        if required_scope not in scopes:
            raise ExternalDeveloperAuthError("forbidden_scope")
        return developer_id


class PublicApiExposureService:
    def list_public_integrations(self) -> list[dict[str, str]]:
        return [
            {
                "integration_slug": "stripe",
                "category": "payments",
                "status": "available",
            },
            {
                "integration_slug": "sendgrid",
                "category": "email",
                "status": "available",
            },
            {
                "integration_slug": "twilio",
                "category": "sms",
                "status": "available",
            },
        ]


class PublicApiLayer:
    def __init__(self, auth: ExternalDeveloperAuthService, exposure: PublicApiExposureService) -> None:
        self._auth = auth
        self._exposure = exposure

    @staticmethod
    def success(data: Any, request_id: str) -> dict[str, Any]:
        return {"data": data, "meta": {"request_id": request_id}}

    @staticmethod
    def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
        return {
            "error": {"code": code, "message": message, "details": details or []},
            "meta": {"request_id": request_id},
        }

    def create_developer_application(
        self,
        request_body: dict[str, Any],
        request_id: str,
    ) -> dict[str, Any]:
        try:
            app = self._auth.register_application(
                developer_id=str(request_body["developer_id"]),
                app_name=str(request_body["app_name"]),
                scopes=tuple(str(scope) for scope in request_body["scopes"]),
                created_at=str(request_body["created_at"]),
            )
            return self.success(
                {
                    "application_id": app.application_id,
                    "developer_id": app.developer_id,
                    "app_name": app.app_name,
                    "client_id": app.client_id,
                    "client_secret": app.client_secret,
                    "scopes": list(app.scopes),
                    "created_at": app.created_at,
                },
                request_id,
            )
        except (KeyError, TypeError):
            return self.error("bad_request", "invalid request body", request_id)
        except ExternalDeveloperAuthError as exc:
            return self.error("validation_error", str(exc), request_id)

    def issue_access_token(self, request_body: dict[str, Any], request_id: str) -> dict[str, Any]:
        try:
            token = self._auth.issue_access_token(
                client_id=str(request_body["client_id"]),
                client_secret=str(request_body["client_secret"]),
                requested_scopes=tuple(str(scope) for scope in request_body.get("scopes", [])),
            )
            return self.success(
                {
                    "access_token": token.token,
                    "token_type": token.token_type,
                    "expires_in": token.expires_in,
                    "scope": token.scope,
                },
                request_id,
            )
        except (KeyError, TypeError):
            return self.error("bad_request", "invalid request body", request_id)
        except ExternalDeveloperAuthError as exc:
            return self.error("unauthorized", str(exc), request_id)

    def list_public_integrations(self, authorization_header: str | None, request_id: str) -> dict[str, Any]:
        try:
            developer_id = self._auth.authorize(authorization_header, required_scope="integrations:read")
            integrations = self._exposure.list_public_integrations()
            return self.success({"developer_id": developer_id, "items": integrations}, request_id)
        except ExternalDeveloperAuthError as exc:
            error_code = "forbidden" if str(exc) == "forbidden_scope" else "unauthorized"
            return self.error(error_code, str(exc), request_id)


@dataclass(frozen=True)
class PublicApiSdkConfig:
    base_url: str
    client_id: str
    client_secret: str


class PublicApiSdk:
    """Basic SDK scaffold that defines endpoint and auth request/response shapes."""

    def __init__(self, config: PublicApiSdkConfig) -> None:
        self._config = config

    def token_request(self, scopes: tuple[str, ...]) -> dict[str, Any]:
        return {
            "method": PUBLIC_API_ENDPOINTS["issue_access_token"]["method"],
            "url": f"{self._config.base_url}{PUBLIC_API_ENDPOINTS['issue_access_token']['path']}",
            "headers": {"Content-Type": "application/json", "Accept": "application/json"},
            "json": {
                "client_id": self._config.client_id,
                "client_secret": self._config.client_secret,
                "scopes": list(scopes),
            },
        }

    def integrations_request(self, access_token: str, page: int = 1, page_size: int = 25) -> dict[str, Any]:
        return {
            "method": PUBLIC_API_ENDPOINTS["list_public_integrations"]["method"],
            "url": f"{self._config.base_url}{PUBLIC_API_ENDPOINTS['list_public_integrations']['path']}",
            "headers": {"Accept": "application/json", "Authorization": f"Bearer {access_token}"},
            "params": {"page": page, "page_size": page_size},
        }
