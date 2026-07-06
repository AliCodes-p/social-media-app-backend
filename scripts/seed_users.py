from app.db.database import SessionLocal
from app.models.user import User
from app.models.profile import Profile
from app.services.auth_service import hash_password


db = SessionLocal()

users = [
    {
        "username": "ali",
        "email": "ali@example.com",
        "bio": "Full Stack Developer",
        "avatar": "https://picsum.photos/seed/ali/200",
        "cover": "https://picsum.photos/seed/ali-cover/1200/400",
    },
    {
        "username": "sara",
        "email": "sara@example.com",
        "bio": "UI/UX Designer",
        "avatar": "https://picsum.photos/seed/sara/200",
        "cover": "https://picsum.photos/seed/sara-cover/1200/400",
    },
    {
        "username": "ahmed",
        "email": "ahmed@example.com",
        "bio": "Backend Engineer",
        "avatar": "https://picsum.photos/seed/ahmed/200",
        "cover": "https://picsum.photos/seed/ahmed-cover/1200/400",
    },
    {
        "username": "fatima",
        "email": "fatima@example.com",
        "bio": "AI Enthusiast",
        "avatar": "https://picsum.photos/seed/fatima/200",
        "cover": "https://picsum.photos/seed/fatima-cover/1200/400",
    },
    {
        "username": "hassan",
        "email": "hassan@example.com",
        "bio": "Mobile App Developer",
        "avatar": "https://picsum.photos/seed/hassan/200",
        "cover": "https://picsum.photos/seed/hassan-cover/1200/400",
    },
]
PASSWORD = "Password123"

for u in users:

    existing = db.query(User).filter(User.email == u["email"]).first()

    if existing:
        print(f"{u['username']} already exists.")
        continue

    user = User(
        username=u["username"],
        email=u["email"],
        hashed_password=hash_password(PASSWORD),
        is_verified=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    profile = Profile(
        user_id=user.id,
        bio=u["bio"],
        avatar_url=u["avatar"],
        cover_url=u["cover"],
    )

    db.add(profile)
    db.commit()

    print(f"Created {u['username']}")

db.close()

print("Done!")