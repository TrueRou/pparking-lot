from __future__ import annotations

import json
from os import path
from typing import Any

from akatsuki_pp_py import Calculator, Beatmap

from gamemode import GameMode
from mods import Mods

osu_folder_path = "C:\\Users\\chenb\\Downloads\\2022_12_01_osu_files"


def to_dic(obj):
    dic = {}
    for field_key in dir(obj):
        field_value = getattr(obj, field_key)
        if not field_key.startswith("__") and not callable(field_value) \
                and not field_key.startswith("_") and field_key != "difficulty":
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


def calculate(beatmap_id: int, mods: int, mode: int, acc: float, ngeki: int, nkatu: int, n300: int,
              n100: int, n50: int, nmiss: int, combo: int):
    try:
        mode_vn = GameMode(mode).as_vanilla
        if mods & Mods.SCOREV2:
            mods &= ~Mods.SCOREV2
        if mods & Mods.NOFAIL:
            mods &= ~Mods.NOFAIL
        beatmap = Beatmap(path=path.join(osu_folder_path, str(beatmap_id) + ".osu"))
        calculator = Calculator(mode=mode_vn, mods=mods, acc=acc, n_geki=ngeki, n_katu=nkatu,
                                n300=n300, n100=n100,
                                n50=n50,
                                n_misses=nmiss)
        calculator.set_combo(combo)
        return do_calculate(calculator, beatmap, mode_vn)
    except:
        return None, None, 0.0


def calculate_prepend(beatmap_id: int, mods: int, acc: float, mode_vn=0):
    beatmap = Beatmap(path=path.join(osu_folder_path, str(beatmap_id) + ".osu"))
    calculator = Calculator(mode=mode_vn, mods=mods, acc=acc)
    return do_calculate(calculator, beatmap, mode_vn)


def do_calculate(calculator: Calculator, beatmap: Beatmap, mode_vn: int):
    beatmap_attr: Any = calculator.map_attributes(beatmap)
    difficulty_attr: Any = calculator.difficulty(beatmap)
    performance_attr: Any = calculator.performance(beatmap)
    performance_point = performance_attr.pp if beatmap_attr.mode == mode_vn else 0.0
    performance_point = performance_point if performance_point <= 8192 else 8192.0
    return json_dump(difficulty_attr), json_dump(performance_attr), performance_point
