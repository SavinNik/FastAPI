import uvicorn
from fastapi import FastAPI, HTTPException

from app.constants import SUCCESS_RESPONSE
from app.crud import add_item, get_item_by_id, delete_item, update_item
from app.schema import (CreateAdvertisementRequest, UpdateAdvertisementRequest, CreateAdvertisementResponse,
                        GetAdvertisementResponse, SearchAdvertisementResponse, UpdateAdvertisementResponse,
                        DeleteAdvertisementResponse, LoginResponse, LoginRequest, CreateUserResponse, CreateUserRequest,
                        UpdateUserRequest, UpdateUserResponse, DeleteUserResponse, GetUserResponse)
from app.lifespan import lifespan
from app.auth import hash_password, check_password, check_permissions
from app.dependancy import SessionDependancy, TokenDependancy

from app.models import Advertisement, User, Token

from sqlalchemy import select

app = FastAPI(
    title="Advertisement API",
    description="list of advertisements",
    lifespan=lifespan
)


@app.post("/api/v1/advertisement", tags=['advertisement'], response_model=CreateAdvertisementResponse)
async def create_advertisement(advertisement: CreateAdvertisementRequest, session: SessionDependancy,
                               token: TokenDependancy):
    adv_dict = advertisement.model_dump(exclude_unset=True)
    adv_orm_obj = Advertisement(**adv_dict, user_id=token.user_id)
    check_permissions(token.user, adv_orm_obj.user_id)
    await add_item(session, adv_orm_obj)
    return adv_orm_obj.id_dict


@app.get("/api/v1/advertisement/{advertisement_id}", tags=['advertisement'], response_model=GetAdvertisementResponse)
async def get_advertisement(advertisement_id: int, session: SessionDependancy):
    adv_orm_obj = await get_item_by_id(session, Advertisement, advertisement_id)
    return adv_orm_obj.dict


@app.patch("/api/v1/advertisement/{advertisement_id}", tags=['advertisement'],
           response_model=UpdateAdvertisementResponse)
async def update_advertisement(advertisement_id: int, advertisement_data: UpdateAdvertisementRequest,
                               session: SessionDependancy, token: TokenDependancy):
    adv_dict = advertisement_data.model_dump(exclude_unset=True)
    adv_orm_obj = await get_item_by_id(session, Advertisement, advertisement_id)
    check_permissions(token.user, adv_orm_obj.user_id)
    await update_item(session, adv_orm_obj, adv_dict)
    return SUCCESS_RESPONSE


@app.delete("/api/v1/advertisement/{advertisement_id}", tags=['advertisement'],
            response_model=DeleteAdvertisementResponse)
async def delete_advertisement(advertisement_id: int, session: SessionDependancy, token: TokenDependancy):
    adv_orm_obj = await get_item_by_id(session, Advertisement, advertisement_id)
    check_permissions(token.user, adv_orm_obj.user_id)
    await delete_item(session, adv_orm_obj)
    return SUCCESS_RESPONSE


@app.get("/api/v1/advertisement", tags=['advertisement'], response_model=SearchAdvertisementResponse)
async def search_advertisement(session: SessionDependancy,
                               title: str | None = None,
                               description: str | None = None,
                               price: float | None = None,
                               author: str | None = None,
                               status_open: bool | None = None):
    query = select(Advertisement)

    if title:
        query = query.filter(Advertisement.title.ilike(f'%{title}%'))
    if description:
        query = query.filter(Advertisement.description.ilike(f'%{description}%'))
    if price:
        query = query.filter(Advertisement.price == price)
    if author:
        query = query.join(User).filter(User.name == author)
    if status_open:
        query = query.filter(Advertisement.status_open == status_open)

    result = await session.execute(query)
    advertisements = result.unique().scalars().all()
    return {'advertisements': [adv.dict for adv in advertisements]}


@app.post("/api/v1/login", tags=['login'], response_model=LoginResponse)
async def login(login_data: LoginRequest, session: SessionDependancy):
    query = select(User).where(User.name == login_data.name)
    result = await session.execute(query)
    user = result.scalars().first()

    if user is None:
        raise HTTPException(401, "Invalid credentials")
    if not check_password(login_data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    token = Token(user_id=user.id)
    await add_item(session, token)
    return token.dict


@app.post("/api/v1/user", tags=['users'], response_model=CreateUserResponse)
async def create_user(user_data: CreateUserRequest, session: SessionDependancy):
    user_dict = user_data.model_dump(exclude_unset=True)
    user_dict['password'] = hash_password(user_dict['password'])
    user_orm_obj = User(**user_dict)
    await add_item(session, user_orm_obj)
    return user_orm_obj.id_dict


@app.get("/api/v1/user/{user_id}", tags=['users'], response_model=GetUserResponse)
async def get_user(user_id: int, session: SessionDependancy):
    user_orm_obj = await get_item_by_id(session, User, user_id)
    return user_orm_obj.id_dict


@app.patch("/api/v1/user/{user_id}", tags=['users'], response_model=UpdateUserResponse)
async def update_user(user_id: int, user_data: UpdateUserRequest, session: SessionDependancy, token: TokenDependancy):
    user_dict = user_data.model_dump(exclude_unset=True)
    user_orm_obj = await get_item_by_id(session, User, user_id)
    check_permissions(token.user, user_orm_obj.id)
    await update_item(session, user_orm_obj, user_dict)
    return SUCCESS_RESPONSE


@app.delete("/api/v1/user/{user_id}", tags=['users'], response_model=DeleteUserResponse)
async def delete_user(user_id: int, session: SessionDependancy, token: TokenDependancy):
    user_orm_obj = await get_item_by_id(session, User, user_id)
    check_permissions(token.user, user_orm_obj.id)
    await delete_item(session, user_orm_obj)
    return SUCCESS_RESPONSE


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=80)
