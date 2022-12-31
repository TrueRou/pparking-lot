# coding: utf-8
import contextlib
from typing import AsyncContextManager

from sqlalchemy import Column, Float, Integer, String, JSON
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
metadata = Base.metadata

bancho_engine = create_async_engine('mysql+aiomysql://root@localhost:3306/banchopy')
pparking_engine = create_async_engine('sqlite+aiosqlite:///./pparking.sqlite?check_same_thread=False')
async_session_maker_bancho = sessionmaker(bancho_engine, class_=AsyncSession, expire_on_commit=False)
async_session_maker_pparking = sessionmaker(pparking_engine, class_=AsyncSession, expire_on_commit=False)


@contextlib.asynccontextmanager
async def db_session_bancho() -> AsyncContextManager[AsyncSession]:
    async with async_session_maker_bancho() as session:
        yield session
        await session.commit()


@contextlib.asynccontextmanager
async def db_session_pparking() -> AsyncContextManager[AsyncSession]:
    async with async_session_maker_pparking() as session:
        yield session
        await session.commit()


async def create_db_and_tables():
    async with pparking_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Score(Base):
    __tablename__ = 'scores'

    id = Column(BIGINT, primary_key=True)
    map_id = Column(Integer, nullable=False)
    old_pp = Column(Float(7), nullable=False)
    new_pp = Column(Float(7), nullable=False)
    difficulty_attributes = Column(JSON, nullable=True)
    performance_attributes = Column(JSON, nullable=True)
    strains = Column(JSON, nullable=True)
    analysis_data = Column(JSON, nullable=True)
    source = Column(String(64), nullable=False)
