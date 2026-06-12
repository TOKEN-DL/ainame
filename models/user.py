from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime
from pwdlib import PasswordHash
from datetime import datetime

password_hash = PasswordHash.recommended()


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(100))
    _password: Mapped[str] = mapped_column(String(200))

    # 关键字已知参数**kwargs   未知参数*args
    def __init__(self, *args, **kwargs):
        password = kwargs.pop('password')
        super().__init__(*args, **kwargs)
        # 密码加密
        if password:
            self.password = password

    # 相当于get方法
    @property
    def password(self):
        return self._password

    # 相当于set方法
    @password.setter
    def password(self, raw_password):
        self._password = password_hash.hash(raw_password)

    # 验证密码，原始密码和加密密码进行对比
    def check_password(self, raw_password):
        return password_hash.verify(raw_password, self.password)


class EmailCode(Base):
    __tablename__ = 'email_code'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(10))
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)




