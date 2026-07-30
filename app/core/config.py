from pydantic_settings import BaseSettings


class Settings(BaseSettings):  # after reading match with class field 
    SECRET_KEY: str
    DATABASE_URL: str

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None

    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # =========================
    # Cloudinary
    # =========================
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    class Config:  # tell it to read value from env file
        env_file = ".env"


settings = Settings()  # type: ignore