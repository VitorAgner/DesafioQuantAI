# Relatório de Progresso — Projeto Sentinel

**Data:** 17/07/2026 · **Repositório:** [github.com/Tatzumikk/DesafioQuantAI](https://github.com/Tatzumikk/DesafioQuantAI) (privado) · **Commit:** `663656b`

## Situação geral

O plano previa o "esqueleto ponta a ponta até 24/07" — ele ficou pronto **no primeiro dia (17/07)**, cobrindo as Fases 1 a 3 integralmente e boa parte da Fase 4. Estamos cerca de uma semana à frente do cronograma, com folga confortável para o pré-relatório de 31/07.

## Entregas por fase

| Fase (prazo do plano) | Status | Evidência |
|---|---|---|
| 1 — Infra e dados (17–19/07) | ✅ Concluída | Loader com cache parquet; 10 tickers + IBOV + CDI real do BCB alinhados sem NaNs estruturais |
| 2 — Sinais (19–21/07) | ✅ Concluída | Regime SMA200 (+histerese) e momentum 12-1; timeline de regime coerente com as crises conhecidas (2011–16, COVID) |
| 3 — Backtest + benchmarks (21–24/07) | ✅ Concluída | 4 curvas geradas, log de decisões em CSV, 10 testes passando |
| 4 — Métricas e análise (24–27/07) | 🟡 Parcial | Tabela de métricas e grade de sensibilidade prontas; falta análise qualitativa (crises, whipsaws, limitações) |
| 5 — Pré-relatório (até 31/07) | ⬜ Não iniciada | — |
| 6 — Relatório final (até 17/08) | ⬜ Não iniciada | — |

## Qualidade e anti-vieses (o que já protege a nota)

- **Look-ahead:** sinal em t, execução em t+1; testes automatizados provam que mutar dados futuros não altera o sinal.
- **Overfitting:** parâmetros da literatura (SMA200, 12-1, top-3); a grade de sensibilidade é apresentada como robustez.
- **Reprodutibilidade:** parâmetros só via `config.yaml`; dados cacheados; toda decisão mensal logada em CSV.
- **AI_LOG.md ativo** com 3 entradas, incluindo um erro sutil real da IA (bug de dtype que pintava o gráfico inteiro de BEAR) — exemplo pronto para o critério de GenAI (15%).

## Resultados atuais (base, sem custos, 2010–jun/2026)

| Estratégia | CAGR | Vol | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|
| **Sentinel** | 11,9% | 18,6% | 0,20 | **−27,9%** | **0,43** |
| Momentum puro | 18,3% | 25,3% | 0,43 | −47,1% | 0,39 |
| IBOV | 5,6% | 23,0% | −0,05 | −48,6% | 0,12 |
| CDI | 9,7% | — | — | 0,0% | — |

**Leitura:** o filtro de regime entrega o que a tese promete no risco (drawdown quase pela metade, melhor Calmar), mas custa retorno — o momentum puro supera o Sentinel em CAGR e Sharpe nesta janela. A sensibilidade mostra SMA=100 bem melhor (CAGR 16%) e momentum 6-1 bem pior; custos de 0,1–0,2% tiram só ~0,8–1,5 p.p. de CAGR.

## Decisões tomadas no caminho

1. **10º ativo = SUZB3** (ELET3.SA não existe no Yahoo Finance; SUZB3 tem histórico desde 2010).
2. **CDI fatiado em janelas de 8 anos** — a API SGS do BCB rejeita séries diárias com intervalo maior que 10 anos.

## Próximos passos (Fase 4 restante)

1. Análise das janelas de estresse (2015–16 e mar/2020): quanto drawdown o filtro evitou, quanto de recuperação perdeu.
2. Contagem e custo dos whipsaws (liga/desliga do filtro).
3. Decisão de narrativa pendente: defender o Sentinel pelo Calmar/drawdown como está, ou incorporar a evidência da SMA mais curta — sem otimizar a posteriori.
4. Seção de limitações honestas + seleção das 4–5 figuras do pré-relatório.

**Ponto de atenção:** o repo está na conta pessoal `Tatzumikk`; se o repositório for submetido junto com o PDF, o anonimato (critério eliminatório) exige migrar para conta neutra.
