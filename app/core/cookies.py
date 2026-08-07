from app.core.config import settings


def cookie_secure() -> bool:
    """Secure cookies in HTTPS deployments; allow plain HTTP for local dev."""
    return settings.FRONTEND_URL.startswith("https://")


def cookie_samesite() -> str:
    """
    Browser auth traffic goes through the frontend /backend proxy, so every
    cookie is scoped to the frontend origin. SameSite=Lax is sufficient and
    is sent on the top-level OAuth callback redirect from Google.
    """
    return "lax"


def base_cookie_params(*, max_age: int | None = None) -> dict:
    params: dict = {
        "httponly": True,
        "secure": cookie_secure(),
        "samesite": cookie_samesite(),
        "path": "/",
    }
    if max_age is not None:
        params["max_age"] = max_age
    return params
