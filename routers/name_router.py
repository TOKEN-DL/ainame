from fastapi import APIRouter,Depends


from schemas.name import NameIn, NameOut
from core.agent import  generate_names
from core.auth import AuthHandler

auth_handler = AuthHandler()

router = APIRouter(prefix="/name", tags=["name"])

@router.get("/", response_model=NameOut)
async def take_names(
        data: NameIn,
        # 验证用户是否登录
        user_id: int=Depends(auth_handler.auth_access_dependency)):
    name_result = await generate_names(data)
    return NameOut(names=name_result.names)
