from fastapi import HTTPException, Request
from auth.google_oauth import verify_jwt


def get_current_user(request: Request) -> dict:
    """
    FastAPI dependency — inject into any route to require authentication.

    Usage:
        @router.get("/protected")
        def my_route(user = Depends(get_current_user)):
            return {"email": user["email"]}
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Provide a Bearer token."
        )

    token = auth_header.split(" ", 1)[1]
    payload = verify_jwt(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token is invalid or has expired. Please log in again."
        )

    return payload