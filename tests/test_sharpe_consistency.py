"""Valida o Sharpe contra valor analítico em série sintética conhecida."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics import sharpe


def test_sharpe_analytical():
    """Excesso alternando +0.002/0.000: mean=0.001, std conhecido → valor exato."""
    idx = pd.bdate_range("2020-01-01", periods=504)
    cdi = pd.Series(0.0003, index=idx)
    excess = np.tile([0.002, 0.0], 252)
    returns = cdi + excess
    expected = excess.mean() / excess.std(ddof=1) * np.sqrt(252)
    assert abs(sharpe(returns, cdi) - expected) < 1e-12


def test_sharpe_is_not_cagr_based():
    """Sharpe usa média aritmética diária: série de retorno constante c tem
    excesso constante → std 0 → NaN (e não (CAGR−CDI)/vol)."""
    idx = pd.bdate_range("2020-01-01", periods=252)
    r = pd.Series(0.001, index=idx)
    cdi = pd.Series(0.0004, index=idx)
    assert np.isnan(sharpe(r, cdi))


def test_sharpe_same_function_all_curves():
    """A mesma função aplicada a duas curvas dá razão coerente com os excessos."""
    rng = np.random.default_rng(1)
    idx = pd.bdate_range("2018-01-01", periods=1000)
    cdi = pd.Series(0.0004, index=idx)
    noise = pd.Series(rng.normal(0.0, 0.01, 1000), index=idx)
    a = cdi + 0.001 + noise  # mesmo ruído, excesso médio maior
    b = cdi + 0.0005 + noise
    assert sharpe(a, cdi) > sharpe(b, cdi)
