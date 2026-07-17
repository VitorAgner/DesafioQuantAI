"""Camada 2 — sinal de momentum 12-1 e seleção top-N equal-weight.

Sinal em t usa apenas preços <= t (retorno de t-lookback até t-skip).
"""
from __future__ import annotations

import pandas as pd


def momentum_signal(
    prices: pd.DataFrame,
    date: pd.Timestamp,
    lookback_months: int = 12,
    skip_months: int = 1,
) -> pd.Series:
    """Retorno acumulado de (date - lookback) até (date - skip), por ativo.

    Usa o último preço disponível <= cada data-alvo (asof). Ativos sem
    histórico suficiente ficam NaN e são excluídos do ranking.
    """
    hist = prices.loc[:date]
    end_target = date - pd.DateOffset(months=skip_months)
    start_target = date - pd.DateOffset(months=lookback_months)
    if hist.index[0] > start_target:
        return pd.Series(float("nan"), index=prices.columns)

    p_end = hist.loc[:end_target].iloc[-1]
    p_start = hist.loc[:start_target].iloc[-1]
    return p_end / p_start - 1.0


def top_n_weights(signal: pd.Series, n: int = 3) -> pd.Series:
    """Pesos iguais (1/n) nos n ativos de maior sinal; 0 nos demais."""
    valid = signal.dropna()
    weights = pd.Series(0.0, index=signal.index)
    if len(valid) < n:
        return weights
    top = valid.nlargest(n).index
    weights[top] = 1.0 / n
    return weights
