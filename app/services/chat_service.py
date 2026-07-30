from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.conversation import Conversation
from app.models.conversation_participant import ConversationParticipant
from app.models.message import Message


def create_conversation(
    db: Session,
    user_ids: list[int]
) -> Conversation:
    """
    Create a new conversation and add all participants.
    """

    conversation = Conversation()

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    for user_id in user_ids:
        participant = ConversationParticipant(
            conversation_id=conversation.id,
            user_id=user_id
        )

        db.add(participant)

    db.commit()

    return conversation


def get_or_create_conversation(
    db: Session,
    user1_id: int,
    user2_id: int,
):
    conversation = (
        db.query(Conversation)
        .join(ConversationParticipant)
        .filter(
            ConversationParticipant.user_id.in_([user1_id, user2_id])
        )
        .group_by(Conversation.id)
        .having(func.count(ConversationParticipant.user_id) == 2)
        .first()
    )

    if not conversation:
        conversation = create_conversation(
            db,
            [user1_id, user2_id],
        )

    other_participant = next(
        participant
        for participant in conversation.participants
        if participant.user_id != user1_id
    )

    last_message = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation.id
        )
        .order_by(
            Message.created_at.desc()
        )
        .first()
    )

    return {
        "id": conversation.id,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "other_user": {
            "id": other_participant.user.id,
            "username": other_participant.user.username,
            "avatar_url": (
                other_participant.user.profile.avatar_url
                if other_participant.user.profile
                else None
            ),
        },
        "last_message": (
            {
                "content": last_message.content,
                "created_at": last_message.created_at,
            }
            if last_message
            else None
        ),
    }

def save_message(
    db: Session,
    conversation_id: int,
    sender_id: int,
    content: str
) -> Message:
    """
    Save a message in a conversation.
    """

    message = Message(
    conversation_id=conversation_id,
    sender_id=sender_id,
    content=content,
    status="sent"
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message

#loading the message of conversation only of loged in user is participant
def get_messages(
    db: Session,
    conversation_id: int,
    user_id: int
):
    """
    Return all messages only if the user belongs to the conversation.
    """

    participant = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id
        )
        .first()
    )

    if not participant:
        return None

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

# return all conversation that belonged to user
def get_user_conversations(
    db: Session,
    user_id: int
):
    conversations = (
        db.query(Conversation)
        .join(ConversationParticipant)
        .filter(
            ConversationParticipant.user_id == user_id
        )
        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )

    result = []

    for conversation in conversations:

        other_participant = next(
            participant
            for participant in conversation.participants
            if participant.user_id != user_id
        )

        last_message = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation.id
            )
            .order_by(
                Message.created_at.desc()
            )
            .first()
        )

        result.append(
            {
                "id": conversation.id,

                "created_at": conversation.created_at,

                "updated_at": conversation.updated_at,

                "other_user": {
                    "id": other_participant.user.id,
                    "username": other_participant.user.username,
                    "avatar_url": (
                        other_participant.user.profile.avatar_url
                        if other_participant.user.profile
                        else None
                    ),
                },

                "last_message": (
                    {
                        "content": last_message.content,
                        "created_at": last_message.created_at,
                    }
                    if last_message
                    else None
                ),
            }
        )

    return result

def get_conversation_participants(
    db: Session,
    conversation_id: int
):
    return (
        db.query(ConversationParticipant.user_id)
        .filter(
            ConversationParticipant.conversation_id == conversation_id
        )
        .all()
    )


def mark_messages_as_read(
    db: Session,
    conversation_id: int,
    user_id: int
):
    """
    Mark all messages in a conversation as read for a specific user.
    Only marks messages sent by other users (not by the current user).
    Returns the list of message IDs that were updated.
    """
    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.status == "sent"
        )
        .all()
    )
    
    updated_message_ids = []
    
    for message in messages:
        message.status = "read"
        updated_message_ids.append(message.id)
    
    if updated_message_ids:
        db.commit()
    
    return updated_message_ids