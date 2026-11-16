"""Собирает data/complexes.csv и data/complexes.xlsx из scripts/rows.py."""
import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from rows import DATE, METHOD, ROWS, Y

ROOT = Path(__file__).resolve().parent.parent
HEADER = ["город", "название ЖК", "застройщик", "район", "класс", "цена от, руб. за м2",
          "срок сдачи", "ссылка на источник (цена)", "ссылка на карточку ЖК (срок, класс)",
          "дата проверки", "примечание"]


def records():
    for city, name, dev, district, cls, price, srok, path, note in ROWS:
        yield [city, name, dev, district, cls, price, srok, Y + path + "planirovki/", Y + path,
               DATE, f"{note}. Метод: {METHOD}"]


def main():
    recs = list(records())
    assert len(recs) == 15
    with open(ROOT / "data/complexes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(recs)

    wb = Workbook()
    ws = wb.active
    ws.title = "ЖК"
    ws.append(HEADER)
    for r in recs:
        ws.append(r)
    for c in ws[1]:
        c.font = Font(bold=True)
    for row in ws.iter_rows(min_row=2):
        row[5].number_format = "# ##0"
        for idx in (7, 8):
            row[idx].hyperlink = row[idx].value
            row[idx].font = Font(color="0563C1", underline="single")
    widths = [16, 24, 20, 34, 10, 16, 24, 50, 50, 13, 60]
    for i, wdt in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = wdt
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    wb.save(ROOT / "data/complexes.xlsx")
    print("ok:", len(recs), "строк")


if __name__ == "__main__":
    main()
