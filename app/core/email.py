from pydantic import BaseModel, EmailStr
from fastapi_mail import ConnectionConfig
import os

class EmailSettings(BaseModel):
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_USERNAME")
    MAIL_PORT: int = 465   # Gmail SMTP port
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_SSL_TLS: bool = True
    MAIL_STARTTLS: bool = False

email_settings = EmailSettings()

conf = ConnectionConfig(
    MAIL_USERNAME=email_settings.MAIL_USERNAME,
    MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
    MAIL_FROM=email_settings.MAIL_FROM,
    MAIL_PORT=email_settings.MAIL_PORT,
    MAIL_SERVER=email_settings.MAIL_SERVER,
    MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
    MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
    USE_CREDENTIALS=True
)