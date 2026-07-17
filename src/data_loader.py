"""Download e cache de dados: preços (yfinance) e CDI (BCB SGS).

Todos os dados brutos são salvos em data/raw (parquet) na primeira execução;
execuções seguintes leem do cache — nunca baixamos dados dentro do loop do backtest.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_config(path: str | Path = ROOT / "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _raw_dir(cfg: dict) -> Path:
    d = ROOT / cfg["data"]["raw_dir"]
    d.mkdir(parents=True, exist_ok=True)
    return d


def download_prices(cfg: dict, force: bool = False) -> pd.DataFrame:
    """Preços de fechamento ajustados (auto_adjust=True) dos tickers + índice.

    Retorna DataFrame diário (index=DatetimeIndex, colunas=tickers).
    """
    cache = _raw_dir(cfg) / "prices.parquet"
    if cache.exists() and not force:
        return pd.read_parquet(cache)

    import yfinance as yf

    tickers = list(cfg["universe"]["tickers"]) + [cfg["universe"]["index"]]
    raw = yf.download(
        tickers,
        start=cfg["period"]["start"],
        end=cfg["period"]["end"],
        auto_adjust=True,
        progress=False,
    )
    prices = raw["Close"].sort_index()
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None)
    prices.to_parquet(cache)
    return prices


def download_cdi(cfg: dict, force: bool = False) -> pd.Series:
    """CDI diário (fração decimal por dia útil) via API SGS do BCB, série 12.

    Fallback: taxa anual constante de config (declarada como limitação no relatório).
    """
    cache = _raw_dir(cfg) / "cdi.parquet"
    if cache.exists() and not force:
        return pd.read_parquet(cache)["cdi"]

    serie = cfg["data"]["cdi_sgs_series"]
    start = dt.datetime.strptime(cfg["period"]["start"], "%Y-%m-%d")
    end = dt.datetime.strptime(cfg["period"]["end"], "%Y-%m-%d")
    try:
        # a API SGS limita séries diárias a ~10 anos por requisição → fatiar em janelas de 8 anos
        frames = []
        cur = start
        while cur <= end:
            chunk_end = min(cur + dt.timedelta(days=8 * 365), end)
            url = (
                f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados"
                f"?formato=json&dataInicial={cur:%d/%m/%Y}&dataFinal={chunk_end:%d/%m/%Y}"
            )
            resp = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            frames.append(pd.DataFrame(resp.json()))
            cur = chunk_end + dt.timedelta(days=1)
        df = pd.concat(frames, ignore_index=True).drop_duplicates(subset="data")
        cdi = pd.Series(
            pd.to_numeric(df["valor"]).values / 100.0,
            index=pd.to_datetime(df["data"], format="%d/%m/%Y"),
            name="cdi",
        ).sort_index()
    except Exception as exc:  # fallback declarado
        print(f"[data_loader] AVISO: API SGS falhou ({exc}); usando CDI constante de fallback.")
        idx = pd.bdate_range(cfg["period"]["start"], cfg["period"]["end"])
        daily = (1 + cfg["data"]["cdi_fallback_annual"]) ** (1 / 252) - 1
        cdi = pd.Series(daily, index=idx, name="cdi")

    cdi.to_frame().to_parquet(cache)
    return cdi


def load_all(cfg: dict | None = None, force: bool = False):
    """Conveniência: (prices_ativos, ibov, cdi) alinhados ao calendário de pregões."""
    cfg = cfg or load_config()
    prices = download_prices(cfg, force=force)
    cdi = download_cdi(cfg, force=force)
    ibov = prices[cfg["universe"]["index"]].dropna()
    assets = prices[cfg["universe"]["tickers"]].reindex(ibov.index)
    cdi = cdi.reindex(ibov.index).ffill().fillna(0.0)
    return assets, ibov, cdi


if __name__ == "__main__":
    cfg = load_config()
    assets, ibov, cdi = load_all(cfg)
    print("Ativos:", assets.shape, "| IBOV:", ibov.shape, "| CDI:", cdi.shape)
    print("Período:", assets.index.min().date(), "→", assets.index.max().date())
    print("NaNs por ativo:\n", assets.isna().sum())
