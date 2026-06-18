from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime
from enum import Enum
import secrets
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
import jwt

from threading import Lock

import settings


class SingletonMeta(type):
    _instance = {}
    _lock:Lock = Lock()
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instance:
                instance = super().__call__(*args, **kwargs)
                cls._instance[cls] = instance
        return cls._instance[cls]

# token类枚举
class TokenTypeEnum(Enum):
    ACCESS_TOKEN = 1
    REFRESH_TOKEN = 2

class AuthHandler(metaclass=SingletonMeta):
    security = HTTPBearer()

    secret = settings.JWT_SECRET_KEY

    # token编码加密
    def _encode_token(self, user_id: int, type: TokenTypeEnum):
        payload = dict(
            iss=str(user_id),
            sub=int(type.value)
        )
        to_encode = payload.copy()
        if type == TokenTypeEnum.ACCESS_TOKEN:
            exp = datetime.now() + settings.JWT_ACCESS_TOKEN_EXPIRES
        else:
            exp = datetime.now() + settings.JWT_REFRESH_TOKEN_EXPIRES
        to_encode.update({"exp": int(exp.timestamp())})
        return jwt.encode(to_encode, self.secret, algorithm='HS256')

    def encode_login_token(self, user_id: int):
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        refresh_token = self._encode_token(user_id, TokenTypeEnum.REFRESH_TOKEN)
        login_token = dict(
            access_token= f"{access_token}",
            refresh_token= f"{refresh_token}"
        )
        return login_token

    def encode_update_token(self, user_id: int):
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)

        update_token = dict(
            access_token= f"{access_token}",
        )
        return update_token

    # 解码token
    def decode_access_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['sub'] != int(TokenTypeEnum.ACCESS_TOKEN.value):
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="TOKEN类型错误！")
            return payload['iss']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="ACCESS TOKEN已经过期")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="ACCESS TOKEN不可用")

    def decode_refresh_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['sub'] != int(TokenTypeEnum.REFRESH_TOKEN.value):
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="TOKEN类型错误！")
            return payload['iss']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="ACCESS TOKEN已经过期")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="ACCESS TOKEN不可用")

    # TOKEN使用
    def auth_access_dependency(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_access_token(auth.credentials)

    def auth_refresh_dependency(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_refresh_token(auth.credentials)