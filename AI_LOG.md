# AI_LOG — Registro de uso de IA Generativa no projeto Sentinel

| Data | Etapa | Ferramenta | O que foi pedido | O que foi aproveitado | O que foi descartado / observações |
|---|---|---|---|---|---|
| 2026-07-17 | Ideação | Claude (chat) | Refinamento da hipótese momentum + filtro de regime, discussão de vieses | Tese no formato "X porque Y, portanto Z"; lista de vieses (look-ahead, sobrevivência, cherry-picking, overfitting) e mitigações | — |
| 2026-07-17 | Código (Fase 1–3) | Claude Code | Geração da estrutura do repositório: data_loader (yfinance + BCB SGS com cache), regime SMA200 c/ histerese, momentum 12-1, loop de backtest com defasagem t+1, métricas, testes anti-look-ahead | Esqueleto completo ponta a ponta; 10 testes passando; 4 curvas geradas | 10º ativo trocado de ELET3 para SUZB3 (ELET3.SA não existe no Yahoo Finance; SUZB3 tem histórico desde 2010) |
| 2026-07-17 | Código — **limitação encontrada** | Claude Code | Figura da timeline de regime | Corrigida pela própria sessão após inspeção visual | **Erro sutil gerado pela IA:** a série de regime saía com dtype `object`; `~True` em Python avalia para `-2`, fazendo o gráfico pintar 100% do período como BEAR. O backtest não era afetado, só a figura. Correção: forçar dtype `boolean` em `regime_series`. Exemplo concreto para a seção de GenAI do relatório. |
| 2026-07-17 | Código — dados | Claude Code | Download do CDI via API SGS do BCB | Requisição fatiada em janelas de 8 anos + header User-Agent | API SGS retorna 406 para séries diárias com intervalo > 10 anos — a IA só tratou isso após o erro real aparecer |
