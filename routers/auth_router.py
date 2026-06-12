import string
import random
from fastapi import APIRouter, Query, Depends, HTTPException
from jinja2.compiler import Frame
from pydantic import EmailStr
from typing import Annotated

from core.mail import send_email
from dependencies import get_mail, get_session
from fastapi_mail import FastMail, MessageSchema, MessageType
from models import AsyncSession
from repository.user_repo import EmailCodeRepository
from schemas import ResponseModel

from schemas import ResponseModel

router = APIRouter(prefix="/auth", tags=["user"])


@router.get("/code", response_model=ResponseModel)
async def get_email_code(
        email: Annotated[EmailStr, Query(...)],
        mail: FastMail = Depends(get_mail),
        session: AsyncSession = Depends(get_session)

):
    # 1.生成4为数字的验证码
    source = string.digits * 4
    code = "".join(random.sample(source, 4))
    # 2.创建消息对象
    message = MessageSchema(
        subject="注册代码",
        recipients=[email],
        body=f"您的验证码为{code},5分钟有效",
        subtype=MessageType.plain
    )
    try:
        await send_email(mail,message)
    except Exception as e:
        if e.code == -1 and b"\\x00\\x00\x00" in str(e).encode():
            print("报错，但是邮箱已经发送")
            email_code_repo = EmailCodeRepository(session=session)
            await email_code_repo.create(email=str(email), code=code)
        else:
            raise HTTPException(status_code=500, detail="邮件发送失败")
    return ResponseModel




