import os
import datetime
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

from sqlalchemy import Integer, String, Float, Boolean, DateTime, func, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from app.custom_types import ROLE

POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):

    @property
    def id_dict(self):
        return {"id": self.id}


class Token(Base):
    __tablename__ = "token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, server_default=func.gen_random_uuid())
    creation_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship("User", lazy="joined", back_populates="tokens")

    @property
    def dict(self):
        return {"token": self.token}


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    tokens: Mapped[list["Token"]] = relationship(Token, lazy="joined", back_populates="user")
    role: Mapped[ROLE] = mapped_column(String, default="user")
    advertisements: Mapped[list["Advertisement"]] = relationship("Advertisement", lazy="joined", back_populates="user")

    @property
    def id_dict(self):
        return {"id": self.id, "name": self.name, "role": self.role}


class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    creation_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    status_open: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship("User", lazy="joined", back_populates="advertisements")

    @property
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "author": self.user.name,
            "creation_date": self.creation_date,
            "status_open": self.status_open,
            "user_id": self.user_id
        }


ORM_OBJ = Advertisement | User | Token
ORM_CLS = type[Advertisement] | type[User] | type[Token]


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()


