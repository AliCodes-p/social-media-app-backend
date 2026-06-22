from fastapi import FastAPI
from app.api.routes import router as root_router
from app.api.auth import router as auth_router

app = FastAPI()

app.include_router(root_router)
app.include_router(auth_router)