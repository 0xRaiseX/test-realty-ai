"""Генерирует web/data.js из data/complexes.csv, чтобы страница работала и без сервера (file://)."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
with open(ROOT / "data/complexes.csv", encoding="utf-8") as f:
    rows = [
        {"city": r["город"], "name": r["название ЖК"], "developer": r["застройщик"],
         "district": r["район"], "cls": r["класс"], "price_m2": int(r["цена от, руб. за м2"]),
         "deadline": r["срок сдачи"], "url": r["ссылка на источник (цена)"]}
        for r in csv.DictReader(f)
    ]
(ROOT / "web/data.js").write_text(
    "// Сгенерировано scripts/build_web_data.py из data/complexes.csv. Не править руками.\n"
    "window.COMPLEXES = " + json.dumps(rows, ensure_ascii=False, indent=1) + ";\n",
    encoding="utf-8",
)
print(len(rows), "ЖК -> web/data.js")
