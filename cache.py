import json

from sqlalchemy import select

import models
from models import db_session_bancho, Score
from mods import Mods
from performance import calculate_prepend

cache_dict = {}
prepend_maps = [(2486881, 99.0, "HDDTRX")]


async def get_cached_data(source: str):
    value = cache_dict[source] if source in cache_dict and cache_dict[source] != {} else await fetch_data(source)
    cache_dict[source] = value
    return value


async def refresh_cached_data(source: str):
    cache_dict[source] = {}


async def fetch_data(source: str):
    if source == "prepend":
        return await get_prepend_data()
    result = []
    async with db_session_bancho() as session:
        records = (await session.execute(
            select(Score).where(Score.source == source).order_by(Score.new_pp.desc()))).scalars().all()
        for record in records:
            score_obj: models.ScoreFull = await session.get(models.ScoreFull, record.score_id)
            score_dict = score_obj.to_dict()
            score_dict["mods_str"] = str(Mods(score_obj.mods))
            result.append({
                "performance": record.to_dict(),
                "beatmap": (await session.get(models.Map, ["osu!", record.map_id])).to_dict(),
                "score": score_dict,
                "user": (await session.get(models.User, score_obj.userid)).to_dict(),
            })
    return result


async def get_prepend_data():
    async with db_session_bancho() as session:
        result = []
        for item in prepend_maps:
            mods = Mods.from_modstr(item[2])
            calc_result = calculate_prepend(item[0], mods.value, item[1])
            result.append({
                "beatmap": (await session.get(models.Map, ["osu!", item[0]])).to_dict(),
                "performance": {
                    "difficulty_attributes": json.loads(calc_result[0] or "{}"),
                    "performance_attributes": json.loads(calc_result[1] or "{}"),
                    "analysis_data": {},
                    "new_pp": calc_result[2],
                },
                "score": {
                    "acc": item[1],
                    "mods_str": item[2]
                }
            })
        return result
