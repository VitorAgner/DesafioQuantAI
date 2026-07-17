"""Camada 1 — filtro de regime Bull/Bear sobre o IBOV.

Regra base: BULL se fechamento > SMA(window). Variante de robustez: banda de
histerese ±band em torno da SMA (só troca de estado ao cruzar a banda oposta).
Só usa dados até a própria data (rolling => sem look-ahead).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def regime_series(ibov: pd.Series, window: int = 200, band: float = 0.0) -> pd.Series:
    """Série diária booleana: True = BULL. NaN até haver `window` observações."""
    sma = ibov.rolling(window).mean()
    if band <= 0:
        return (ibov > sma).astype("boolean").mask(sma.isna())

    upper, lower = sma * (1 + band), sma * (1 - band)
    state = pd.Series(np.nan, index=ibov.index, dtype="float64")
    cur = np.nan
    for i, (px, up, lo) in enumerate(zip(ibov.values, upper.values, lower.values)):
        if np.isnan(up):
            continue
        if np.isnan(cur):
            cur = 1.0 if px > up else 0.0
        elif cur == 0.0 and px > up:
            cur = 1.0
        elif cur == 1.0 and px < lo:
            cur = 0.0
        state.iloc[i] = cur
    return state.astype("boolean") == 1.0
