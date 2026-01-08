"""
JWT authentication for WebSocket connections.

Validates JWT tokens to extract user_id.
"""

from jose import jwt, JWTError
import os
import logging

logger = logging.getLogger(__name__)

# JWT configuration (should match auth service)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


def verify_token(token: str) -> int:
    """
    Verify JWT token and extract user_id.

    Args:
        token: JWT token string

    Returns:
        User ID if valid, None otherwise

    Raises:
        Exception: If token is invalid
    """
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user_id (adjust field name based on your auth service)
        user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")

        if not user_id:
            raise ValueError("Token missing user identifier")

        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)

        logger.debug(f"Token verified for user {user_id}")
        return user_id

    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise Exception("Invalid token")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise Exception("Token verification failed")
