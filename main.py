from fastapi import FastAPI
from sqlalchemy import text

import models
from cache import get_cached_data, refresh_cached_data
from models import db_session_bancho, Score
from performance import calculate

app = FastAPI()


@app.on_event("startup")
async def create_table():
    await models.create_db_and_tables()


@app.get("/calc/all")
async def calc_all():
    await gen_for_all()


@app.get("/calc/mode")
async def calc_mode(mode: int):
    await gen_for_mode(mode)


@app.get("/calc/player")
async def calc_player(player_id: int, mode: int):
    await gen_for_player_mode(player_id, mode)


@app.get("/data/all")
async def fetch_all():
    return await get_cached_data("mode_12")


@app.get("/data/mode")
async def fetch_mode(mode: int):
    return await get_cached_data("mode_" + str(mode))


@app.get("/data/player")
async def fetch_player(player_id: int, mode: int):
    return await get_cached_data(f"player_{player_id}_{mode}")


async def insert_data(sentence, source):
    async with db_session_bancho() as session:
        result_best = await session.execute(sentence)
        for score in result_best.all():
            calc_result = calculate(score.beatmap_id, score.mods, score.mode, score.acc, score.ngeki
                                    , score.nkatu, score.n300, score.n100, score.n50, score.nmiss, score.max_combo)
            # Beatmap not exist or something else
            if calc_result[2] < 1.00:
                print("Beatmap skipped" + str(score.beatmap_id))
                continue
            score = Score(score_id=score.id, map_id=score.beatmap_id, old_pp=score.pp, new_pp=calc_result[2],
                          difficulty_attributes=calc_result[0], performance_attributes=calc_result[1],
                          source=source)
            session.add(score)
            await refresh_cached_data(source)


async def gen_for_all():
    sentence = text("select maps.id as beatmap_id, scores.* from scores left join users on "
                    "scores.userid=users.id left join maps on scores.map_md5=maps.md5 where "
                    "users.priv>2 and maps.status=2 order by scores.pp desc limit 100")
    await insert_data(sentence, "mode_12")


async def gen_for_mode(mode: int):
    sentence = text("select maps.id as beatmap_id, scores.* from scores left join users on "
                    "scores.userid=users.id left join maps on scores.map_md5=maps.md5 where "
                    "users.priv>2 and maps.status=2 and scores.mode=:mode"
                    " order by scores.pp desc limit 100").bindparams(mode=mode)
    await insert_data(sentence, f"mode_{mode}")


async def gen_for_player_mode(player_id: int, mode: int):
    sentence = text("select maps.id as beatmap_id, scores.* from scores left join users on "
                    "scores.userid=users.id left join maps on scores.map_md5=maps.md5 where "
                    "users.priv>2 and maps.status=2 and scores.mode=:mode and userid=:player_id"
                    " order by scores.pp desc limit 100").bindparams(mode=mode, player_id=player_id)
    await insert_data(sentence, f"player_{player_id}_{mode}")
