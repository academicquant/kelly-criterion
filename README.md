# Kelly criterion in Python: bet sizing for binary, multi-outcome and continuous bets

If you're interviewing for a quant trading role you'll almost certainly be asked how much of your bankroll to put on a bet with an edge, and the answer they're after is the Kelly criterion. It's the stake that maximises the expected log of your wealth, which over many bets means the fastest long-run growth. I wrote this small module so the formulas sit next to tests you can run, because the follow-up questions (what about half Kelly, what if there are three outcomes, what does it say about a stock) are where most people get stuck.

`kelly_fraction(p, b)` is the textbook case. You win b for every unit staked with probability p and lose the stake otherwise, and the fraction to bet is p − (1 − p)/b. At 60% on an even-money bet that's 20% of the bankroll. If the edge is zero or negative it returns 0, since Kelly never tells you to take a bet that's against you.

`growth_rate(f, p, b)` gives the expected log growth per bet for any fraction f, so you can see the shape of the curve for yourself. With a small edge it's close to a parabola, which is why half Kelly keeps about three quarters of the growth for a lot less risk, and why staking twice Kelly earns you roughly nothing.

`kelly_multi(outcomes)` handles a bet with several payoffs. The slope of the log growth only ever falls as the stake rises, so it finds the root by bisection and never stakes so much that the worst outcome could wipe you out. `kelly_continuous(mu, r, sigma)` is the version for an asset whose price follows geometric Brownian motion: hold (μ − r)/σ² of your wealth in it. With 8% drift, 3% cash and 20% volatility that comes to 125%, so you'd be borrowing.

```python
from kelly import kelly_fraction, growth_rate, kelly_multi, kelly_continuous

kelly_fraction(0.6, 1.0)                              # 0.2
growth_rate(0.2, 0.6, 1.0)                            # 0.0201 per bet
kelly_multi([(0.3, 2.0), (0.3, 0.0), (0.4, -1.0)])    # 1/7
kelly_continuous(0.08, 0.03, 0.20)                    # 1.25
```

## Tests

`python3 -m unittest test_kelly` runs 12 checks in well under a second. They compare the formula with a brute-force search over 10,000 stakes, check the three-outcome answer of 1/7 that you can get by hand, confirm that half Kelly keeps 75% of the growth when the edge is small, and simulate 400,000 bets on a fixed seed to make sure the average log growth lands where the formula says it should (0.0200 against 0.0201). You only need the Python standard library.

## More practice

Betting, Kelly and market-making interview questions with worked answers: https://academicquant.co.uk/quant-questions-market-making?utm_source=github&utm_medium=post&utm_campaign=github-kelly-criterion

MIT licence.
