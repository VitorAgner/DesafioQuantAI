"""Sinais em t não podem mudar quando dados futuros a t são alterados."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.momentum import momentum_signal
from src.regime import regime_series


def _prices(n=600, cols=("A", "B", "C")):
    rng = np.random.default_rng(42)
    idx = pd.bdate_range("2020-01-01", periods=n)
    return pd.DataFrame(
        100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, (n, len(cols))), axis=0)),
        index=idx, columns=list(cols),
    )


def test_momentum_ignores_future():
    prices = _prices()
    t = prices.index[400]
    base = momentum_signal(prices, t)
    mutated = prices.copy()
    mutated.iloc[401:] *= 5.0  # explode o futuro
    assert momentum_signal(mutated, t).equals(base)


def test_regime_ignores_future():
    prices = _prices()["A"]
    t = prices.index[400]
    base = regime_series(prices, window=200).loc[t]
    mutated = prices.copy()
    mutated.iloc[401:] *= 5.0
    assert regime_series(mutated, window=200).loc[t] == base


def test_momentum_skip_excludes_last_month():
    prices = _prices()
    t = prices.index[-1]
    base = momentum_signal(prices, t, lookback_months=12, skip_months=1)
    mutated = prices.copy()
    last_month = t - pd.DateOffset(days=15)  # dentro do mês skipado
    mutated.loc[mutated.index > last_month] *= 3.0
    assert momentum_signal(mutated, t, 12, 1).equals(base)
