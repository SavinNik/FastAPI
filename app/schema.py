from pydantic import BaseModel
import datetime
import uuid
from typing import Literal
from app.custom_types import ROLE


# =====================
# =       Requests    =
# =====================

# Advertisement requests

class CreateAdvertisementRequest(BaseModel):
    title: str
    description: str
    price: float
    status_open: bool


class UpdateAdvertisementRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    status_open: bool | None = None



# User requests

class LoginRequest(BaseModel):
    name: str
    password: str


class CreateUserRequest(BaseModel):
    name: str
    password: str
    role: ROLE


class UpdateUserRequest(BaseModel):
    name: str | None = None
    password: str | None = None
    role: ROLE | None = None


# =====================
# =       Responses   =
# =====================

# Advertisement responses

class IdResponse(BaseModel):
    id: int


class CreateAdvertisementResponse(IdResponse):
    pass


class GetAdvertisementResponse(BaseModel):
    title: str
    description: str
    price: float
    author: str
    creation_date: datetime.datetime
    status_open: bool
    user_id: int


class SearchAdvertisementResponse(BaseModel):
    advertisements: list[GetAdvertisementResponse]


class SuccessResponse(BaseModel):
    status: Literal["success"]


class UpdateAdvertisementResponse(SuccessResponse):
    pass


class DeleteAdvertisementResponse(SuccessResponse):
    pass


# User responses

class LoginResponse(BaseModel):
    token: uuid.UUID


class CreateUserResponse(IdResponse):
    pass


class GetUserResponse(BaseModel):
    name: str
    role: ROLE


class UpdateUserResponse(SuccessResponse):
    pass


class DeleteUserResponse(SuccessResponse):
    pass
