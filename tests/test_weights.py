"""Pesos somam 1; BEAR aloca 100% em CDI; top-N equal-weight."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backtest import run_backtest
from src.momentum import top_n_weights


CFG = {
    "regime": {"sma_window": 50, "hysteresis_band": 0.0},
    "momentum": {"lookback_months": 3, "skip_months": 1, "top_n": 2},
    "backtest": {"rebalance": "M", "cost_per_trade": 0.0, "initial_capital": 1.0},
}


def _data(trend=0.001, n=400):
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2021-01-01", periods=n)
    assets = pd.DataFrame(
        100 * np.exp(np.cumsum(rng.normal(trend, 0.01, (n, 4)), axis=0)),
        index=idx, columns=["A", "B", "C", "D"],
    )
    ibov = pd.Series(100 * np.exp(np.cumsum(np.full(n, trend))), index=idx)
    cdi = pd.Series(0.0004, index=idx)
    return assets, ibov, cdi


def test_top_n_weights_sum_to_one():
    w = top_n_weights(pd.Series({"A": 0.3, "B": 0.1, "C": 0.5, "D": np.nan}), n=2)
    assert abs(w.sum() - 1.0) < 1e-12
    assert w["C"] == w["A"] == 0.5 and w["B"] == 0.0 and w["D"] == 0.0


def test_bear_goes_full_cdi():
    assets, ibov, cdi = _data(trend=-0.002)  # queda constante → sempre BEAR
    res = run_backtest(assets, ibov, cdi, CFG, use_regime=True)
    assert (res.decisions["regime"] == "BEAR").all()
    assert (res.decisions["assets"] == "CDI").all()
    # carteira rende exatamente CDI
    pd.testing.assert_series_equal(res.daily_returns, cdi, check_names=False)


def test_bull_weights_sum_to_one():
    assets, ibov, cdi = _data(trend=0.002)  # alta constante → BULL após warmup
    res = run_backtest(assets, ibov, cdi, CFG, use_regime=True)
    bull_rows = res.decisions[res.decisions["regime"] == "BULL"]
    assert len(bull_rows) > 0
    for w in bull_rows["weights"]:
        assert abs(sum(map(float, w.split(";"))) - 1.0) < 1e-9
