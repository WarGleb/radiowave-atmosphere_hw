"""Заготовка решения домашнего задания.

Что нужно сделать:
1. В SOLVERS заполните функцию для вашего задания (dz1 ... dz11). Она принимает
   словарь исходных данных варианта и возвращает словарь результатов.
   Имена ключей должны совпадать с tests/control_answers.json (поле "key").
2. В get_variant допишите формулы вариантов из текста задания, чтобы считать свой номер n.
   Вариант 0 (контрольный) уже подставлен из tests/control_answers.json.
3. Запускайте:  python src/solution.py --dz dz1 --variant 0
4. Для сдачи:  python src/solution.py --dz dz11 --variant <n> --json results/result_dz11.json
   Файл читает проверка преподавателя; в нём ключи результатов и номер варианта.
"""
import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTROL = json.loads((ROOT / "tests" / "control_answers.json").read_text(encoding="utf-8"))


def get_variant(dz, n):
    """Исходные данные варианта n задания dz (словарь)."""
    if n == 0:
        return dict(CONTROL[dz]["variant"])
    # TODO: впишите формулы вариантов из таблицы «Исходные данные» вашего задания
    raise NotImplementedError("Формулы вариантов ещё не добавлены")


def solve_dz1(v):
    # TODO: модели Дебая, Лоренца, Друде
    raise NotImplementedError


def solve_dz2(v):
    # TODO: проницаемость воды, спектр капель, удельное затухание
    raise NotImplementedError


def solve_dz3(v):
    # TODO: лёд, снег, град
    raise NotImplementedError


def solve_dz4(v):
    # TODO: геометрия трассы и рефракция
    raise NotImplementedError


def solve_dz5(v):
    # TODO: профили атмосферы и бюджет потерь
    raise NotImplementedError


def solve_dz6(v, ref_inputs=None):
    """v: city, f, el, tau, hs. ref_inputs: эталонные данные карт (R001, P0, R01, R1, hR, lat, lon).

    Если ref_inputs не None, используйте их вместо собственных найденных значений:
    так проверяется сам расчёт, а не выбор источников.
    """
    # TODO: метод P.618, подгонка, разнесённый приём
    raise NotImplementedError


def solve_dz7(v):
    # TODO: газовые линии O2 и H2O, форма линии, дисперсия
    raise NotImplementedError


def solve_dz8(v):
    # TODO: ионосфера, TEC, задержка, Фарадей, сцинтилляция, IWV
    raise NotImplementedError


def solve_dz9(v):
    # TODO: энергетический бюджет, шумы, запас на замирания, обнаружение, XPD
    raise NotImplementedError


def solve_dz10(v):
    # TODO: статистика замираний, спектр, оценка фазы
    raise NotImplementedError


def solve_dz11(v):
    # TODO: оптическая линия
    raise NotImplementedError


SOLVERS = {"dz1": solve_dz1, "dz2": solve_dz2, "dz3": solve_dz3,
           "dz4": solve_dz4, "dz5": solve_dz5, "dz6": solve_dz6,
           "dz7": solve_dz7, "dz8": solve_dz8, "dz9": solve_dz9, "dz10": solve_dz10, "dz11": solve_dz11}


def solve(dz, n, ref_inputs=None):
    v = get_variant(dz, n)
    if dz == "dz6":
        return SOLVERS[dz](v, ref_inputs)
    return SOLVERS[dz](v)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dz", default="dz1")
    ap.add_argument("--variant", type=int, default=0)
    ap.add_argument("--json", default=None, help="записать результаты в JSON-файл (для сдачи)")
    a = ap.parse_args()
    ref = CONTROL.get(a.dz, {}).get("inputs") if a.variant == 0 else None
    res = solve(a.dz, a.variant, ref)
    for key, value in res.items():
        print(f"{key}: {value}")
    if a.json:
        out = pathlib.Path(a.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {"dz": a.dz, "variant": a.variant,
                   "values": {k: (float(v) if not isinstance(v, str) else v) for k, v in res.items()}}
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
