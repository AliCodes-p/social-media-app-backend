from app.schemas.user import UserCardResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependency import get_db
from app.services.auth_dependency import get_current_user
from app.models.user import User

from app.schemas.friend_request import (
    FriendRequestCreate,
    FriendRequestResponse,
    FriendStatusResponse ,
    IncomingFriendRequestResponse   
)

from app.services.friend_request_service import (
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
    get_friends,
    get_incoming_requests,
    get_friend_status,
    cancel_friend_request,
    remove_friend
)


router = APIRouter(
    prefix="/friend-requests",
    tags=["Friend Requests"]
)


# Send friend request
@router.post("",response_model=FriendRequestResponse)
def send_request(
    request: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return send_friend_request(
        db,
        current_user,
        request.receiver_id
    )


# Accept friend request
@router.patch("/{request_id}/accept",response_model=FriendRequestResponse)
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return accept_friend_request(
        db,
        current_user,
        request_id
    )


# Reject friend request
@router.patch("/{request_id}/reject",response_model=FriendRequestResponse)
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return reject_friend_request(
        db,
        current_user,
        request_id
    )
#Get Friends
@router.get("/friends",response_model=list[UserCardResponse])
def friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_friends(
        db,
        current_user
    )
# GET INCOMMING REQUEST 

@router.get("/incoming",response_model=list[IncomingFriendRequestResponse]
)
def incoming_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_incoming_requests(
        db,
        current_user
    )
# GET FRIEND STATUS ROUTE

@router.get(
    "/status/{user_id}",
    response_model=FriendStatusResponse
)
def friend_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_friend_status(
        db,
        current_user,
        user_id
    )

# CANCEL FRIEND REQUEST BY THE SENDER(ITS ROUTE)

@router.delete("/{request_id}")
def cancel_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return cancel_friend_request(
        db,
        current_user,
        request_id
    )

# REMOVE FRIEND
@router.delete("/{user_id}/remove")
def unfriend(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return remove_friend(
        db,
        current_user,
        user_id
    )