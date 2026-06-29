from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str
    purpose: str  # register | login


class ResendOtpRequest(BaseModel):
    email: EmailStr
    purpose: str  # register | login
