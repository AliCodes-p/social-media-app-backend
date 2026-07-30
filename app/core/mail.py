from fastapi_mail import ConnectionConfig , FastMail #Used to store email server configuration
from pydantic import SecretStr

conf = ConnectionConfig(
    MAIL_USERNAME="mali.hashlogics@gmail.com",
    MAIL_PASSWORD=SecretStr("stwgpgewiskmlzgg"),
    MAIL_FROM="mali.hashlogics@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com", #SMTP server responsible for sending mail
    MAIL_STARTTLS=True,  #start with normal conn then upgrade to tls encrypted
    MAIL_SSL_TLS=False, # do not use ssl from start
    USE_CREDENTIALS=True, # validate using username and pass
    VALIDATE_CERTS=True  # is this really gmail
)

fm = FastMail(conf)