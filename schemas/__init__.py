from pydantic import BaseModel, Field
from typing import Annotated, Literal


class ResponseModel(BaseModel):
    result: Annotated[Literal["success", "failure"], Field("success", description="操作结果！")]