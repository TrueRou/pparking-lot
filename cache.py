from sqlalchemy import select

import models
from models import db_session_bancho, Score
from mods import Mods

cache_dict: dict = {}


async def get_cached_data(source: str):
    value = cache_dict[source] if source in cache_dict and cache_dict[source] != {} else await fetch_data(source)
    cache_dict[source] = value
    return value


async def refresh_cached_data(source: str):
    cache_dict[source] = {}


async def fetch_data(source: str):
    result = []
    async with db_session_bancho() as session:
        records = (await session.execute(
            select(Score).where(Score.source == source).order_by(Score.new_pp.desc()))).scalars().all()
        for record in records:
            score_obj: models.ScoreFull = await session.get(models.ScoreFull, record.score_id)
            score_dict = score_obj.to_dict()
            score_dict["mods_str"] = repr(Mods(score_obj.mods))
            result.append({
                "performance": record.to_dict(),
                "beatmap": (await session.get(models.Map, ["osu!", record.map_id])).to_dict(),
                "score": score_dict,
            })
    return result


async def fetch_analysis_data(database_score_id: int):
    async with db_session_bancho() as session:
        score_obj: models.Score = await session.get(models.Score, database_score_id)
        if score_obj is not None:
            return score_obj.get_analysis_data()
