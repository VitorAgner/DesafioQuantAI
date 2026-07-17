"""Grade de sensibilidade: SMA (100/150/200), momentum (6-1/9-1/12-1), top-N (2/3/4), custos.

Apresentada como robustez, não como otimização (parâmetros base vêm da literatura).
"""
import copy
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.backtest import run_backtest
from src.data_loader import load_all, load_config
from src.metrics import summary


def main():
    base = load_config()
    assets, ibov, cdi = load_all(base)

    grid = [("base", {})]
    grid += [(f"sma={w}", {("regime", "sma_window"): w}) for w in (100, 150)]
    grid += [(f"mom={m}-1", {("momentum", "lookback_months"): m}) for m in (6, 9)]
    grid += [(f"top_n={n}", {("momentum", "top_n"): n}) for n in (2, 4)]
    grid += [(f"custo={c:.1%}", {("backtest", "cost_per_trade"): c}) for c in (0.001, 0.002)]
    grid += [("histerese=2%", {("regime", "hysteresis_band"): 0.02})]

    rows = []
    for name, overrides in grid:
        cfg = copy.deepcopy(base)
        for (sec, key), val in overrides.items():
            cfg[sec][key] = val
        res = run_backtest(assets, ibov, cdi, cfg, use_regime=True)
        rows.append(summary(name, res.equity, res.daily_returns, cdi, res.decisions))
        print(f"[ok] {name}")

    table = pd.DataFrame(rows).set_index("Estratégia")
    out = ROOT / "reports" / "sensitivity.csv"
    table.to_csv(out)
    pd.set_option("display.float_format", "{:.4f}".format)
    print(table)
    print(f"\nSalvo em {out}")


if __name__ == "__main__":
    main()
