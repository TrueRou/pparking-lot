from __future__ import annotations

import json
from os import path

from rosu_pp_py import Beatmap, Difficulty, Performance

from mods import Mods
from config import osu_folder_path


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


class SkipNoneEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, dict):
            # 过滤掉值为 None 的字段
            return {k: v for k, v in obj.items() if v is not None}
        return json.JSONEncoder.default(self, obj)


def json_dump(obj):
    return json.dumps(to_dic(obj))


def calculate(beatmap_id: int, mods: int, mode: int, acc: float, ngeki: int, nkatu: int, n300: int, n100: int, n50: int, nmiss: int, combo: int):
    try:
        beatmap = Beatmap(path=path.join(osu_folder_path, str(beatmap_id) + ".osu"))
        difficulty = Difficulty(mods=mods)
        calculator = Performance(mods=mods, accuracy=acc, n_geki=ngeki, n_katu=nkatu, n300=n300, n100=n100, n50=n50, misses=nmiss, combo=combo)
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
