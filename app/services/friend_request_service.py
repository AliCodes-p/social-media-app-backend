from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from sqlalchemy import and_,or_
from app.models.user import User
from app.models.friend_request import FriendRequest

# SEND FRIEND REQUESTS

def send_friend_request(
    db: Session,
    current_user: User,
    receiver_id: int
):
    if current_user.id == receiver_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot send a friend request to yourself."
        )

    receiver = (
        db.query(User)
        .filter(User.id == receiver_id)
        .first()
    )

    if receiver is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    existing_request = (
    db.query(FriendRequest)
    .filter(
        or_(
            and_(
                FriendRequest.sender_id == current_user.id,
                FriendRequest.receiver_id == receiver_id,
            ),
            and_(
                FriendRequest.sender_id == receiver_id,
                FriendRequest.receiver_id == current_user.id,
            ),
        )
    )
    .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Friend request already exists."
        )
            
    friend_request = FriendRequest(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        status="pending"
    )

    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)

    return friend_request

# ACCEPT FRIEND REQUESTS

def accept_friend_request(
    db: Session,
    current_user: User,
    request_id: int
):
    friend_request = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.id == request_id
        )
        .first()
    )

    if friend_request is None:
        raise HTTPException(
            status_code=404,
            detail="Friend request not found."
        )

    if friend_request.receiver_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to accept this friend request."
        )

    if friend_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Friend request has already been processed."
        )

    friend_request.status = "accepted"

    db.commit()
    db.refresh(friend_request)

    return friend_request

# ONLY RECEIVER CAN REJECT IT 

def reject_friend_request(
    db: Session,
    current_user: User,
    request_id: int
):
    friend_request = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.id == request_id
        )
        .first()
    )

    if friend_request is None:
        raise HTTPException(
            status_code=404,
            detail="Friend request not found."
        )

    if friend_request.receiver_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to reject this friend request."
        )

    if friend_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Friend request has already been processed."
        )
    db.delete(friend_request)
    db.commit()

    return friend_request

#GET FRIEND 
def get_friends(
    db: Session,
    current_user: User
):
    """
    Return all accepted friends of the current user.
    """

    friendships = (
        db.query(FriendRequest)
        .options(
            joinedload(FriendRequest.sender).joinedload(User.profile),
            joinedload(FriendRequest.receiver).joinedload(User.profile)
        )
        .filter(
            FriendRequest.status == "accepted",
            or_(
                FriendRequest.sender_id == current_user.id,
                FriendRequest.receiver_id == current_user.id,
            ),
        )
        .all()
    )

    friends = []

    for friendship in friendships:
        if friendship.sender_id == current_user.id:
            friends.append(friendship.receiver)
        else:
            friends.append(friendship.sender)

    return friends
 
# GET REQUEST SO USER KNOW SOMEONE SEND HIM A REQUEST   

def get_incoming_requests(
    db: Session,
    current_user: User
):
    """
    Return all pending friend requests received by the current user.
    """

    incoming_requests = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.receiver_id == current_user.id,
            FriendRequest.status == "pending",
        )
        .all()
    )

    result = []

    for request in incoming_requests:
        result.append({
            "id": request.id,
            "sender_id": request.sender_id,
            "receiver_id": request.receiver_id,
            "status": request.status,
            "updated_at": request.updated_at,

            "sender_username": request.sender.username,
            "sender_avatar": (
            request.sender.profile.avatar_url
            if request.sender.profile
            else None
        ),
        })

    return result

# WHEN USER SEND REQUEST AND VISIT THAT PROFILE HE NEED TO KNOW THAT IS THE REQUEST ACCEPTED OR NOT TO SHOW IN PROFILE 

def get_friend_status(
    db: Session,
    current_user: User,
    user_id: int
):
    """
    Return the relationship status between the current user
    and another user.
    """

    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot check friend status with yourself."
        )
    # (FIND ANY FRIENDSHIP BETWEEN CURRENT USER AND THE USER. THEY CAN EXITS IN BOTH SIDES)
    friendship = (
        db.query(FriendRequest)
        .filter(
            or_(
                and_(
                    FriendRequest.sender_id == current_user.id,
                    FriendRequest.receiver_id == user_id,
                ),
                and_(
                    FriendRequest.sender_id == user_id,
                    FriendRequest.receiver_id == current_user.id,
                ),
            )
        )
        .first()
    )

    if friendship is None:
        return {
            "status": "none"
        }

    if friendship.status == "accepted":
        return {
            "status": "friends"
        }

    if (
        friendship.status == "pending"
        and friendship.sender_id == current_user.id
    ):
     return {
        "status": "pending_sent",
        "request_id": friendship.id,
    }

    if (
        friendship.status == "pending"
        and friendship.receiver_id == current_user.id
    ):
        return {
        "status": "pending_received",
        "request_id": friendship.id,
    }

    return {
        "status": friendship.status
    }


# TO CANCEL THE FRIEND REQUEST SENT BY THE USER(SENDER) IF THEY CHANGE THEIR MIND THAT THEY WANT TO SEND REQUEST

def cancel_friend_request(
    db: Session,
    current_user: User,
    request_id: int
):
    """
    Cancel a pending friend request sent by the current user.
    """

    friend_request = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.id == request_id
        )
        .first()
    )

    if friend_request is None:
        raise HTTPException(
            status_code=404,
            detail="Friend request not found."
        )

    if friend_request.sender_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to cancel this friend request."
        )

    if friend_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending friend requests can be cancelled."
        )

    db.delete(friend_request)
    db.commit()

    return {"message": "Friend request cancelled successfully."}

# UNFRIEND A FRIEND

def remove_friend(
    db: Session,
    current_user: User,
    friend_id: int
):
    """
    Remove an existing friendship.
    """

    friendship = (
    db.query(FriendRequest)
    .filter(
        FriendRequest.status == "accepted",
        or_(
            and_(
                FriendRequest.sender_id == current_user.id,
                FriendRequest.receiver_id == friend_id,
            ),
            and_(
                FriendRequest.sender_id == friend_id,
                FriendRequest.receiver_id == current_user.id,
            ),
        ),
    )
    .first()
)

    if friendship is None:
        raise HTTPException(
            status_code=404,
            detail="Friend not found."
        )

    db.delete(friendship)
    db.commit()

    return {"message": "Friend removed successfully."}
