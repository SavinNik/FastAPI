import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Header, HTTPException
import uuid

from app.models import Session, Token
from app.constants import TOKEN_TTL_SEC

from typing import Annotated


async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session


SessionDependancy = Annotated[AsyncSession, Depends(get_session, use_cache=True)]


async def get_token(
        x_token: Annotated[uuid.UUID, Header()],
        session: SessionDependancy
) -> Token:
    query = select(Token).where(Token.token == x_token, Token.creation_time >= (
            datetime.datetime.now() - datetime.timedelta(seconds=TOKEN_TTL_SEC)))
    result = await session.execute(query)
    token = result.scalars().first()

    if token is None:
        raise HTTPException(401, "Token not found")
    return token


TokenDependancy = Annotated[Token, Depends(get_token)]
