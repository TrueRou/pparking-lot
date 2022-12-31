# Config
import asyncio

from sqlalchemy import text

from models import db_session_bancho, db_session_pparking, Score, create_db_and_tables
from performance import calculate


async def init():
    await create_db_and_tables()


async def insert_datas(sentence, source):
    async with db_session_bancho() as session:
        result_best = await session.execute(sentence)
        async with db_session_pparking() as pparking:
            for score in result_best.all():
                calc_result = calculate(score.beatmap_id, score.mods, score.mode, score.acc, score.ngeki
                                        , score.nkatu, score.n300, score.n100, score.n50, score.nmiss, score.max_combo)
                # Beatmap not exist or something else
                if calc_result[3] < 1.00:
                    print("Beatmap skipped" + str(score.beatmap_id))
                    continue
                score = Score(id=score.id, map_id=score.beatmap_id, old_pp=score.pp, new_pp=calc_result[3],
                              difficulty_attributes=calc_result[0], performance_attributes=calc_result[1],
                              strains=calc_result[2], source=source)
                pparking.add(score)
                await pparking.commit()


async def gen_for_all():
    sentence = text("select maps.id as beatmap_id, scores.* from scores left join users on "
                    "scores.userid=users.id left join maps on scores.map_md5=maps.md5 where "
                    "users.priv>2 and maps.status=2 order by scores.pp desc limit 100")
    await insert_datas(sentence, "mode_12")


async def gen_for_mode(mode: int):
    sentence = text("select maps.id as beatmap_id, scores.* from scores left join users on "
                    "scores.userid=users.id left join maps on scores.map_md5=maps.md5 where "
                    "users.priv>2 and maps.status=2 and mode=:mode"
                    " order by scores.pp desc limit 100").bindparams(mode=mode)
    await insert_datas(sentence, f"mode_{mode}")


async def gen_for_player_mode(player_id: int, mode: int):
    sentence = text("select maps.id as beatmap_id, scores.* from scores left join users on "
                    "scores.userid=users.id left join maps on scores.map_md5=maps.md5 where "
                    "users.priv>2 and maps.status=2 and mode=:mode and userid=:player_id"
                    " order by scores.pp desc limit 100").bindparams(mode=mode, player_id=player_id)
    await insert_datas(sentence, f"player_{player_id}_{mode}")


if __name__ == '__main__':
    asyncio.run(init())
    asyncio.run(gen_for_all())
