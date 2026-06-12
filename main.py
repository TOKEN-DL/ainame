# 放在文件第一行
import os

from core.mail import send_email

# 强制覆盖本机hostname，纯英文无中文
os.environ["HOSTNAME"] = "mail-client-en"

from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi import Depends
from dependencies import get_mail
from routers.auth_router import router as auth_router


app = FastAPI()

# 导入用户路由
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/mail/test")
async def mail_test(
        email: str,
        mail: FastMail =Depends(get_mail),
):
    message = MessageSchema(
        subject="hello",
        recipients=[email],
        body=f"hello{email}",
        subtype=MessageType.plain,

    )
    await send_email(mail, message)
    return {"message": "邮件发送成功"}
