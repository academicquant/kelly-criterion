import math
import random
import unittest

from kelly import growth_rate, kelly_continuous, kelly_fraction, kelly_multi, simulate


class KellyTests(unittest.TestCase):
    def test_even_money(self):
        # 60% to win an even-money bet: stake 2p - 1 = 20%.
        self.assertAlmostEqual(kelly_fraction(0.6, 1.0), 0.2)

    def test_no_edge_no_bet(self):
        self.assertEqual(kelly_fraction(0.5, 1.0), 0.0)
        self.assertEqual(kelly_fraction(0.3, 2.0), 0.0)

    def test_odds(self):
        # 40% at 2 to 1: f = 0.4 - 0.6 / 2 = 0.1.
        self.assertAlmostEqual(kelly_fraction(0.4, 2.0), 0.1)

    def test_growth_value(self):
        self.assertAlmostEqual(growth_rate(0.2, 0.6, 1.0), 0.6 * math.log(1.2) + 0.4 * math.log(0.8))
        self.assertAlmostEqual(growth_rate(0.2, 0.6, 1.0), 0.0201355, places=6)

    def test_kelly_maximises_growth(self):
        for p, b in [(0.6, 1.0), (0.55, 1.5), (0.3, 4.0)]:
            f = kelly_fraction(p, b)
            grid = max((growth_rate(k / 10000, p, b), k / 10000) for k in range(0, 9999))
            self.assertAlmostEqual(grid[1], f, places=3)

    def test_double_kelly_grows_about_nothing(self):
        # For a small edge the growth curve is close to a parabola, so staking twice Kelly earns about zero.
        p, b = 0.51, 1.0
        f = kelly_fraction(p, b)
        self.assertLess(abs(growth_rate(2 * f, p, b)), 0.02 * growth_rate(f, p, b))

    def test_half_kelly_keeps_three_quarters(self):
        p, b = 0.51, 1.0
        f = kelly_fraction(p, b)
        ratio = growth_rate(f / 2, p, b) / growth_rate(f, p, b)
        self.assertAlmostEqual(ratio, 0.75, places=2)

    def test_multi_matches_binary(self):
        for p, b in [(0.6, 1.0), (0.4, 2.0), (0.55, 1.5)]:
            self.assertAlmostEqual(kelly_multi([(p, b), (1 - p, -1.0)]), kelly_fraction(p, b), places=9)

    def test_multi_three_outcomes(self):
        # Win 2 with 30%, break even with 30%, lose the stake with 40%. The slope is
        # 0.6 / (1 + 2f) - 0.4 / (1 - f), which is zero at f = 0.2 / 1.4 = 1/7.
        self.assertAlmostEqual(kelly_multi([(0.3, 2.0), (0.3, 0.0), (0.4, -1.0)]), 1 / 7, places=9)

    def test_multi_no_edge(self):
        self.assertEqual(kelly_multi([(0.5, 1.0), (0.5, -1.0)]), 0.0)

    def test_continuous(self):
        # 8% drift, 3% cash, 20% volatility: 0.05 / 0.04 = 1.25, so 125% of wealth, borrowing the rest.
        self.assertAlmostEqual(kelly_continuous(0.08, 0.03, 0.2), 1.25)

    def test_simulation_agrees_with_growth(self):
        rng = random.Random(1)
        p, b, n = 0.6, 1.0, 20000
        f = kelly_fraction(p, b)
        logs = [math.log(simulate(f, p, b, n, rng)) / n for _ in range(20)]
        mean = sum(logs) / len(logs)
        # Per-bet log returns have sd about 0.2, so the mean over 400,000 bets has sd about 0.0003.
        self.assertAlmostEqual(mean, growth_rate(f, p, b), delta=0.0015)


if __name__ == "__main__":
    unittest.main()
