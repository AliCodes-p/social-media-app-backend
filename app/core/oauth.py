import secrets

import httpx
from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.cookies import base_cookie_params
from app.models.oauth_account import OAuthAccount
from app.models.user import User
from app.services.auth_service import hash_password
from app.services.refresh_token_service import issue_auth_tokens


def _get_frontend_url() -> str:
    return settings.FRONTEND_URL or "http://localhost:3000"


# OAuth callback must hit the frontend /backend proxy so the oauth_state cookie
# (set during start on the frontend origin) is present on the callback request.
def _get_oauth_redirect_uri(provider: str) -> str:
    return f"{_get_frontend_url().rstrip('/')}/backend/auth/oauth/{provider}/callback"


def _get_provider_config(provider: str) -> dict[str, str]:
    if provider == "google":
        return {
            "client_id": settings.GOOGLE_CLIENT_ID or "",
            "client_secret": settings.GOOGLE_CLIENT_SECRET or "",
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        }

    if provider == "github":
        return {
            "client_id": settings.GITHUB_CLIENT_ID or "",
            "client_secret": settings.GITHUB_CLIENT_SECRET or "",
            "auth_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "user_info_url": "https://api.github.com/user",
        }

    raise HTTPException(status_code=404, detail="Unsupported OAuth provider")


OAUTH_STATE_MAX_AGE = 600


def _set_oauth_state_cookie(response: Response, provider: str, state: str) -> None:
    cookie_params = base_cookie_params(max_age=OAUTH_STATE_MAX_AGE)

    response.set_cookie(key="oauth_state", value=state, **cookie_params)
    response.set_cookie(key="oauth_provider", value=provider, **cookie_params)


def _clear_oauth_state_cookie(response: Response) -> None:
    cookie_params = base_cookie_params()
    response.delete_cookie(key="oauth_state", **cookie_params)
    response.delete_cookie(key="oauth_provider", **cookie_params)

#Create the Google/GitHub authorization URL, store a security state 
#value in a cookie, and redirect the user to Google/GitHub login page.

async def start_oauth_flow(provider: str, response: Response) -> RedirectResponse:
    config = _get_provider_config(provider)
   #check credential
    if not config["client_id"] or not config["client_secret"]:
        raise HTTPException(status_code=500, detail=f"{provider.title()} OAuth is not configured")

    state = secrets.token_urlsafe(24)

    if provider == "google":
        params = {
            "client_id": config["client_id"],
            "redirect_uri": _get_oauth_redirect_uri(provider),
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        import urllib.parse #convert dic into url format

        auth_url = f"{config['auth_url']}?{urllib.parse.urlencode(params)}"
        redirect = RedirectResponse(url=auth_url, status_code=302)
        _set_oauth_state_cookie(redirect, provider, state)
        return redirect

    params = {
        "client_id": config["client_id"],
        "redirect_uri": _get_oauth_redirect_uri(provider),
        "scope": "read:user user:email",
        "state": state,
    }
    import urllib.parse

    auth_url = f"{config['auth_url']}?{urllib.parse.urlencode(params)}"
    redirect = RedirectResponse(url=auth_url, status_code=302)
    _set_oauth_state_cookie(redirect, provider, state)
    return redirect


async def handle_oauth_callback(
    provider: str,
    code: str | None,
    state: str | None,
    request: Request,
    response: Response,
    db: Session,
) -> RedirectResponse:
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth code or state")

    stored_state = request.cookies.get("oauth_state")
    stored_provider = request.cookies.get("oauth_provider")
    print("Returned state:", state)
    print("Stored state:", request.cookies.get("oauth_state"))
    print("Stored provider:", request.cookies.get("oauth_provider"))
    print("All callback cookies:", request.cookies)
    

    if stored_state != state or stored_provider != provider:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    config = _get_provider_config(provider)
    if not config["client_id"] or not config["client_secret"]:
        raise HTTPException(status_code=500, detail=f"{provider.title()} OAuth is not configured")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if provider == "google":
                token_response = await client.post(
                    config["token_url"],
                    data={
                        "code": code,
                        "client_id": config["client_id"],
                        "client_secret": config["client_secret"],
                        "redirect_uri": _get_oauth_redirect_uri(provider),
                        "grant_type": "authorization_code",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                token_response.raise_for_status()
                token_data = token_response.json()
                access_token = token_data.get("access_token")
                #we have now access token but not user find who is the user

                profile_response = await client.get(
                    config["user_info_url"],
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                profile_response.raise_for_status()
                profile = profile_response.json()
                provider_user_id = str(profile.get("id") or profile.get("sub") or "")
                email = profile.get("email")
            else:
                token_response = await client.post(
                    config["token_url"],
                    data={
                        "code": code,
                        "client_id": config["client_id"],
                        "client_secret": config["client_secret"],
                        "redirect_uri": _get_oauth_redirect_uri(provider),
                    },
                    headers={"Accept": "application/json"},
                )
                token_response.raise_for_status()
                token_data = token_response.json()
                access_token = token_data.get("access_token")

                user_response = await client.get(
                    config["user_info_url"],
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                    },
                )
                user_response.raise_for_status()
                profile = user_response.json()

                email_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                    },
                )
                email_response.raise_for_status()
                email_entries = email_response.json() or []
                primary_email = next(
                    (item for item in email_entries if item.get("primary") and item.get("verified")),
                    None,
                )

                provider_user_id = str(profile.get("id") or "")
                email = (primary_email or {}).get("email") or profile.get("email")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=400, detail=f"Failed to authenticate with {provider.title()}: {exc}") from exc

    if not provider_user_id or not email:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read {provider.title()} profile",
        )

    user = _get_or_create_oauth_user(
        db,
        provider,
        provider_user_id,
        email,
    )

    redirect_url = f"{_get_frontend_url().rstrip('/')}/home"

    redirect_response = RedirectResponse(
        url=redirect_url,
        status_code=303,
    )

    issue_auth_tokens(redirect_response, db, user)
    _clear_oauth_state_cookie(redirect_response)

    return redirect_response


def _get_or_create_oauth_user(
    db: Session,
    provider: str,
    provider_user_id: str,
    email: str,
) -> User:

    # 1. Existing OAuth link
    existing_link = (
        db.query(OAuthAccount)
        .filter(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
        .first()
    )

    if existing_link:
        user = (
            db.query(User)
            .filter(User.id == existing_link.user_id)
            .first()
        )

        if user:
            return user

    # 2. Existing email/password account(check if acc with this email exist)
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:

        existing_oauth = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.user_id == existing_user.id,
                OAuthAccount.provider == provider,
            )
            .first()
        )

        if not existing_oauth:
            db.add(
                OAuthAccount(
                    user_id=existing_user.id,
                    provider=provider,
                    provider_user_id=provider_user_id,
                )
            )

        existing_user.is_verified = True
        db.commit()
        db.refresh(existing_user)

        return existing_user

    # 3. Brand new OAuth user
    username = _build_unique_username(db, email)

    user = User(
        username=username,
        email=email,
        hashed_password=None,
        is_verified=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(
        OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
        )
    )

    db.commit()
    db.refresh(user)

    return user


def _build_unique_username(db: Session, email: str) -> str:
    base_username = email.split("@", 1)[0].replace(".", "_").replace("-", "_")
    username = base_username
    counter = 1

    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    return username