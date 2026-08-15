"""Gráficos do relatório gerados NO TAMANHO REAL DE EXIBIÇÃO.

O edital exige leitura em tela cheia sem zoom. Um gráfico autorado em 16x9 pol e
depois reduzido a meia página tem suas fontes reduzidas na mesma proporção
(10pt viram ~4pt). Aqui cada figura é criada já com a largura em polegadas que
terá na página, de modo que os tamanhos de fonte em pontos são os finais.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from src.backtest import run_backtest, run_benchmarks
from src.data_loader import load_all, load_config
from src.regime import regime_series

FIG_DIR = ROOT / "reports" / "figures"
C_SENT, C_MOM, C_IBOV, C_CDI, C_BEAR = "#1f3b73", "#e67e22", "#7f8c8d", "#b0b0b0", "#c0392b"

# a página tem 13,333 pol de largura = 16 unidades do sistema de layout
UNIT_IN = 13.333 / 16.0

plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 9.5, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
    "axes.linewidth": 0.8, "grid.linewidth": 0.5,
})


def save(fig, nome):
    fig.savefig(FIG_DIR / nome, dpi=200, facecolor="white", bbox_inches="tight",
                pad_inches=0.02)
    plt.close(fig)
    print(f"[chart] {nome}  ({fig.get_size_inches()[0]:.2f} x {fig.get_size_inches()[1]:.2f} pol)")


def shade_bear(ax, bull):
    bear = (~bull.fillna(False)).astype(bool)
    ax.fill_between(bull.index, 0, 1, where=bear, transform=ax.get_xaxis_transform(),
                    color=C_BEAR, alpha=0.10, linewidth=0)


def main():
    cfg = load_config()
    assets, ibov, cdi = load_all(cfg)
    ibov_ret = ibov.pct_change().fillna(0)
    bull = regime_series(ibov, cfg["regime"]["sma_window"], cfg["regime"]["hysteresis_band"])

    sent = run_backtest(assets, ibov, cdi, cfg, use_regime=True)
    mom = run_backtest(assets, ibov, cdi, cfg, use_regime=False)
    ibov_eq, cdi_eq = run_benchmarks(assets, ibov, cdi, cfg)

    # ---- página 3, esquerda: curvas de patrimônio (6,9 unidades de largura)
    fig, ax = plt.subplots(figsize=(6.9 * UNIT_IN, 3.55))
    for label, eq, color in [("Sentinel", sent.equity, C_SENT),
                             ("Momentum puro", mom.equity, C_MOM),
                             ("IBOV", ibov_eq, C_IBOV), ("CDI", cdi_eq, C_CDI)]:
        ax.plot(eq.index, eq.values, label=label, color=color, lw=1.2)
    shade_bear(ax, bull)
    ax.set_yscale("log")
    ax.legend(loc="upper left", framealpha=0.9)
    ax.grid(alpha=0.3)
    ax.margins(x=0.01)
    save(fig, "P3_curvas.png")

    # ---- página 4, esquerda: drawdown (7,3 unidades, faixa baixa)
    fig, ax = plt.subplots(figsize=(7.3 * UNIT_IN, 1.95))
    for label, eq, color in [("Sentinel", sent.equity, C_SENT),
                             ("Momentum puro", mom.equity, C_MOM)]:
        dd = eq / eq.cummax() - 1
        ax.plot(dd.index, dd.values, label=label, color=color, lw=1.1)
        ax.fill_between(dd.index, dd.values, 0, color=color, alpha=0.15)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.legend(loc="lower left", framealpha=0.9, ncol=2)
    ax.grid(alpha=0.3)
    ax.margins(x=0.01)
    save(fig, "P4_drawdown.png")

    # ---- página 4, direita: crises (7,3 unidades, dois painéis)
    windows = {"Bear 2015-16": ("2014-09-01", "2016-12-31"),
               "COVID 2020": ("2020-01-01", "2020-12-31")}
    fig, axes = plt.subplots(1, 2, figsize=(7.3 * UNIT_IN, 1.95))
    for ax, (nome, (ini, fim)) in zip(axes, windows.items()):
        for label, r, color in [("Sentinel", sent.daily_returns, C_SENT),
                                ("Momentum puro", mom.daily_returns, C_MOM),
                                ("IBOV", ibov_ret, C_IBOV)]:
            eq = 100 * (1 + r.loc[ini:fim]).cumprod()
            ax.plot(eq.index, eq.values, label=label, color=color, lw=1.1)
        shade_bear(ax, bull.loc[ini:fim])
        ax.set_title(nome, fontsize=8.5)
        ax.grid(alpha=0.3)
        ax.margins(x=0.01)
        ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
    axes[0].legend(loc="lower right", framealpha=0.9)
    fig.tight_layout(pad=0.3)
    save(fig, "P4_crises.png")


if __name__ == "__main__":
    main()
