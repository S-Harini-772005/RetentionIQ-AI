from typing import List
from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.auth.security import get_current_user

class RoleChecker:
    """
    FastAPI Dependency for Role Based Access Control (RBAC).
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        """
        Validates if the authenticated user has one of the required roles.
        """
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FOR_REFORBIDDEN,
                detail=f"Operation not permitted for role: {user.role}. Required: {self.allowed_roles}"
            )
        return user

# Predefined role dependencies for clean architecture
allow_admin = RoleChecker(["Admin"])
allow_analyst = RoleChecker(["Admin", "Analyst"])
allow_executive = RoleChecker(["Admin", "Executive"])
allow_all_authenticated = RoleChecker(["Admin", "Analyst", "Executive"])