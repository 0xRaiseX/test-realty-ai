"""Подборщик ЖК по городу, бюджету и площади.

Данные: data/complexes.csv (Часть 1). Только стандартная библиотека.

Пример:
    python matcher.py --city Сочи --budget 30000000 --area 60
"""
from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "complexes.csv"
TOP_N = 3

CITY_ALIASES = {
    "спб": "Санкт-Петербург",
    "питер": "Санкт-Петербург",
    "петербург": "Санкт-Петербург",
    "санкт петербург": "Санкт-Петербург",
    "мск": "Москва",
}


@dataclass(frozen=True)
class Complex:
    city: str
    name: str
    developer: str
    district: str
    cls: str
    price_m2: int
    deadline: str
    url: str


@dataclass(frozen=True)
class Match:
    complex: Complex
    cost: int  # примерная стоимость = цена за м2 * площадь


def load(path: Path = DATA) -> list[Complex]:
    with open(path, encoding="utf-8", newline="") as f:
        return [
            Complex(
                city=r["город"],
                name=r["название ЖК"],
                developer=r["застройщик"],
                district=r["район"],
                cls=r["класс"],
                price_m2=int(r["цена от, руб. за м2"]),
                deadline=r["срок сдачи"],
                url=r["ссылка на источник (цена)"],
            )
            for r in csv.DictReader(f)
        ]


def normalize_city(city: str, known: set[str]) -> str | None:
    key = city.strip().lower().replace("-", " ").replace("ё", "е")
    key = " ".join(key.split())
    for name in known:
        if name.lower().replace("-", " ") == key:
            return name
    alias = CITY_ALIASES.get(key)
    return alias if alias in known else None


def pick(complexes: list[Complex], city: str, budget: int, area: float, top: int = TOP_N) -> list[Match]:
    """Город совпадает, стоимость (цена за м2 * площадь) не больше бюджета.
    Сортировка: сначала те, что ближе всего к бюджету снизу (лучшее, что можно себе позволить)."""
    if budget <= 0 or area <= 0:
        raise ValueError("бюджет и площадь должны быть больше нуля")
    fits = [Match(c, round(c.price_m2 * area)) for c in complexes if c.city == city]
    fits = [m for m in fits if m.cost <= budget]
    fits.sort(key=lambda m: (budget - m.cost, m.complex.name))
    return fits[:top]


def cheapest(complexes: list[Complex], city: str, area: float) -> Match | None:
    """Самый дешевый вариант в городе - для подсказки, если в бюджет ничего не попало."""
    in_city = [Match(c, round(c.price_m2 * area)) for c in complexes if c.city == city]
    return min(in_city, key=lambda m: m.cost, default=None)


def num(x: float) -> str:
    return f"{x:,.0f}".replace(",", " ")


def rub(x: float) -> str:
    return num(x) + " руб."


def format_result(city: str, budget: int, area: float, matches: list[Match], fallback: Match | None) -> str:
    lines = [f"Город: {city}, бюджет: {rub(budget)}, площадь: {area:g} м2", ""]
    if not matches:
        lines.append("В этот бюджет ни один ЖК из таблицы не проходит.")
        if fallback:
            c = fallback.complex
            need_area = budget // c.price_m2  # вниз: на округленную вверх площадь бюджета не хватит
            lines.append(
                f"Самый доступный вариант: {c.name} (от {num(c.price_m2)} руб./м2), "
                f"{area:g} м2 там стоит примерно {rub(fallback.cost)}"
            )
            lines.append(f"За ваш бюджет там можно рассчитывать примерно на {need_area:.0f} м2.")
        return "\n".join(lines)
    if len(matches) < TOP_N:
        lines.append(f"Подходит только {len(matches)} из {TOP_N}, показываю что есть.")
        lines.append("")
    for i, m in enumerate(matches, 1):
        c = m.complex
        lines += [
            f"{i}. {c.name} ({c.cls}), застройщик {c.developer}",
            f"   Район: {c.district}. Срок сдачи: {c.deadline}",
            f"   Цена от {num(c.price_m2)} руб./м2 x {area:g} м2 = примерно {rub(m.cost)}",
            f"   Остаток бюджета: {rub(budget - m.cost)}",
            f"   Источник: {c.url}",
        ]
    lines += ["", "Стоимость примерная: минимальная цена за м2 у застройщика, умноженная на площадь."]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Подбор 3 ЖК по городу, бюджету и площади")
    p.add_argument("--city", required=True, help="Сочи, Москва или Санкт-Петербург (можно СПб)")
    p.add_argument("--budget", required=True, type=float, help="бюджет на квартиру, руб.")
    p.add_argument("--area", required=True, type=float, help="желаемая площадь, м2")
    p.add_argument("--data", default=str(DATA), help="путь к CSV (по умолчанию data/complexes.csv)")
    a = p.parse_args(argv)

    complexes = load(Path(a.data))
    known = {c.city for c in complexes}
    city = normalize_city(a.city, known)
    if city is None:
        print(f"Города '{a.city}' нет в таблице. Доступны: {', '.join(sorted(known))}.")
        return 2
    if a.budget <= 0 or a.area <= 0:
        print("Бюджет и площадь должны быть больше нуля.")
        return 2
    budget = int(a.budget)
    matches = pick(complexes, city, budget, a.area)
    fallback = None if matches else cheapest(complexes, city, a.area)
    print(format_result(city, budget, a.area, matches, fallback))
    return 0 if matches else 1


if __name__ == "__main__":
    sys.exit(main())
