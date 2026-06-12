from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from pydantic import SecretStr , EmailStr
from aiosmtplib import SMTP
from email.mime.text import MIMEText
import settings

def create_mail_instance():
    """创建FastMail实例"""
    mail_config = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return mail_config

# 自定义发送，强制指定纯英文 local_hostname，绕过系统主机名
async def send_email(config: ConnectionConfig, msg: MessageSchema):
    # 手动创建SMTP连接，固定英文主机名
    async with SMTP(
        hostname=config.MAIL_SERVER,
        port=config.MAIL_PORT,
        use_tls=config.MAIL_SSL_TLS,
        validate_certs=config.VALIDATE_CERTS,
        local_hostname="dev-pc-mail"  # 纯英文，无中文
    ) as server:
        mail_pwd = config.MAIL_PASSWORD.get_secret_value()
        await server.login(config.MAIL_USERNAME, mail_pwd)
        # 构建邮件内容
        mail_msg = MIMEText(msg.body, "html", "utf-8")
        mail_msg["Subject"] = msg.subject
        mail_msg["From"] = str(config.MAIL_FROM)
        mail_msg["To"] = ",".join(str(addr) for addr in msg.recipients)
        # 发送
        await server.send_message(mail_msg)