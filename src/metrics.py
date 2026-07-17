"""Métricas de performance (base diária, 252 pregões/ano)."""
from __future__ import annotations

import numpy as np
import pandas as pd

ANN = 252


def cagr(equity: pd.Series) -> float:
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1


def ann_vol(returns: pd.Series) -> float:
    return returns.std() * np.sqrt(ANN)


def sharpe(returns: pd.Series, cdi: pd.Series) -> float:
    excess = returns - cdi.reindex(returns.index).fillna(0)
    vol = excess.std()
    return float("nan") if vol == 0 else excess.mean() / vol * np.sqrt(ANN)


def max_drawdown(equity: pd.Series) -> float:
    return (equity / equity.cummax() - 1).min()


def calmar(equity: pd.Series) -> float:
    dd = abs(max_drawdown(equity))
    return float("nan") if dd == 0 else cagr(equity) / dd


def pct_positive_months(returns: pd.Series) -> float:
    monthly = (1 + returns).groupby([returns.index.year, returns.index.month]).prod() - 1
    return (monthly > 0).mean()


def summary(name: str, equity: pd.Series, returns: pd.Series, cdi: pd.Series,
            decisions: pd.DataFrame | None = None) -> dict:
    out = {
        "Estratégia": name,
        "CAGR": cagr(equity),
        "Vol anual": ann_vol(returns),
        "Sharpe": sharpe(returns, cdi),
        "Max DD": max_drawdown(equity),
        "Calmar": calmar(equity),
        "% meses positivos": pct_positive_months(returns),
    }
    if decisions is not None and len(decisions):
        out["% tempo em risco"] = (decisions["assets"] != "CDI").mean()
        out["Turnover médio"] = decisions["turnover"].mean()
    return out
