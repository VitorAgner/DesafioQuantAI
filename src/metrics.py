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
    """Sharpe anualizado sobre o excesso diário em relação ao CDI.

    Definição única do projeto (Bloco 1.1 da Fase 4):
        excesso_t = r_t − cdi_t   (retornos diários simples)
        Sharpe    = mean(excesso_t) × 252 / (std(excesso_t) × √252)
                  = mean(excesso_t) / std(excesso_t) × √252

    Nota: usa média ARITMÉTICA do excesso diário — portanto NÃO é
    (CAGR − CDI) / Vol, que usa composição geométrica. A mesma função é
    aplicada a todas as curvas; para o próprio CDI não se reporta Sharpe.
    """
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


def risk_exposure(weights_daily: pd.DataFrame) -> float:
    """Fração dos dias úteis com peso > 0 em ações (colunas != CDI)."""
    stock_cols = [c for c in weights_daily.columns if c != "CDI"]
    return (weights_daily[stock_cols].sum(axis=1) > 0).mean()


def regime_stats(decisions: pd.DataFrame) -> dict:
    """Nº de meses em BEAR e nº de trocas de regime no log de decisões."""
    reg = decisions["regime"]
    return {
        "Meses em BEAR": int((reg == "BEAR").sum()),
        "Trocas de regime": int((reg != reg.shift()).sum() - 1),
    }


def annual_turnover(decisions: pd.DataFrame, equity: pd.Series) -> float:
    """Σ |Δpesos| nos rebalanceamentos ÷ nº de anos (inclui migração p/ CDI)."""
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return decisions["turnover"].sum() * 2 / years  # turnover do log é one-way (Σ|Δw|/2)


def summary(name: str, equity: pd.Series, returns: pd.Series, cdi: pd.Series,
            decisions: pd.DataFrame | None = None,
            weights_daily: pd.DataFrame | None = None,
            is_cdi: bool = False) -> dict:
    out = {
        "Estratégia": name,
        "CAGR": cagr(equity),
        "Vol anual": ann_vol(returns),
        # CDI é a própria taxa livre de risco — Sharpe não se aplica
        "Sharpe": float("nan") if is_cdi else sharpe(returns, cdi),
        "Max DD": max_drawdown(equity),
        "Calmar": calmar(equity),
        "% meses positivos": pct_positive_months(returns),
    }
    if weights_daily is not None:
        out["Exposição a risco"] = risk_exposure(weights_daily)
    if decisions is not None and len(decisions):
        out.update(regime_stats(decisions))
        out["Turnover anual"] = annual_turnover(decisions, equity)
    return out


def regime_decomposition(returns: pd.Series, weights_daily: pd.DataFrame) -> dict:
    """Decompõe o retorno total em fatores BULL (em ações) × BEAR (em CDI).

    Produto de fatores por sub-período: fator_BULL × fator_BEAR == (1 + ret_total),
    logo os logs somam exatamente — propriedade usada em test_decomposition.py.
    """
    stock_cols = [c for c in weights_daily.columns if c != "CDI"]
    in_risk = (weights_daily[stock_cols].sum(axis=1) > 0).reindex(returns.index).fillna(False)
    factor_bull = float((1 + returns[in_risk]).prod())
    factor_bear = float((1 + returns[~in_risk]).prod())
    return {"factor_bull": factor_bull, "factor_bear": factor_bear,
            "factor_total": float((1 + returns).prod())}
