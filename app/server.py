import uvicorn
from fastapi import FastAPI

from app.constants import SUCCESS_RESPONSE
from app.crud import add_item, get_item_by_id, delete_item
from app.schema import (CreateAdvertisementRequest, UpdateAdvertisementRequest, CreateAdvertisementResponse,
                    GetAdvertisementResponse, SearchAdvertisementResponse, UpdateAdvertisementResponse,
                    DeleteAdvertisementResponse)
from app.lifespan import lifespan
from app.dependancy import SessionDependancy

from app.models import Advertisement

from sqlalchemy import select

app = FastAPI(
    title="Advertisement API",
    description="list of advertisements",
    lifespan=lifespan
)


@app.post("/api/v1/advertisement", tags=['advertisement'], response_model=CreateAdvertisementResponse)
async def create_advertisement(advertisement: CreateAdvertisementRequest, session: SessionDependancy):
    adv_dict = advertisement.model_dump(exclude_unset=True)
    adv_orm_obj = Advertisement(**adv_dict)
    await add_item(session, adv_orm_obj)
    return adv_orm_obj.id_dict


@app.get("/api/v1/advertisement/{advertisement_id}", tags=['advertisement'], response_model=GetAdvertisementResponse)
async def get_advertisement(advertisement_id: int, session: SessionDependancy):
    adv_orm_obj = await get_item_by_id(session, Advertisement, advertisement_id)
    return adv_orm_obj.dict


@app.patch("/api/v1/advertisement/{advertisement_id}", tags=['advertisement'],
           response_model=UpdateAdvertisementResponse)
async def update_advertisement(advertisement_id: int, advertisement_data: UpdateAdvertisementRequest,
                               session: SessionDependancy):
    adv_dict = advertisement_data.model_dump(exclude_unset=True)
    adv_orm_obj = await get_item_by_id(session, Advertisement, advertisement_id)

    for field, value in adv_dict.items():
        setattr(adv_orm_obj, field, value)
    await add_item(session, adv_orm_obj)
    return SUCCESS_RESPONSE


@app.delete("/api/v1/advertisement/{advertisement_id}", tags=['advertisement'],
            response_model=DeleteAdvertisementResponse)
async def delete_advertisement(advertisement_id: int, session: SessionDependancy):
    adv_orm_obj = await get_item_by_id(session, Advertisement, advertisement_id)

    if adv_orm_obj:
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
        query = query.filter(Advertisement.author == author)
    if status_open:
        query = query.filter(Advertisement.status_open == status_open)


    result = await session.execute(query)
    advertisements = result.scalars().all()
    return {'advertisements': [adv.dict for adv in advertisements]}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=80)
