from fastapi import Header, HTTPException
from jose import jwt, JWTError
from app.config import settings


def verify_token(authorization: str = Header(...)) -> str:
    """Verify JWT token and extract user_id

    Constitution Principle: Security and User Isolation

    Args:
        authorization: Authorization header (Bearer <token>)

    Returns:
        user_id from token claims

    Raises:
        HTTPException 401 for invalid/missing tokens
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")

    # Development mode: Accept 'dev_token' for testing
    if settings.ENVIRONMENT == "development" and token.startswith("dev_"):
        return "test_user_123"  # Return test user ID

    # Production mode: Verify JWT properly
    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET,
            issuer=settings.AUTH_ISSUER,
            algorithms=["HS256"]
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")

        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# Alias for FastAPI dependency injection
get_current_user_id = verify_token
