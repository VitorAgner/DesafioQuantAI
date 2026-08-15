"""Fase 4 — Blocos 2 (crises), 3 (whipsaws), 4 (robustez) e 6 (figuras F1–F5).

Gera: reports/analise_crises.csv, analise_whipsaws.csv, sensibilidade.csv
e as 5 figuras candidatas ao pré-relatório (paleta sóbria, 16:9, sem
informação identificadora).
"""
import copy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from src.backtest import run_backtest, run_benchmarks
from src.data_loader import load_all, load_config
from src.metrics import cagr, calmar, max_drawdown, regime_decomposition, sharpe
from src.regime import regime_series

# paleta sóbria: azul-escuro Sentinel, cinzas p/ benchmarks, tom de alerta p/ BEAR
C_SENT, C_MOM, C_IBOV, C_CDI, C_BEAR = "#1f3b73", "#e67e22", "#7f8c8d", "#b0b0b0", "#c0392b"
FIGSIZE, DPI = (12.8, 7.2), 150
FIG_DIR = ROOT / "reports" / "figures"
plt.rcParams.update({"font.size": 13, "axes.titlesize": 16, "legend.fontsize": 13})


def shade_bear(ax, bull: pd.Series):
    bear = (~bull.fillna(False)).astype(bool)
    ax.fill_between(bull.index, 0, 1, where=bear, transform=ax.get_xaxis_transform(),
                    color=C_BEAR, alpha=0.10, linewidth=0)


def save(fig, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / name, dpi=DPI)
    plt.close(fig)
    print(f"[fig] {name}")


def window_dd(returns: pd.Series, start, end) -> float:
    eq = (1 + returns.loc[start:end]).cumprod()
    return max_drawdown(eq)


def window_ret(returns: pd.Series, start, end) -> float:
    return float((1 + returns.loc[start:end]).prod() - 1)


def main():
    cfg = load_config()
    assets, ibov, cdi = load_all(cfg)
    ibov_ret = ibov.pct_change().fillna(0)
    bull = regime_series(ibov, cfg["regime"]["sma_window"], cfg["regime"]["hysteresis_band"])

    sent = run_backtest(assets, ibov, cdi, cfg, use_regime=True)
    mom = run_backtest(assets, ibov, cdi, cfg, use_regime=False)
    ibov_eq, cdi_eq = run_benchmarks(assets, ibov, cdi, cfg)

    # ------------------------------------------------------------------ Bloco 2
    windows = {
        "Bear 2015-16": ("2014-09-01", "2016-12-31"),
        "COVID 2020": ("2020-01-01", "2020-12-31"),
    }
    dec = sent.decisions.set_index("date")
    crises = []
    for name, (start, end) in windows.items():
        w = dec.loc[start:end]
        bear_dates = w.index[w["regime"] == "BEAR"]
        exit_date = bear_dates[0] if len(bear_dates) else pd.NaT
        reentry = pd.NaT
        if pd.notna(exit_date):
            after = dec.loc[exit_date:]
            bulls = after.index[after["regime"] == "BULL"]
            reentry = bulls[0] if len(bulls) else pd.NaT
        bottom = ibov.loc[start:end].idxmin()
        missed = (ibov.loc[:reentry].iloc[-1] / ibov.loc[bottom] - 1) if pd.notna(reentry) else np.nan
        dd_s = window_dd(sent.daily_returns, start, end)
        dd_m = window_dd(mom.daily_returns, start, end)
        crises.append({
            "Janela": name, "Início": start, "Fim": end,
            "Ret Sentinel": window_ret(sent.daily_returns, start, end),
            "Ret Momentum puro": window_ret(mom.daily_returns, start, end),
            "Ret IBOV": window_ret(ibov_ret, start, end),
            "MaxDD Sentinel": dd_s, "MaxDD Momentum puro": dd_m,
            "MaxDD IBOV": window_dd(ibov_ret, start, end),
            "Saída do risco": exit_date, "Reentrada": reentry,
            "Fundo IBOV": bottom,
            "Recuperação perdida (IBOV fundo→reentrada)": missed,
            "Drawdown evitado (p.p.)": (dd_s - dd_m) * 100,  # |DD mom| − |DD sentinel|
        })
    crises_df = pd.DataFrame(crises)
    crises_df.to_csv(ROOT / "reports" / "analise_crises.csv", index=False)
    print(crises_df.to_string())

    # F3 — zoom das crises (painel duplo, normalizado em 100)
    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE)
    for ax, (name, (start, end)) in zip(axes, windows.items()):
        for label, r, color in [("Sentinel", sent.daily_returns, C_SENT),
                                ("Momentum puro", mom.daily_returns, C_MOM),
                                ("IBOV", ibov_ret, C_IBOV)]:
            eq = 100 * (1 + r.loc[start:end]).cumprod()
            ax.plot(eq.index, eq.values, label=label, color=color, lw=1.6)
        shade_bear(ax, bull.loc[start:end])
        ax.set_title(name)
        ax.grid(alpha=0.3)
        ax.tick_params(axis="x", rotation=30)
    axes[0].legend()
    fig.suptitle("Crises: curvas normalizadas (100 = início da janela; faixas = BEAR)")
    save(fig, "F3_zoom_crises.png")

    # ------------------------------------------------------------------ Bloco 3
    def whipsaw_table(decisions: pd.DataFrame) -> pd.DataFrame:
        reg = decisions["regime"].values
        dates = decisions["date"].values
        runs, start_i = [], 0
        for i in range(1, len(reg) + 1):
            if i == len(reg) or reg[i] != reg[start_i]:
                runs.append({"regime": reg[start_i], "start": dates[start_i],
                             "end": dates[i - 1], "len": i - start_i})
                start_i = i
        df = pd.DataFrame(runs)
        # whipsaw: permanência ≤ 2 rebalanceamentos antes de reverter (exclui o último run)
        df["whipsaw"] = df["len"] <= 2
        df.loc[df.index[-1], "whipsaw"] = False
        return df

    runs = whipsaw_table(sent.decisions)
    for i, r in runs.iterrows():
        s, e = r["start"], r["end"]
        runs.loc[i, "ret_sentinel"] = window_ret(sent.daily_returns, s, e)
        runs.loc[i, "ret_momentum"] = window_ret(mom.daily_returns, s, e)
    runs["custo_vs_momentum"] = runs["ret_sentinel"] - runs["ret_momentum"]
    runs.to_csv(ROOT / "reports" / "analise_whipsaws.csv", index=False)

    n_switches = len(runs) - 1
    ws = runs[runs["whipsaw"]]
    print(f"\n[whipsaws] trocas de regime: {n_switches} | runs whipsaw (≤2 rebal): {len(ws)} "
          f"| custo médio vs momentum puro por whipsaw: {ws['custo_vs_momentum'].mean():.4%}")

    # comparativo com histerese ±2%
    cfg_h = copy.deepcopy(cfg)
    cfg_h["regime"]["hysteresis_band"] = 0.02
    sent_h = run_backtest(assets, ibov, cdi, cfg_h, use_regime=True)
    runs_h = whipsaw_table(sent_h.decisions)
    print(f"[histerese ±2%] trocas: {len(runs_h) - 1} | whipsaws: {int(runs_h['whipsaw'].sum())} "
          f"| CAGR {cagr(sent_h.equity):.4f} vs base {cagr(sent.equity):.4f} "
          f"| MaxDD {max_drawdown(sent_h.equity):.4f} vs base {max_drawdown(sent.equity):.4f}")

    # ------------------------------------------------------------------ Bloco 4
    grid = [("SMA100", ("regime", "sma_window"), 100),
            ("SMA150", ("regime", "sma_window"), 150),
            ("SMA200 (base)", None, None),
            ("Mom 6-1", ("momentum", "lookback_months"), 6),
            ("Mom 9-1", ("momentum", "lookback_months"), 9),
            ("Mom 12-1 (base)", None, None),
            ("Custo 0,10%", ("backtest", "cost_per_trade"), 0.001),
            ("Custo 0,20%", ("backtest", "cost_per_trade"), 0.002),
            ("Sem custo (base)", None, None)]
    rows = []
    for name, key, val in grid:
        c = copy.deepcopy(cfg)
        if key:
            c[key[0]][key[1]] = val
        r = run_backtest(assets, ibov, cdi, c, use_regime=True)
        rows.append({"Cenário": name, "CAGR": cagr(r.equity),
                     "Sharpe": sharpe(r.daily_returns, cdi),
                     "MaxDD": max_drawdown(r.equity), "Calmar": calmar(r.equity)})
    sens = pd.DataFrame(rows).set_index("Cenário")
    sens.to_csv(ROOT / "reports" / "sensibilidade.csv")
    print("\n", sens.to_string())

    # F5 — tabela de sensibilidade como figura
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.axis("off")
    cell = sens.copy()
    cell["CAGR"] = cell["CAGR"].map("{:.1%}".format)
    cell["Sharpe"] = cell["Sharpe"].map("{:.2f}".format)
    cell["MaxDD"] = cell["MaxDD"].map("{:.1%}".format)
    cell["Calmar"] = cell["Calmar"].map("{:.2f}".format)
    tbl = ax.table(cellText=cell.values, rowLabels=cell.index, colLabels=cell.columns,
                   loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(14)
    tbl.scale(1, 2.2)
    ax.set_title("Sensibilidade de parâmetros (base: SMA200, mom 12-1, top-3, sem custos)")
    save(fig, "F5_sensibilidade.png")

    # ------------------------------------------------------------------ Figuras F1, F2, F4
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for label, eq, color in [("Sentinel", sent.equity, C_SENT),
                             ("Momentum puro", mom.equity, C_MOM),
                             ("IBOV", ibov_eq, C_IBOV), ("CDI", cdi_eq, C_CDI)]:
        ax.plot(eq.index, eq.values, label=label, color=color, lw=1.6)
    shade_bear(ax, bull)
    ax.set_yscale("log")
    ax.set_title("Curvas de patrimônio 2010–2026 (base 1,0; escala log; faixas = BEAR)")
    ax.legend()
    ax.grid(alpha=0.3)
    save(fig, "F1_curvas_patrimonio.png")

    fig, ax = plt.subplots(figsize=FIGSIZE)
    for label, eq, color in [("Sentinel", sent.equity, C_SENT),
                             ("Momentum puro", mom.equity, C_MOM)]:
        dd = eq / eq.cummax() - 1
        ax.plot(dd.index, dd.values, label=label, color=color, lw=1.4)
        ax.fill_between(dd.index, dd.values, 0, color=color, alpha=0.15)
    ax.set_title("Drawdown: Sentinel × momentum puro")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.legend()
    ax.grid(alpha=0.3)
    save(fig, "F2_drawdown.png")

    # F2W / F3W — variantes largas (16:5) para a página de resultados do relatório,
    # onde a tabela de métricas consome a altura que uma figura 16:9 exigiria
    WIDE = (16, 5)
    fig, ax = plt.subplots(figsize=WIDE)
    for label, eq, color in [("Sentinel", sent.equity, C_SENT),
                             ("Momentum puro", mom.equity, C_MOM)]:
        dd = eq / eq.cummax() - 1
        ax.plot(dd.index, dd.values, label=label, color=color, lw=1.4)
        ax.fill_between(dd.index, dd.values, 0, color=color, alpha=0.15)
    ax.set_title("Drawdown: Sentinel × momentum puro")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.legend(loc="lower left")
    ax.grid(alpha=0.3)
    save(fig, "F2W_drawdown_wide.png")

    fig, axes = plt.subplots(1, 2, figsize=WIDE)
    for ax, (name, (start, end)) in zip(axes, windows.items()):
        for label, r, color in [("Sentinel", sent.daily_returns, C_SENT),
                                ("Momentum puro", mom.daily_returns, C_MOM),
                                ("IBOV", ibov_ret, C_IBOV)]:
            eq = 100 * (1 + r.loc[start:end]).cumprod()
            ax.plot(eq.index, eq.values, label=label, color=color, lw=1.5)
        shade_bear(ax, bull.loc[start:end])
        ax.set_title(name)
        ax.grid(alpha=0.3)
        ax.tick_params(axis="x", rotation=30, labelsize=10)
    axes[0].legend(fontsize=10)
    fig.suptitle("Crises: curvas normalizadas (100 = início da janela; faixas = BEAR)")
    save(fig, "F3W_crises_wide.png")

    # F4 — decomposição BULL × CDI (curvas acumuladas por regime)
    stock_cols = [c for c in sent.weights_daily.columns if c != "CDI"]
    in_risk = (sent.weights_daily[stock_cols].sum(axis=1) > 0)
    r = sent.daily_returns
    bull_curve = (1 + r.where(in_risk, 0.0)).cumprod()
    bear_curve = (1 + r.where(~in_risk, 0.0)).cumprod()
    d = regime_decomposition(r, sent.weights_daily)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(bull_curve.index, bull_curve.values, color=C_SENT,
            label=f"Contribuição BULL/ações (fator {d['factor_bull']:.2f}x)", lw=1.6)
    ax.plot(bear_curve.index, bear_curve.values, color=C_BEAR,
            label=f"Contribuição BEAR/CDI (fator {d['factor_bear']:.2f}x)", lw=1.6)
    ax.plot(sent.equity.index, sent.equity.values, color="k", ls="--",
            label=f"Sentinel total ({d['factor_total']:.2f}x)", lw=1.2)
    ax.set_yscale("log")
    ax.set_title("Decomposição do retorno do Sentinel por regime (produto de fatores)")
    ax.legend()
    ax.grid(alpha=0.3)
    save(fig, "F4_decomposicao_regime.png")


if __name__ == "__main__":
    main()
