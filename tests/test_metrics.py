"""Métricas contra casos sintéticos de resultado conhecido."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import metrics


def test_cagr_exact():
    idx = pd.date_range("2020-01-01", "2022-01-01", freq="D")  # 2 anos
    eq = pd.Series(np.linspace(1, 1, len(idx)), index=idx)
    eq.iloc[-1] = 1.21  # 10% a.a. por 2 anos
    assert abs(metrics.cagr(eq) - 0.10) < 5e-3


def test_max_drawdown():
    idx = pd.date_range("2020-01-01", periods=4, freq="D")
    eq = pd.Series([1.0, 2.0, 1.0, 1.5], index=idx)
    assert metrics.max_drawdown(eq) == -0.5


def test_sharpe_zero_for_cdi_itself():
    idx = pd.bdate_range("2020-01-01", periods=252)
    cdi = pd.Series(0.0004, index=idx)
    assert abs(metrics.sharpe(cdi, cdi)) < 1e-12 or np.isnan(metrics.sharpe(cdi, cdi))


def test_pct_positive_months():
    idx = pd.bdate_range("2020-01-01", "2020-04-30")
    r = pd.Series(0.001, index=idx)
    r[idx.month == 2] = -0.001  # fevereiro negativo
    assert abs(metrics.pct_positive_months(r) - 3 / 4) < 1e-12
