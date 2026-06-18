
from models import AsyncSession
from models.user import EmailCode, User
from sqlalchemy import select, exists
from datetime import datetime, timedelta
from schemas.user import UserCreateSchema


class EmailCodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 创建邮件验证码
    async def create(self, email: str, code: str) -> EmailCode:
        async with self.session.begin():
            email_code = EmailCode(email=email, code=code)
            self.session.add(email_code)
            return email_code

    # 检验邮箱验证码
    async def check_email_code(self, email: str, code: str) -> bool:
        async with self.session.begin():
            # 相当于写sql语句
            stmt = select(EmailCode).where(EmailCode.email == email,
                                           EmailCode.code == code)
            # session.scalar()查找数据，相当于select
            email_code: EmailCode | None = await self.session.scalar(stmt)
            if email_code is None:
                return False
            # 验证码过期时间5分钟
            if (datetime.now() - email_code.created_time) > timedelta(minutes=5):
                return False
            return True


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 通过用户获取到邮箱
    async def get_by_email(self, email: str) -> User | None:
        async with self.session.begin():
            return await self.session.scalar(select(User).where(User.email == email))

    # 判断邮箱是否存在
    async def email_is_exist(self, email: str) -> bool:
        async with self.session.begin():
            stmt = select(exists().where(User.email == email))
            return await self.session.scalar(stmt)

    # 创建用户
    async def create(self, user_schema: UserCreateSchema) -> User:
        async with self.session.begin():
            user = User(**user_schema.model_dump())  # 转化成字典和关键字参数
            self.session.add(user)
            return user
