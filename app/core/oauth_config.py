from pydantic_settings import BaseSettings


class OAuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None

    FRONTEND_URL: str = "https://social-media-app-frontend-psi.vercel.app"
    BACKEND_URL: str = "https://socialsphereb.duckdns.org"

    class Config:
        env_file = ".env"


oauth_settings = OAuthSettings()