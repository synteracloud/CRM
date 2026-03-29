"""Territory management exports."""

from .api import API_ENDPOINTS, TerritoryManagementApi
from .entities import (
    AmbiguousOwnershipError,
    PrincipalContext,
    SecurityBoundaryError,
    Territory,
    TerritoryAssignment,
    TerritoryError,
    TerritoryNotFoundError,
    TerritoryRule,
)
from .services import TerritoryManagementService

__all__ = [
    "API_ENDPOINTS",
    "AmbiguousOwnershipError",
    "PrincipalContext",
    "SecurityBoundaryError",
    "Territory",
    "TerritoryAssignment",
    "TerritoryError",
    "TerritoryManagementApi",
    "TerritoryManagementService",
    "TerritoryNotFoundError",
    "TerritoryRule",
]
