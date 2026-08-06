from fastapi import APIRouter, Depends, WebSocketException
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi import WebSocket, WebSocketDisconnect
from app.api.connection_manager import manager
from app.services.chat_service import save_message
from app.models.message import Message
import json

from app.db.dependency import get_db
from app.models.user import User
from app.schemas.conversation import ConversationResponse
from app.schemas.message import MessageResponse
from app.services.auth_dependency import get_current_user
from app.services.chat_service import (
    get_or_create_conversation,
    get_messages,
    get_user_conversations,
    get_conversation_participants,
    mark_messages_as_read,
    get_unread_message_counts,
)
from app.services.token_service import verify_token

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "/conversation/{user_id}",
    response_model=ConversationResponse
)
def create_or_get_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_or_create_conversation(
        db=db,
        user1_id=current_user.id,
        user2_id=user_id,
    )


@router.get(
    "/conversations",
    response_model=list[ConversationResponse]
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_conversations(
        db=db,
        user_id=current_user.id,
    )

#This endpoint is called when the user opens the Messages page.
@router.get(
    "/messages/{conversation_id}",
    response_model=list[MessageResponse]
)
def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    messages = get_messages(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if messages is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a participant in this conversation."
        )

    return messages

@router.get("/unread-count")
def unread_message_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_unread_message_counts(
        db,
        current_user.id,
    )


@router.post("/messages/{conversation_id}/read")
async def mark_conversation_as_read(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark all unread messages in a conversation as read.
    This is called when a user opens a conversation.
    """
    # Verify user is a participant
    messages = get_messages(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if messages is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a participant in this conversation."
        )

    # Mark messages as read and get updated message IDs
    updated_message_ids = mark_messages_as_read(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    # Notify the sender(s) via WebSocket about read receipts
    for message_id in updated_message_ids:
        # Get the message to find the sender
        message = db.query(Message).filter(Message.id == message_id).first()
        if message:
            # Send read receipt event to the sender
            read_receipt_data = {
                "type": "read_receipt",
                "message_id": message.id,
                "conversation_id": message.conversation_id,
                "reader_id": current_user.id,
                "status": "read",
            }
            # Use the connection manager to send to the sender
            await manager.send_personal_message(
                user_id=message.sender_id,
                message=read_receipt_data
            )

    return {"message": "Messages marked as read", "updated_count": len(updated_message_ids)}

#WEB Socket Endpoint

async def get_websocket_user(
    websocket: WebSocket,
    db: Session
) -> User:

    token = websocket.query_params.get("token")

    print("DEBUG WS TOKEN:", token)

    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="No authentication token provided"
        )

    payload = verify_token(
        token,
        expected_type="access"
    )

    if not payload:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token"
        )

    user_id = int(payload["sub"])

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User not found"
        )

    return user

@router.get("/ws-token")
def websocket_token(
    current_user: User = Depends(get_current_user)
):
    from app.services.token_service import create_access_token

    token = create_access_token(
        {
            "sub": str(current_user.id)
        }
    )

    return {
        "token": token
    }

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint with JWT authentication.
    """

    # Authenticate user before accepting connection
    try:
        user = await get_websocket_user(websocket, db)
    except WebSocketException as e:
        await websocket.close(code=e.code, reason=e.reason)
        return

    await manager.connect(
        user.id,
        websocket,
    )

    try:
        while True:
            data = await websocket.receive_json()

            conversation_id = data["conversation_id"]
            content = data["content"]

            message = save_message(
                db=db,
                conversation_id=conversation_id,
                sender_id=user.id,
                content=content,
            )

            message_data = {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "sender_id": message.sender_id,
                "content": message.content,
                "status": message.status,
                "created_at": message.created_at.isoformat(),
            }

            participants = get_conversation_participants(
                db,
                conversation_id,
            )

            # Send only to the OTHER participant(s)
            for participant in participants:
                participant_id = participant[0]

                if participant_id == user.id:
                    continue

                await manager.send_personal_message(
                    user_id=participant_id,
                    message=message_data,
                )

    except WebSocketDisconnect:
        manager.disconnect(user.id)

    except Exception as e:
        manager.disconnect(user.id)
        print(e)