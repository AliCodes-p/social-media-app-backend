from fastapi import FastAPI  # type: ignore[import]
from app.api.routes import router

app = FastAPI()

app.include_router(router)