from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import follows
from app.api.routes import router as root_router
from app.api.auth import router as auth_router
from app.api.post import router as post_router
from app.api.user import router as users_router
from app.api.feed import router as feed_router
from app.api.comment import router as comment_router
from app.api.likes import router as like_router
from app.api.share import router as share_router
from app.api.friend_request import router as friend_request_router
from app.api import chat
from app.api import admin

app = FastAPI(
    title="Social Media App",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root routes (health check, etc.)
app.include_router(root_router)

# Auth routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Post routes
app.include_router(post_router)

# User routes
app.include_router(users_router)

#feed routes
app.include_router(feed_router)

# Comment routes
app.include_router(comment_router)

# Like routes
app.include_router(like_router)

# Share routes
app.include_router(share_router)

#follow routes
app.include_router(follows.router)

#friend request routes
app.include_router(friend_request_router)
#chat router
app.include_router(chat.router)

app.include_router(admin.router)
