"""Roda o cenário base: Sentinel + ablação (momentum puro) + benchmarks (IBOV, CDI)."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.backtest import run_backtest, run_benchmarks
from src.data_loader import load_all, load_config
from src.plots import drawdowns, equity_curves, regime_timeline
from src.regime import regime_series
from src.metrics import summary


def main():
    cfg = load_config()
    assets, ibov, cdi = load_all(cfg)
    fig_dir = ROOT / cfg["output"]["figures_dir"]

    sentinel = run_backtest(assets, ibov, cdi, cfg, use_regime=True)
    mom_puro = run_backtest(assets, ibov, cdi, cfg, use_regime=False)
    ibov_eq, cdi_eq = run_benchmarks(assets, ibov, cdi, cfg)

    log_path = ROOT / cfg["output"]["decisions_log"]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    sentinel.decisions.to_csv(log_path, index=False)

    curves = {"Sentinel": sentinel.equity, "Momentum puro": mom_puro.equity,
              "IBOV": ibov_eq, "CDI": cdi_eq}
    equity_curves(curves, fig_dir)
    drawdowns(curves, fig_dir)
    bull = regime_series(ibov, cfg["regime"]["sma_window"], cfg["regime"]["hysteresis_band"])
    regime_timeline(ibov, bull, fig_dir)

    rows = [
        summary("Sentinel", sentinel.equity, sentinel.daily_returns, cdi, sentinel.decisions),
        summary("Momentum puro", mom_puro.equity, mom_puro.daily_returns, cdi, mom_puro.decisions),
        summary("IBOV", ibov_eq, ibov.pct_change().fillna(0), cdi),
        summary("CDI", cdi_eq, cdi, cdi),
    ]
    table = pd.DataFrame(rows).set_index("Estratégia")
    table.to_csv(ROOT / "reports" / "metrics_summary.csv")
    pd.set_option("display.float_format", "{:.4f}".format)
    print(table)
    print(f"\nFiguras em {fig_dir} | Log de decisões em {log_path}")


if __name__ == "__main__":
    main()
