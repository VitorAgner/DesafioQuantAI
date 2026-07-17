"""Decomposição BULL×BEAR fecha com o retorno total (tolerância 1e-8 em log)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backtest import run_backtest
from src.metrics import regime_decomposition, risk_exposure
from src.regime import regime_series

CFG = {
    "regime": {"sma_window": 50, "hysteresis_band": 0.0},
    "momentum": {"lookback_months": 3, "skip_months": 1, "top_n": 2},
    "backtest": {"rebalance": "M", "cost_per_trade": 0.0, "initial_capital": 1.0},
}


def _data(n=500):
    rng = np.random.default_rng(11)
    idx = pd.bdate_range("2020-01-01", periods=n)
    assets = pd.DataFrame(
        100 * np.exp(np.cumsum(rng.normal(0.0005, 0.012, (n, 4)), axis=0)),
        index=idx, columns=["A", "B", "C", "D"],
    )
    # IBOV oscilante para gerar os dois regimes
    ibov = pd.Series(100 + 10 * np.sin(np.arange(n) / 40) + np.arange(n) * 0.01, index=idx)
    cdi = pd.Series(0.0004, index=idx)
    return assets, ibov, cdi


def test_decomposition_closes_in_log():
    assets, ibov, cdi = _data()
    res = run_backtest(assets, ibov, cdi, CFG, use_regime=True)
    d = regime_decomposition(res.daily_returns, res.weights_daily)
    assert abs(np.log(d["factor_bull"]) + np.log(d["factor_bear"])
               - np.log(d["factor_total"])) < 1e-8


def test_exposure_in_unit_interval_and_coherent():
    assets, ibov, cdi = _data()
    res = run_backtest(assets, ibov, cdi, CFG, use_regime=True)
    exp = risk_exposure(res.weights_daily)
    assert 0.0 <= exp <= 1.0
    # coerência com a timeline: houve meses BULL e BEAR no log
    regimes = set(res.decisions["regime"])
    if regimes == {"BULL", "BEAR"}:
        assert 0.0 < exp < 1.0
