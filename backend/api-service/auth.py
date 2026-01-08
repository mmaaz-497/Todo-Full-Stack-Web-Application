"""Authentication middleware for FastAPI backend.

This module provides:
- BetterAuth session token verification
- User ID extraction from session response
- Path parameter validation (user_id must match token)
- FastAPI dependencies for protected endpoints
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Dapr configuration
DAPR_HTTP_URL = os.getenv("DAPR_HTTP_URL", "http://localhost:3500")
DAPR_APP_ID_AUTH = os.getenv("DAPR_APP_ID_AUTH", "better-auth-service")

# BetterAuth configuration (fallback for non-Dapr deployments)
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3001")
USE_DAPR_INVOCATION = os.getenv("USE_DAPR_INVOCATION", "true").lower() == "true"

# HTTP Bearer token scheme
security = HTTPBearer()


def verify_better_auth_session(token: str) -> dict:
    """Verify BetterAuth session token by calling auth service.

    Uses Dapr service invocation for service-to-service communication when enabled.
    Falls back to direct HTTP call if USE_DAPR_INVOCATION=false.

    Args:
        token: BetterAuth session token

    Returns:
        dict: Session data with user information

    Raises:
        HTTPException: If token is invalid or session validation fails
    """
    try:
        print(f"[DEBUG] Validating session token: {token[:20]}...")

        # Determine URL based on Dapr configuration
        if USE_DAPR_INVOCATION:
            # Dapr service invocation pattern: http://localhost:3500/v1.0/invoke/{app-id}/method/{method-name}
            url = f"{DAPR_HTTP_URL}/v1.0/invoke/{DAPR_APP_ID_AUTH}/method/api/auth/get-session"
            print(f"[DEBUG] Using Dapr service invocation: {url}")
        else:
            # Direct HTTP call (fallback for non-Dapr deployments)
            url = f"{BETTER_AUTH_URL}/api/auth/get-session"
            print(f"[DEBUG] Using direct HTTP call: {url}")

        # Call BetterAuth session endpoint with Bearer token
        # Note: Better Auth uses /get-session endpoint, not /session
        # Increased timeout to handle database latency
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=20  # Increased from 10 to 20 seconds
        )

        print(f"[DEBUG] BetterAuth session response status: {response.status_code}")

        if response.status_code != 200:
            print(f"[DEBUG] Session validation failed: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        session_data = response.json()
        print(f"[DEBUG] Session data: {session_data}")

        # Extract user from session response
        user = session_data.get("user")
        if not user or not user.get("id"):
            print(f"[DEBUG] No user in session data")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session missing user information",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except requests.RequestException as e:
        print(f"[DEBUG] Request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service unavailable: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extract and validate user ID by verifying BetterAuth session token.

    This dependency can be used in FastAPI endpoints to:
    1. Verify the session token is valid
    2. Extract the user_id from the session

    Usage:
        @app.get("/api/{user_id}/tasks")
        def get_tasks(user_id: str, current_user_id: str = Depends(get_current_user_id)):
            if user_id != current_user_id:
                raise HTTPException(status_code=403, detail="Unauthorized access")
            # Proceed with query...

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        str: User ID extracted from session

    Raises:
        HTTPException: If token is invalid or missing user_id
    """
    token = credentials.credentials
    user = verify_better_auth_session(token)

    # Extract user_id from session user data
    user_id = user.get("id")

    print(f"[DEBUG] Extracted user_id from session: {user_id}")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not extract user_id from session",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def verify_user_ownership(path_user_id: str, token_user_id: str) -> None:
    """Verify that the user_id in the path matches the token's user_id.

    This enforces data isolation - users can only access their own resources.

    Args:
        path_user_id: user_id from API path parameter
        token_user_id: user_id extracted from session validation

    Raises:
        HTTPException: If user IDs don't match (403 Forbidden)
    """
    # DEBUG: Log both user IDs for comparison
    print(f"[DEBUG] Path user_id: {path_user_id}")
    print(f"[DEBUG] Token user_id: {token_user_id}")
    print(f"[DEBUG] Match: {path_user_id == token_user_id}")

    if path_user_id != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: Cannot access another user's data",
        )
