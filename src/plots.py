"""Figuras do relatório — sempre 16:9, salvas em reports/figures."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

FIGSIZE = (12.8, 7.2)  # 16:9


def _save(fig, out: Path, name: str):
    out.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out / name, dpi=150)
    plt.close(fig)


def equity_curves(curves: dict[str, pd.Series], out: Path, log: bool = True):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for name, eq in curves.items():
        ax.plot(eq.index, eq.values, label=name, lw=1.6)
    if log:
        ax.set_yscale("log")
    ax.set_title("Curvas de patrimônio (base 1.0)")
    ax.legend()
    ax.grid(alpha=0.3)
    _save(fig, out, "equity_curves.png")


def drawdowns(curves: dict[str, pd.Series], out: Path):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for name, eq in curves.items():
        dd = eq / eq.cummax() - 1
        ax.plot(dd.index, dd.values, label=name, lw=1.2)
    ax.set_title("Drawdown")
    ax.legend()
    ax.grid(alpha=0.3)
    _save(fig, out, "drawdowns.png")


def regime_timeline(ibov: pd.Series, bull: pd.Series, out: Path):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(ibov.index, ibov.values, color="k", lw=1, label="IBOV")
    bear = (~bull.fillna(False)).astype(bool)
    ax.fill_between(ibov.index, ibov.min(), ibov.max(), where=bear,
                    color="crimson", alpha=0.15, label="BEAR")
    ax.set_title("IBOV e regimes (vermelho = BEAR)")
    ax.legend()
    ax.grid(alpha=0.3)
    _save(fig, out, "regime_timeline.png")
