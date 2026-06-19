from pydantic import BaseModel, Field
from typing import Annotated, List


# 名字模型
class NameSchema(BaseModel):
    name: Annotated[str, Field(...,description="姓名")]
    reference: Annotated[str, Field(...,description="出处")]
    moral: Annotated[str, Field(...,description="寓意")]

# 多个名字
class NameResultSchema(BaseModel):
    names: List[NameSchema]