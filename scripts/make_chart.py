"""График: цена 'от' за м2 по городам. Точки - отдельные ЖК (цвет = класс),
горизонтальная черта - медиана по городу. Результат: charts/price_by_city.png"""
import csv
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CITIES = ["Сочи", "Санкт-Петербург", "Москва"]
COLORS = {"бизнес": "#2a78d6", "премиум": "#eb6834"}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"

rows = list(csv.DictReader(open(ROOT / "data/complexes.csv", encoding="utf-8")))
for r in rows:
    r["p"] = int(r["цена от, руб. за м2"]) / 1000

fig, ax = plt.subplots(figsize=(10, 6.2), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

for i, city in enumerate(CITIES):
    cr = sorted([r for r in rows if r["город"] == city], key=lambda r: r["p"])
    med = st.median(r["p"] for r in cr)
    ax.hlines(med, i + 0.24, i + 0.36, color=INK, linewidth=2.5, zorder=2)
    ax.text(i + 0.38, med, f"медиана {med:.0f}", va="center", fontsize=8.5, color=INK)
    # подписи раздвигаем по вертикали, чтобы не наезжали (мин. зазор 16 тыс.)
    ys = []
    for r in cr:
        y = r["p"]
        if ys and y - ys[-1] < 16:
            y = ys[-1] + 16
        ys.append(y)
    for j, (r, ly) in enumerate(zip(cr, ys)):
        x = i - 0.1 + 0.07 * j
        ax.scatter(x, r["p"], s=70, color=COLORS[r["класс"]], edgecolor=SURFACE, linewidth=2, zorder=3)
        ax.annotate(f"{r['название ЖК']}  {r['p']:.0f}", (x, r["p"]), xytext=(i - 0.16, ly),
                    fontsize=7.5, color=INK2, ha="right", va="center",
                    arrowprops=dict(arrowstyle="-", color=GRID, lw=0.8) if abs(ly - r["p"]) > 1 else None)

ax.set_xticks(range(len(CITIES)), CITIES, fontsize=11, color=INK)
ax.set_xlim(-0.75, 2.75)
ax.set_ylim(200, 880)
ax.set_ylabel("цена от, тыс. руб. за м2", color=INK2)
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="y", colors=INK2, length=0)
ax.tick_params(axis="x", length=0)
handles = [plt.Line2D([], [], marker="o", ls="", color=c, markersize=8, label=k) for k, c in COLORS.items()]
handles.append(plt.Line2D([], [], color=INK, lw=2, label="медиана по городу"))
ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=9)
ax.set_title("Цена 'от' за м2 в 15 ЖК бизнес- и премиум-класса", loc="left", fontsize=13, color=INK, pad=14)
fig.text(0.01, 0.01, "Источник: Яндекс Недвижимость, страницы 'Планировки' ЖК, минимальная цена за м2 у застройщика, 16.11.2026",
         fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1))
out = ROOT / "charts/price_by_city.png"
fig.savefig(out, facecolor=SURFACE)
print(out)
