"""JWT authentication dependency for FastAPI public routes.

Spec: backend/docs/security/identity-auth-rbac.md §3.2
  - Bearer token, short-lived ≤15m
  - Claims: sub, tenant_id, role, role_ids, scopes, jti, iss, aud, territory_ids
  - RBAC: deny-overrides-allow
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

_SECRET = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-in-production")
_ALGORITHM = "HS256"
_EXPECTED_ISS = os.environ.get("JWT_ISSUER", "")
_EXPECTED_AUD = os.environ.get("JWT_AUDIENCE", "")

_bearer = HTTPBearer()


@dataclass(frozen=True)
class TokenClaims:
    sub: str                              # user_id
    tenant_id: str
    role: str
    jti: str
    role_ids: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    iss: str = ""
    aud: str = ""
    territory_ids: List[str] = field(default_factory=list)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> TokenClaims:
    token = credentials.credentials
    try:
        options = {"verify_aud": bool(_EXPECTED_AUD), "verify_iss": bool(_EXPECTED_ISS)}
        payload = jwt.decode(
            token,
            _SECRET,
            algorithms=[_ALGORITHM],
            audience=_EXPECTED_AUD or None,
            issuer=_EXPECTED_ISS or None,
            options=options,
        )
        return TokenClaims(
            sub=payload["sub"],
            tenant_id=payload["tenant_id"],
            role=payload.get("role", "sales_rep"),
            jti=payload["jti"],
            role_ids=payload.get("role_ids", []),
            scopes=payload.get("scopes", []),
            iss=payload.get("iss", ""),
            aud=payload.get("aud", ""),
            territory_ids=payload.get("territory_ids", []),
        )
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
