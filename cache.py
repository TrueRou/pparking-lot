from sqlalchemy import select

import models
from models import db_session_bancho, Score

cache_dict = {}


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
            result.append({
                "performance": record.to_dict(),
                "beatmap": (await session.get(models.Map, ["osu!", record.map_id])).to_dict(),
                "score": score_obj.to_dict(),
                "user": (await session.get(models.User, score_obj.userid)).to_dict(),
            })
    return result

