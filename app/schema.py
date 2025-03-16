from pydantic import BaseModel
import datetime
from typing import Literal


# Requests

class CreateAdvertisementRequest(BaseModel):
    title: str
    description: str
    price: float
    author: str
    status_open: bool


class UpdateAdvertisementRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    status_open: bool | None = None


# Responses

class CreateAdvertisementResponse(BaseModel):
    id: int


class GetAdvertisementResponse(BaseModel):
    title: str
    description: str
    price: float
    author: str
    creation_date: datetime.datetime
    status_open: bool


class SearchAdvertisementResponse(BaseModel):
    advertisements: list[GetAdvertisementResponse]


class SuccessResponse(BaseModel):
    status: Literal["success"]


class UpdateAdvertisementResponse(SuccessResponse):
    pass


class DeleteAdvertisementResponse(SuccessResponse):
    pass
