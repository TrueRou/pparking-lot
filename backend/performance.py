from __future__ import annotations

import json
from os import path

from rosu_pp_py import Beatmap, Difficulty, GameMode, Performance

from config import osu_folder_path
from mods import Mods


def to_dic(obj):
    dic = {}
    for field_key in dir(obj):
        field_value = getattr(obj, field_key)
        if (
            not field_key.startswith("__")
            and not callable(field_value)
            and not field_key.startswith("_")
            and field_key != "difficulty"
            and field_key != "state"
            and field_key != "mode"
        ):
            dic[field_key] = field_value
    return dic


def json_dump(obj):
    return json.dumps(to_dic(obj))


gm_dict: dict[int, GameMode] = {
    0: GameMode.Osu,
    1: GameMode.Taiko,
    2: GameMode.Catch,
    3: GameMode.Mania,
}


def get_mode(mode: int) -> GameMode:
    return gm_dict[mode]


def calculate(
    beatmap_id: int,
    mods: int,
    mode: int,
    acc: float,
    ngeki: int,
    nkatu: int,
    n300: int,
    n100: int,
    n50: int,
    nmiss: int,
    combo: int,
    score: int,
):
    try:
        beatmap = Beatmap(path=path.join(osu_folder_path, str(beatmap_id) + ".osu"))
        beatmap.convert(get_mode(mode), mods)

        difficulty = Difficulty(mods=mods)
        calculator = Performance(
            mods=mods,
            accuracy=acc,
            n_geki=ngeki,
            n_katu=nkatu,
            n300=n300,
            n100=n100,
            n50=n50,
            misses=nmiss,
            combo=combo,
            lazer=False,
            legacy_total_score=score,
        )
        performance_attr = calculator.calculate(beatmap)
        difficulty_attr = difficulty.calculate(beatmap)

        performance_vn = {}
        if mods & Mods.RELAX:
            mods &= ~Mods.RELAX
            calculator.set_mods(mods)
            performance_vn = calculator.calculate(beatmap)

        return (
            json_dump(difficulty_attr),
            json_dump(performance_attr),
            performance_attr.pp,
            json_dump(difficulty.strains(beatmap)),
            json_dump(performance_vn),
        )
    except:
        return None, None, 0.0, None, None
