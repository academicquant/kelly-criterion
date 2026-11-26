"""Kelly criterion: the stake that maximises long-run growth of a bankroll.

kelly_fraction(p, b)          binary bet, win b per unit staked with probability p
growth_rate(f, p, b)          expected log growth per bet when staking a fraction f
kelly_multi(outcomes)         best fraction for a bet with several payoffs, by bisection
kelly_continuous(mu, r, sig)  fraction of wealth in a lognormal asset, (mu - r) / sig^2
simulate(f, p, b, n, rng)     final wealth after n bets, for checking the above by hand
"""
import math
import random


def kelly_fraction(p, b):
    """Fraction of the bankroll to stake on a bet paying b to 1 that wins with probability p.

    Returns 0 when the bet has no edge (p * b - (1 - p) <= 0): Kelly never bets against you.
    """
    if not 0 <= p <= 1:
        raise ValueError("p must be a probability")
    if b <= 0:
        raise ValueError("b must be positive")
    f = p - (1 - p) / b
    return max(f, 0.0)


def growth_rate(f, p, b):
    """Expected log growth per bet: p log(1 + f b) + (1 - p) log(1 - f)."""
    if not 0 <= f < 1:
        raise ValueError("f must be in [0, 1)")
    return p * math.log1p(f * b) + (1 - p) * math.log1p(-f)


def kelly_multi(outcomes, tol=1e-12):
    """Kelly fraction for one bet with several outcomes.

    outcomes is a list of (probability, return per unit staked), e.g. (0.5, 1.0) for doubling the stake's
    profit and (0.5, -1.0) for losing it. The derivative of the log growth, sum p r / (1 + f r), falls as f
    rises, so the root is found by bisection between 0 and the largest stake that can't wipe you out.
    """
    if abs(sum(p for p, _ in outcomes) - 1) > 1e-9:
        raise ValueError("probabilities must sum to 1")
    slope = lambda f: sum(p * r / (1 + f * r) for p, r in outcomes)
    if slope(0.0) <= 0:
        return 0.0
    worst = min(r for _, r in outcomes)
    hi = 1.0 if worst >= 0 else -1.0 / worst
    hi -= 1e-12
    if slope(hi) > 0:
        return hi
    lo = 0.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if slope(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def kelly_continuous(mu, r, sigma):
    """Fraction of wealth to hold in an asset with drift mu and volatility sigma when cash earns r."""
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return (mu - r) / sigma ** 2


def simulate(f, p, b, n, rng=None):
    """Wealth after n independent bets starting from 1, staking the fraction f each time."""
    rng = rng or random.Random()
    w = 1.0
    for _ in range(n):
        w *= 1 + f * b if rng.random() < p else 1 - f
    return w
