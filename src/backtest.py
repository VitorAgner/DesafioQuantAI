"""Loop do backtest: rebalanceamento mensal com defasagem t+1.

Em cada último pregão do mês t: avalia regime e (se BULL) ranking de momentum
com dados até t. Os pesos valem a partir do 1º pregão do mês seguinte —
o retorno do próprio dia da decisão nunca entra na carteira nova.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .momentum import momentum_signal, top_n_weights
from .regime import regime_series

CASH = "CDI"


@dataclass
class BacktestResult:
    equity: pd.Series                 # curva de patrimônio diária
    daily_returns: pd.Series
    decisions: pd.DataFrame           # log: data, regime, ativos, pesos, turnover
    weights_daily: pd.DataFrame = field(repr=False, default=None)


def rebalance_dates(prices: pd.DataFrame) -> pd.DatetimeIndex:
    """Último pregão de cada mês (exceto o último mês, que não tem mês seguinte)."""
    idx = prices.index
    last = idx.to_series().groupby([idx.year, idx.month]).max()
    return pd.DatetimeIndex(last.values)[:-1]


def run_backtest(
    assets: pd.DataFrame,
    ibov: pd.Series,
    cdi: pd.Series,
    cfg: dict,
    use_regime: bool = True,
) -> BacktestResult:
    """Sentinel (use_regime=True) ou momentum puro (use_regime=False)."""
    sma_w = cfg["regime"]["sma_window"]
    band = cfg["regime"]["hysteresis_band"]
    lb = cfg["momentum"]["lookback_months"]
    skip = cfg["momentum"]["skip_months"]
    top_n = cfg["momentum"]["top_n"]
    cost = cfg["backtest"]["cost_per_trade"]

    bull = regime_series(ibov, sma_w, band)
    rets = assets.pct_change()

    cols = list(assets.columns) + [CASH]
    target = pd.DataFrame(0.0, index=assets.index, columns=cols)
    decisions = []
    prev_w = pd.Series(0.0, index=cols)
    prev_w[CASH] = 1.0  # começa em caixa

    warmup = max(sma_w, 1)
    for t in rebalance_dates(assets):
        pos = assets.index.get_loc(t)
        if pos < warmup:
            continue
        sig = momentum_signal(assets, t, lb, skip)
        is_bull = bool(bull.loc[t]) if pd.notna(bull.loc[t]) else False
        w = pd.Series(0.0, index=cols)
        if (is_bull or not use_regime) and sig.notna().sum() >= top_n:
            w[assets.columns] = top_n_weights(sig, top_n)
        if w.sum() == 0:
            w[CASH] = 1.0
        turnover = (w - prev_w).abs().sum() / 2
        picks = [c for c in assets.columns if w[c] > 0]
        decisions.append(
            {"date": t, "regime": "BULL" if is_bull else "BEAR",
             "assets": ",".join(picks) if picks else CASH,
             "weights": ";".join(f"{w[c]:.4f}" for c in picks) or "1.0",
             "turnover": turnover}
        )
        # pesos valem do pregão seguinte à decisão em diante
        target.iloc[pos + 1:] = w.values
        prev_w = w

    # retornos da carteira: pesos do dia (já defasados) * retornos do dia
    port_ret = (target[assets.columns] * rets).sum(axis=1) + target[CASH] * cdi

    # custos: turnover aplicado no 1º dia de vigência dos novos pesos
    if cost > 0 and decisions:
        for d in decisions:
            pos = assets.index.get_loc(d["date"])
            if pos + 1 < len(assets.index):
                port_ret.iloc[pos + 1] -= 2 * d["turnover"] * cost  # 2 pernas

    # antes do primeiro rebal a carteira está em caixa
    first = decisions[0]["date"] if decisions else assets.index[-1]
    port_ret.loc[:first] = cdi.loc[:first]

    equity = cfg["backtest"]["initial_capital"] * (1 + port_ret).cumprod()
    return BacktestResult(equity, port_ret, pd.DataFrame(decisions), target)


def run_benchmarks(assets: pd.DataFrame, ibov: pd.Series, cdi: pd.Series, cfg: dict):
    """Curvas IBOV buy&hold e CDI, no mesmo calendário."""
    cap = cfg["backtest"]["initial_capital"]
    ibov_eq = cap * (1 + ibov.pct_change().fillna(0)).cumprod()
    cdi_eq = cap * (1 + cdi).cumprod()
    return ibov_eq, cdi_eq
