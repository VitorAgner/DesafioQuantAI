# ANÁLISE — Sentinel (documento-fonte da Fase 4)

> Todas as afirmações quantitativas são rastreáveis aos arquivos em `reports/`: `tabela_metricas.csv`, `analise_crises.csv`, `analise_whipsaws.csv`, `sensibilidade.csv` e figuras F1–F5. Cenário-base: SMA200 / momentum 12-1 / top-3 / sem custos / jan-2010→jun-2026.

## 1. Resumo executivo

A tese confirmou-se **parcialmente**. O filtro de regime entrega a proteção prometida — o máximo drawdown cai de −47,1% (momentum puro) para −27,9%, e o Calmar sobe de 0,39 para 0,43 — ao custo de parte relevante do retorno: CAGR de 11,9% contra 18,3% do momentum puro, e Sharpe de 0,20 contra 0,43. No Brasil esse custo é amplificado pelo CDI historicamente alto (9,7% a.a. no período), que torna caro cada mês fora do risco por engano — o mesmo CDI que explica o IBOV (5,6% a.a.) perder do caixa na janela. O Sentinel é, portanto, uma estratégia de **gestão de risco condicional** que se paga em drawdown, não em retorno absoluto.

## 2. Comportamento ao longo do tempo

**Decomposição por regime** (F4, `test_decomposition.py` valida o fechamento): dos 6,42x acumulados do Sentinel, 3,32x vieram das posições de momentum em regime BULL e 1,93x do CDI em regime BEAR. O caixa remunerado não é acessório: responde por cerca de um terço do log-retorno total — consequência direta do nível de juros brasileiro, e um resultado que não se transporta para mercados de juro baixo.

**Bear 2015-16** (`analise_crises.csv`): o Sentinel rendeu +14,2% na janela com drawdown de −21,2%, contra −1,7% e −39,4% do IBOV. A proteção contra o momentum puro, porém, foi quase nula em drawdown (−21,2% vs −21,6%): a queda de 2015 foi gradual e o momentum puro se defendeu sozinho rotacionando de setor. Primeira saída do risco em dez/2014, primeira reentrada em abr/2015 (whipsaw); o custo agregado dos vai-e-véns aparece na análise de whipsaws abaixo.

**COVID 2020** (`analise_crises.csv`, F3): aqui a tese aparece com força. Saída do risco no rebalanceamento de fev/2020 (executada início de mar), fundo do IBOV em 23/03, reentrada em jul/2020. O filtro evitou **30,9 p.p. de drawdown** (−16,2% vs −47,1% do momentum puro), ao custo de perder ~62% de alta do IBOV entre o fundo e a reentrada. No ano fechado: Sentinel +17,7% vs +69,2% do momentum puro — o preço da proteção é assimétrico: protege muito na queda rápida, perde muito na recuperação em V.

## 3. Whipsaws (falsos sinais do filtro)

Do log de decisões (`analise_whipsaws.csv`): **36 trocas de regime** no período; **17 runs com permanência ≤ 2 rebalanceamentos** (whipsaws). Custo médio por whipsaw vs momentum puro: **−1,68%** por episódio. É o custo estrutural da SMA200 avaliada mensalmente: em mercado lateral o filtro liga e desliga tarde demais nos dois sentidos.

**Histerese ±2% (robustez):** reduz whipsaws de 17 para 11 e trocas de 36 para 34, mas **piora** o caso-base nesta amostra (CAGR 11,2% vs 11,9%; MaxDD −33,3% vs −27,9%) — a banda atrasa também as saídas verdadeiras. Fica registrada como próximo passo de investigação, não promovida a caso-base.

## 4. Fragilidades declaradas

1. **Viés de sobrevivência:** universo de 10 ações definido hoje olhando para trás; a direção do viés é conhecida — **infla o retorno do momentum** (vencedores de longo prazo permanecem na lista).
2. **Sensibilidade a parâmetros** (`sensibilidade.csv`, F5): momentum 6-1 derruba o CAGR para 6,0% (Sharpe negativo); SMA100 sobe para 16,0%. O resultado depende materialmente de escolhas que a literatura fixa mas a amostra não confirma de forma robusta.
3. **Atraso estrutural da SMA200:** quantificado no Bloco 2 — na COVID, 62% de recuperação do IBOV perdida entre fundo e reentrada.
4. **Universo pequeno → concentração:** top-3 de 10 ativos significa 33% por papel; risco idiossincrático alto.
5. **Custos fora do caso-base:** sensibilidade indica impacto de ~0,8 p.p. (0,10%) a ~1,5 p.p. (0,20%) de CAGR — não muda a conclusão qualitativa.
6. **Janela única, um só mercado:** sem out-of-sample formal; conclusões condicionais ao Brasil 2010–2026 e ao seu nível de juros.

## 5. Cenário desfavorável explícito

Mercados laterais com reversões frequentes são o pior caso: o filtro gera whipsaws em sequência (17 episódios a −1,68% cada, em média) e o momentum 12-1 perde validade sem tendência persistente. O período 2012–2015 no Brasil aproxima esse cenário — visível na F1 como o trecho em que o Sentinel anda de lado colado no CDI enquanto alterna regimes.

## 6. Veredito e próximos passos

**Veredito:** proporcional às evidências — o Sentinel cumpre o que a tese promete (menos drawdown, melhor Calmar, 56% de exposição a risco), mas não domina o momentum puro em retorno nem em Sharpe nesta amostra; com CDI alto, o custo de oportunidade da proteção é grande. A contribuição do trabalho é mostrar **quando** o filtro paga (crash rápido, COVID) e quando não (queda lenta 2015-16; recuperação em V).

**Próximos passos realistas (não implementados, por disciplina anti-overfitting):**
1. Validação out-of-sample de janelas de regime mais curtas (a superioridade da SMA100 nesta amostra é hipótese, não conclusão).
2. Filtro de volatilidade complementar à SMA (regime por vol realizada), possivelmente mais rápido em crashes.
3. Universo ampliado com tratamento explícito de sobrevivência (composição histórica do índice).
4. Custos de transação no caso-base.
