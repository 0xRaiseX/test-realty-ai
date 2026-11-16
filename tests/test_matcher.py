import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matcher  # noqa: E402
from matcher import Complex, cheapest, load, main, normalize_city, pick  # noqa: E402


def cx(name, city="Сочи", price=300_000):
    return Complex(city, name, "Застройщик", "Район", "бизнес", price, "2027", "https://example.org")


class PickTest(unittest.TestCase):
    def setUp(self):
        self.data = [
            cx("A", price=300_000),  # 60 м2 -> 18 млн
            cx("B", price=400_000),  # 24 млн
            cx("C", price=450_000),  # 27 млн
            cx("D", price=500_000),  # 30 млн
            cx("E", price=600_000),  # 36 млн - дороже бюджета
            cx("M", city="Москва", price=100_000),
        ]

    def test_cost_is_price_times_area(self):
        res = pick(self.data, "Сочи", 30_000_000, 60)
        self.assertEqual(res[0].cost, 500_000 * 60)

    def test_filters_by_city_and_budget(self):
        names = [m.complex.name for m in pick(self.data, "Сочи", 30_000_000, 60, top=10)]
        self.assertNotIn("E", names)  # дороже бюджета
        self.assertNotIn("M", names)  # другой город

    def test_top3_closest_to_budget(self):
        names = [m.complex.name for m in pick(self.data, "Сочи", 30_000_000, 60)]
        self.assertEqual(names, ["D", "C", "B"])

    def test_budget_boundary_inclusive(self):
        names = [m.complex.name for m in pick(self.data, "Сочи", 18_000_000, 60)]
        self.assertEqual(names, ["A"])

    def test_nothing_fits(self):
        self.assertEqual(pick(self.data, "Сочи", 1_000_000, 60), [])
        self.assertEqual(cheapest(self.data, "Сочи", 60).complex.name, "A")

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            pick(self.data, "Сочи", 0, 60)
        with self.assertRaises(ValueError):
            pick(self.data, "Сочи", 10_000_000, -5)


class CityTest(unittest.TestCase):
    known = {"Сочи", "Москва", "Санкт-Петербург"}

    def test_aliases_and_case(self):
        self.assertEqual(normalize_city("сочи", self.known), "Сочи")
        self.assertEqual(normalize_city("СПб", self.known), "Санкт-Петербург")
        self.assertEqual(normalize_city("санкт петербург", self.known), "Санкт-Петербург")
        self.assertIsNone(normalize_city("Казань", self.known))


class RealDataTest(unittest.TestCase):
    """Проверки на настоящей таблице из Части 1."""

    def test_table_has_15_rows_5_per_city(self):
        data = load()
        self.assertEqual(len(data), 15)
        for city in ("Сочи", "Москва", "Санкт-Петербург"):
            self.assertEqual(sum(c.city == city for c in data), 5)
        self.assertTrue(all(c.url.startswith("https://") for c in data))
        self.assertTrue(all(c.cls in ("бизнес", "премиум") for c in data))

    def test_cli_example(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--city", "Сочи", "--budget", "30000000", "--area", "60"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("1. ", text)
        self.assertIn("3. ", text)

    def test_cli_unknown_city(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--city", "Казань", "--budget", "30000000", "--area", "60"])
        self.assertEqual(code, 2)
        self.assertIn("нет в таблице", out.getvalue())

    def test_cli_nothing_fits_gives_hint(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--city", "Москва", "--budget", "5000000", "--area", "60"])
        self.assertEqual(code, 1)
        self.assertIn("Самый доступный вариант", out.getvalue())


if __name__ == "__main__":
    unittest.main()
