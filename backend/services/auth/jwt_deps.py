"""JWT authentication dependency for FastAPI public routes.

Spec: backend/docs/identity-auth-rbac.md
  - Bearer token, short-lived ≤15m
  - Claims: sub (user_id), tenant_id, role, jti
  - RBAC: deny-overrides-allow
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

_SECRET = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-in-production")
_ALGORITHM = "HS256"

_bearer = HTTPBearer()


@dataclass(frozen=True)
class TokenClaims:
    sub: str        # user_id
    tenant_id: str
    role: str
    jti: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> TokenClaims:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
        return TokenClaims(
            sub=payload["sub"],
            tenant_id=payload["tenant_id"],
            role=payload.get("role", "sales_rep"),
            jti=payload["jti"],
        )
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
