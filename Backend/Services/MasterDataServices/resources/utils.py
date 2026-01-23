from jose import JWTError, jwt
from fastapi import Request, HTTPException, status

from configs import BaseConfig

def verify_authentication(request: Request):
    """
    Verifies JWT from:
    1. Authorization header (Bearer token)
    2. Session (legacy / browser-based)
    """
 
    token = None
 
    # ------------------ Authorization Header ------------------
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
 
    # ------------------ Session Fallback ------------------
    elif "loginer_details" in request.session:
        token = request.session["loginer_details"]
 
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
 
    try:
        payload = jwt.decode(
            token,
            BaseConfig.SECRET_KEY,
            algorithms=[BaseConfig.ALGORITHM],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
 
    user_id = payload.get("user_id")
    user_role = payload.get("user_role")
 
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )
 
    return user_id, user_role, token