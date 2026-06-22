from fastapi_mail import ConnectionConfig, FastMail
from pydantic import SecretStr

conf = ConnectionConfig(
    MAIL_USERNAME="mali.hashlogics@gmail.com",
    MAIL_PASSWORD=SecretStr("stwgpgewiskmlzgg"),
    MAIL_FROM="mali.hashlogics@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)