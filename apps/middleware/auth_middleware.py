import os
import jwt
import logging
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

logger = logging.getLogger(__name__)

# Security scheme
security_scheme = HTTPBearer(auto_error=False)

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-for-local-development")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> dict:
    """
    Dependency that extracts the JWT token from the Authorization header,
    decodes it, validates the expiration, and extracts the claims.
    
    Supports a 'dev-bypass' token for easy manual testing during hackathon review.
    """
    # If security scheme is disabled in config or credentials not provided
    if not credentials:
        # For ease of testing in hackathons, let's allow bypass if configured
        if os.getenv("BYPASS_AUTH", "true").lower() == "true":
            logger.info("Authentication bypassed (BYPASS_AUTH=true). Using mock risk_engineer user.")
            return {"user_id": "hackathon-dev-user", "role": "risk_engineer"}
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid scheme"
        )
        
    token = credentials.credentials
    
    # Check for dev-bypass token
    if token == "mock-token" or token == "risk_engineer_token":
        return {"user_id": "hackathon-mock-user", "role": "risk_engineer"}
        
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

class RoleChecker:
    """
    RBAC Authorization checker helper.
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role")
        if user_role not in self.allowed_roles:
            logger.warning(f"User with role '{user_role}' denied access. Required roles: {self.allowed_roles}")
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires role in {self.allowed_roles}"
            )
        return user
