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
from models.user import User
from repository.user_repo import EmailCodeRepository, UserRepository

from schemas import ResponseOut
from schemas.user import RegisterIn, UserCreateSchema, LoginIn, LoginOut
from core.auth import AuthHandler

router = APIRouter(prefix="/auth", tags=["user"])

auth_handler = AuthHandler()

# 发送邮箱码接口
@router.get("/code", response_model=ResponseOut)
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

    await send_email(mail,message) # 发送邮箱


    email_code_repo = EmailCodeRepository(session=session)
    await email_code_repo.create(email=str(email), code=code)
    # else:
    #     raise HTTPException(status_code=500, detail="邮件发送失败")
    return ResponseOut

# 注册接口
@router.post("/register", response_model=ResponseOut)
async def register(
        data: RegisterIn,
        session: AsyncSession = Depends(get_session),

):
    # 1. 判断邮箱是否存在
    user_repo = UserRepository(session=session)
    email_exist = await user_repo.email_is_exist(email=str(data.email))
    if email_exist:
        raise HTTPException(status_code=400, detail="该邮箱已经存在！")
    # 2.校验验证码是否正确
    email_code_repo = EmailCodeRepository(session=session)
    email_code_match = await email_code_repo.check_email_code(email=str(data.email),
                                                        code=str(data.code))
    if not email_code_match:
        raise HTTPException(status_code=400, detail="邮箱或者验证码错误")
    #3. 创建用户
    try:
        await user_repo.create(UserCreateSchema(email=data.email, password=data.password,
                                                username=data.username))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ResponseOut

# 登录接口
@router.post("/login", response_model=LoginOut)
async def login(
        data: LoginIn,
        session: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(session=session)
    # 根据邮箱查找用户
    user: User | None = await user_repo.get_by_email(email=str(data.email))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.check_password(str(data.password)):
        raise HTTPException(status_code=400, detail="密码不正确")
    # 生成JWToekn
    tokens = auth_handler.encode_login_token(user.id)
    return {
        "user":user,
        "token":tokens['access_token']
    }








