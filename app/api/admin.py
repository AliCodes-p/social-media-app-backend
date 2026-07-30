from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.dependency import get_db
from app.core.admin import require_admin
from app.models.user import User
from app.services.admin_service import (
    get_dashboard_stats,
    get_all_users,
    get_user_by_id,
    update_user as update_user_service,
    delete_user as delete_user_service,
    block_user as block_user_service,
    unblock_user as unblock_user_service,
    get_all_posts,
    get_post_by_id,
    admin_update_post,
    admin_delete_post,
)
from app.schemas.post import (
    PostResponse,
    PostUpdate,
    AdminPostResponse,
)
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminUserResponse,
    AdminUserUpdate
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return get_dashboard_stats(db)

@router.get("/users",response_model=list[AdminUserResponse])
def get_users(db: Session = Depends(get_db),
              current_user: User = Depends(require_admin),
):
    return get_all_users(db)


@router.get("/users/{user_id}",response_model=AdminUserResponse,)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return get_user_by_id(db, user_id)


@router.patch("/users/{user_id}",response_model=AdminUserResponse,)
def update_user(
    user_id: int,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return update_user_service(
        db,
        user_id,
        data
    )


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return delete_user_service(
        db,
        user_id
    )


@router.patch("/users/{user_id}/block")
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return block_user_service(
        db,
        user_id
    )

@router.patch("/users/{user_id}/unblock")
def unblock_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return unblock_user_service(
        db,
        user_id
    )




@router.get("/posts",response_model=list[AdminPostResponse])
def get_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return get_all_posts(db)


@router.get("/posts/{post_id}",response_model=AdminPostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return get_post_by_id(
        db,
        post_id
    )





@router.patch("/posts/{post_id}",response_model=PostResponse)
def update_post(
    post_id: int,
    body: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return admin_update_post(
        db,
        post_id,
        body
    )

from app.services.admin_service import admin_delete_post


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return admin_delete_post(
        db,
        post_id
    )