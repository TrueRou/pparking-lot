from fastapi import FastAPI
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware

import cache
import models
from cache import get_cached_data, refresh_cached_data
from models import db_session_bancho, Score
from performance import calculate

app = FastAPI()

origins = [
    "http://localhost:5173",  # yarn dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await models.create_db_and_tables()
    cache.read_cache()
    await cache.refresh_cached_data("prepend")


@app.on_event("shutdown")
def shutdown_event():
    cache.save_cache()


@app.patch("/scores/mode")
async def patch_mode(mode: int):
    await update_mode(mode)


@app.patch("/scores/player")
async def patch_player(player_id: int, mode: int):
    await update_player_mode(player_id, mode)


@app.get("/scores/prepend")
async def fetch_prepend():
    return await get_cached_data("prepend")


@app.get("/scores/mode")
async def fetch_mode(mode: int):
    return await get_cached_data("mode_" + str(mode))


@app.get("/scores/player")
async def fetch_player(player_id: int, mode: int):
    return await get_cached_data(f"player_{player_id}_{mode}")


@app.get("/scores/analysis")
async def fetch_score(database_score_id: int):
    return await cache.fetch_analysis_data(database_score_id)


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
                          source=source, analysis_data=calc_result[3], performance_vn=calc_result[4])
            session.add(score)
            await refresh_cached_data(source)


async def delete_data(source):
    async with db_session_bancho() as session:
        await session.execute(text("delete from scores_analysis where source=:source").bindparams(source=source))


async def update_mode(mode: int):
    await delete_data(f"mode_{mode}")
    sentence = text("select maps.id as beatmap_id, scores.* from scores left join users on "
                    "scores.userid=users.id left join maps on scores.map_md5=maps.md5 where "
                    "users.priv>2 and maps.status=2 and scores.mode=:mode and scores.status=2"
                    " order by scores.pp desc limit 100").bindparams(mode=mode)
    await insert_data(sentence, f"mode_{mode}")


async def update_player_mode(player_id: int, mode: int):
    await delete_data(f"player_{player_id}_{mode}")
    sentence = text("select maps.id as beatmap_id, scores.* from scores left join users on "
                    "scores.userid=users.id left join maps on scores.map_md5=maps.md5 where "
                    "users.priv>2 and maps.status=2 and scores.mode=:mode and userid=:player_id "
                    "and scores.status=2 order by scores.pp desc limit 100").bindparams(mode=mode, player_id=player_id)
    await insert_data(sentence, f"player_{player_id}_{mode}")
