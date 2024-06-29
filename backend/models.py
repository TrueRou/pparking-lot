# coding: utf-8
import contextlib
import json
from typing import AsyncContextManager

from sqlalchemy import JSON
from sqlalchemy import CHAR, Column, DateTime, Enum, Float, Integer, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import db_dsn

Base = declarative_base()
LazyBase = declarative_base()

bancho_engine = create_async_engine(db_dsn)
async_session_maker_bancho = sessionmaker(bancho_engine, class_=AsyncSession, expire_on_commit=False)


@contextlib.asynccontextmanager
async def db_session_bancho() -> AsyncContextManager[AsyncSession]:
    async with async_session_maker_bancho() as session:
        yield session
        await session.commit()


async def create_db_and_tables():
    async with bancho_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Score(Base):
    __tablename__ = "performance_rework"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    score_id = Column(BIGINT, nullable=False)
    map_id = Column(Integer, nullable=False)
    old_pp = Column(Float(7), nullable=False)
    new_pp = Column(Float(7), nullable=False)
    difficulty_attributes = Column(JSON, nullable=True)
    performance_attributes = Column(JSON, nullable=True)
    strains = Column(JSON, nullable=True)
    performance_vn = Column(JSON, nullable=True)
    source = Column(String(64), nullable=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "old_pp": self.old_pp,
            "new_pp": self.new_pp,
            "difficulty_attributes": json.loads(self.difficulty_attributes or "{}"),
            "performance_attributes": json.loads(self.performance_attributes or "{}"),
            "performance_vn": json.loads(self.performance_vn or "{}"),
            # No longer provide analysis data because too large.
        }

    def get_analysis_data(self):
        return json.loads(self.analysis_data or "{}")


class Map(LazyBase):
    __tablename__ = "maps"

    server = Column(Enum("osu!", "private"), primary_key=True, nullable=False, server_default=text("'osu!'"))
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    set_id = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    md5 = Column(CHAR(32), nullable=False, unique=True)
    artist = Column(String(128), nullable=False)
    title = Column(String(128), nullable=False)
    version = Column(String(128), nullable=False)
    creator = Column(String(19), nullable=False)
    filename = Column(String(256), nullable=False, index=True)
    last_update = Column(DateTime, nullable=False)
    total_length = Column(Integer, nullable=False)
    max_combo = Column(Integer, nullable=False)
    frozen = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    plays = Column(Integer, nullable=False, server_default=text("'0'"))
    passes = Column(Integer, nullable=False, server_default=text("'0'"))
    mode = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    bpm = Column(Float(12), nullable=False, server_default=text("'0.00'"))
    cs = Column(Float(4), nullable=False, server_default=text("'0.00'"))
    ar = Column(Float(4), nullable=False, server_default=text("'0.00'"))
    od = Column(Float(4), nullable=False, server_default=text("'0.00'"))
    hp = Column(Float(4), nullable=False, server_default=text("'0.00'"))
    diff = Column(Float(6), nullable=False, server_default=text("'0.000'"))

    def to_dict(self):
        return {"id": self.id, "title": self.title, "version": self.version, "set_id": self.set_id}


class ScoreFull(LazyBase):
    __tablename__ = "scores"

    id = Column(BIGINT, primary_key=True)
    map_md5 = Column(CHAR(32), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    pp = Column(Float(7), nullable=False)
    acc = Column(Float(6), nullable=False)
    max_combo = Column(Integer, nullable=False)
    mods = Column(Integer, nullable=False)
    n300 = Column(Integer, nullable=False)
    n100 = Column(Integer, nullable=False)
    n50 = Column(Integer, nullable=False)
    nmiss = Column(Integer, nullable=False)
    ngeki = Column(Integer, nullable=False)
    nkatu = Column(Integer, nullable=False)
    grade = Column(String(2), nullable=False, server_default=text("'N'"))
    status = Column(TINYINT, nullable=False)
    mode = Column(TINYINT, nullable=False)
    play_time = Column(DateTime, nullable=False)
    time_elapsed = Column(Integer, nullable=False)
    client_flags = Column(Integer, nullable=False)
    userid = Column(Integer, nullable=False, index=True)
    perfect = Column(TINYINT(1), nullable=False)
    online_checksum = Column(CHAR(32), nullable=False)

    def to_dict(self):
        return {
            "acc": self.acc,
            "nmiss": self.nmiss,
        }
