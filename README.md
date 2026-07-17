# Sentinel — Momentum condicionado a regime de mercado

> Robô quantitativo para o Desafio Itaú Asset Quant AI 2026. O Sentinel é a sentinela que vigia o regime do mercado antes de deixar a carteira avançar: só assume risco de momentum quando o filtro de regime indica mercado saudável; caso contrário, recua para o CDI.

## Tese

Acredito que o momentum funciona melhor em mercados de alta **porque** em regimes de baixa a correlação entre ativos sobe, tendências se revertem abruptamente e vencedores recentes tendem a ser os ativos mais castigados nas reversões. **Portanto**, testamos uma carteira de momentum que só assume risco quando um filtro de regime indica mercado saudável, migrando para renda fixa (CDI) caso contrário.

Referências: Jegadeesh & Titman (1993); Moskowitz, Ooi & Pedersen (2012); Daniel & Moskowitz (2016, *momentum crashes*); Faber (2007).

## Modelo (2 camadas)

1. **Filtro de regime:** BULL se IBOV > SMA200 (avaliado apenas no rebalanceamento mensal). Em BEAR, 100% em CDI. Variante de robustez: histerese ±2%.
2. **Momentum 12-1:** retorno acumulado de 12 meses excluindo o último mês; compra os top 3 do universo em pesos iguais.

**Universo:** 10 ações brasileiras líquidas de grande capitalização (PETR4, VALE3, ITUB4, BBDC4, BBAS3, ABEV3, WEGE3, RENT3, B3SA3, SUZB3). O viés de sobrevivência da lista é declarado e discutido na análise.

## Backtest

- **Período:** jan/2010 → jun/2026 (múltiplos regimes: bear 2011–16, Joesley Day, COVID, ciclos de juros).
- **Dados:** yfinance com preços ajustados; CDI diário real via API SGS do Banco Central (série 12), com cache local em `data/raw/`.
- **Anti-vieses:** sinal calculado com dados até t, execução em t+1 (testado em `tests/test_no_lookahead.py`); parâmetros vindos da literatura, não de otimização; sensibilidade apresentada como robustez; toda decisão logada em CSV.
- **Ablação:** 4 curvas comparadas — Sentinel, momentum puro (sem filtro), IBOV buy & hold e CDI.

## Resultados do cenário base (sem custos)

| Estratégia | CAGR | Vol anual | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|
| **Sentinel** | 11,9% | 18,6% | 0,20 | **−27,9%** | **0,43** |
| Momentum puro | 18,3% | 25,3% | 0,43 | −47,1% | 0,39 |
| IBOV | 5,6% | 23,0% | −0,05 | −48,6% | 0,12 |
| CDI | 9,7% | — | — | 0,0% | — |

O filtro de regime cumpre o objetivo de gestão de risco (drawdown quase pela metade, melhor Calmar), ao custo de parte relevante do retorno do momentum — trade-off discutido honestamente na análise.

## Como rodar

```bash
pip install -r requirements.txt
python scripts/run_backtest.py      # cenário base + ablações + benchmarks + figuras
python scripts/run_sensitivity.py   # grade de sensibilidade (SMA, janela, top-N, custos)
python -m pytest tests -q           # testes (look-ahead, pesos, métricas)
```

Saídas em `reports/`: `metrics_summary.csv`, `sensitivity.csv`, `decisions_log.csv` e figuras 16:9 em `reports/figures/`.

## Estrutura

```
config.yaml          # todos os parâmetros (única fonte de verdade)
AI_LOG.md            # registro de usos de IA generativa no projeto
src/                 # data_loader, regime, momentum, backtest, metrics, plots
scripts/             # run_backtest, run_sensitivity
tests/               # anti-look-ahead, pesos, métricas
data/raw/            # cache local (não versionado)
reports/             # tabelas, log de decisões e figuras
```
