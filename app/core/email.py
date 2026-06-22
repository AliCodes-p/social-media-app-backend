from fastapi_mail import MessageSchema, MessageType, NameEmail
from app.core.mail import fm


async def send_otp_email(email: str, otp: str):

    message = MessageSchema(
        subject="Your OTP Code",
        recipients=[NameEmail(email=email, name="User")],
        body=f"Your OTP is: {otp}. It will expire in 5 minutes.",
        subtype=MessageType.plain
    )

    await fm.send_message(message)