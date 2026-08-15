# Texto-fonte do relatório final (5 páginas · 16:9)

> Orçamento: ~750 palavras no total. Cada página indica as figuras que a acompanham.
> Documento 100% anônimo: sem nomes, instituição, links de repositório ou caminhos de máquina.

---

## PÁGINA 1 — SENTINEL: A TESE
**Figuras:** emblema do robô · F6 (diagrama das duas camadas)

**A tese**
Acredito que o momentum funciona melhor em mercados de alta porque, em regimes de baixa, as correlações sobem, as tendências se revertem abruptamente e os vencedores recentes tornam-se os mais castigados. Portanto, testo uma carteira de momentum que só assume risco quando um filtro de regime indica mercado saudável, recuando para o CDI caso contrário.

**Por que deveria funcionar**
O prêmio de momentum é atribuído à sub-reação do mercado à informação nova, ao efeito manada e à persistência de fluxos (Jegadeesh & Titman, 1993). Em regimes de estresse essa dinâmica se inverte, produzindo as reversões severas conhecidas como *momentum crashes* (Daniel & Moskowitz, 2016). O filtro de regime não pretende acertar topos e fundos: é gestão de risco condicional, na tradição de Faber (2007).

**O robô**
Sentinel é a sentinela que vigia o regime do mercado antes de deixar a carteira avançar. O nome descreve o mecanismo — primeiro a guarda verifica o terreno, só então o capital avança.

---

## PÁGINA 2 — MODELAGEM
**Figuras:** F7 (fluxo, parâmetros e exemplo real de decisão)

**Duas camadas**
A Camada 1 classifica o regime: BULL se o Ibovespa fecha acima da sua média móvel de 200 dias, BEAR caso contrário. A Camada 2 só é acionada em BULL — ordena as dez ações pelo retorno de doze meses excluindo o último, pois o *skip* evita a reversão de curto prazo, e compra as três melhores com pesos iguais. Em BEAR o vetor de pesos é 100% CDI.

**Parâmetros**
SMA de 200 dias, momentum 12-1 e top-3 vêm da literatura, não de busca exaustiva nesta amostra. A escolha custa desempenho, mas protege contra overfitting; a sensibilidade é reportada como robustez, nunca como otimização retroativa.

**Saída observável**
A cada mês o modelo emite um vetor de pesos auditável. O sinal usa dados até o fechamento do último pregão e a execução ocorre no primeiro pregão do mês seguinte. As 188 decisões do período estão registradas integralmente.

---

## PÁGINA 3 — BACKTEST
**Figuras:** F1 (curvas de patrimônio com faixas de regime)

**Dados e período**
Janeiro de 2010 a junho de 2026, com preços ajustados por proventos e desdobramentos e CDI diário oficial. A janela cobre o bear de 2011-2016, o choque de 2017, a COVID e dois ciclos de juros — variedade suficiente para que o resultado não dependa de um único ambiente.

**Controle de vieses**
*Look-ahead:* sinal em t, execução em t+1, verificado por testes que alteram dados futuros e exigem sinal idêntico. *Sobrevivência:* o universo foi definido olhando para trás e o viés infla o momentum — declarado, não corrigido. *Aquecimento:* os primeiros catorze meses permanecem em CDI por falta de histórico para o sinal. *Cherry-picking:* janela longa e leitura por subperíodo.

**Ablação**
Quatro curvas comparadas: Sentinel, momentum sem filtro, Ibovespa e CDI. A segunda isola exatamente o que a camada de vigia adiciona — ou destrói.

---

## PÁGINA 4 — RESULTADOS
**Figuras:** F8 (tabela de métricas) · F2 (drawdown) · F3 (zoom nas crises)

**O que o filtro entregou**
O drawdown máximo cai de 47,1% para 27,9% e o Calmar sobe de 0,39 para 0,43, com apenas 56% do tempo exposto a risco. O custo é explícito: CAGR de 11,9% contra 18,3% do momentum sem filtro.

**Onde protegeu e onde não**
Na COVID o filtro saiu do risco no rebalanceamento de fevereiro e evitou 30,9 pontos percentuais de drawdown, ao preço de perder a maior parte da recuperação até reentrar em agosto. Em 2015-16 a proteção foi quase nula: a queda foi lenta e o momentum se defendeu sozinho, rotacionando setores.

**Fragilidades**
Houve 36 trocas de regime, 17 delas falsos sinais, a um custo médio de 1,7% cada. O resultado é sensível à janela — momentum de seis meses derruba o CAGR para 6,0%. Universo pequeno, ausência de custos no caso-base e um único mercado completam a lista.

---

## PÁGINA 5 — CONCLUSÃO E USO DE IA
**Figuras:** F9 (fluxograma de uso de IA) · F4 ou F5 (decomposição ou sensibilidade)

**Veredito**
A tese confirma-se parcialmente. O Sentinel cumpre o que promete em risco, mas não domina o momentum puro em retorno nesta amostra. Um terço do ganho acumulado veio do CDI durante os regimes de baixa — dependente do juro brasileiro e não transportável a mercados de juro baixo. A contribuição do trabalho é delimitar quando o filtro paga: crashes rápidos, não quedas lentas.

**Próximos passos**
Validar out-of-sample janelas de regime mais curtas; testar um filtro de volatilidade complementar; ampliar o universo com composição histórica do índice; incorporar custos ao caso-base.

**IA generativa**
Usada em cinco etapas, da ideação à comunicação. O uso mais produtivo foi adversarial: pedir à IA que atacasse a própria estratégia originou os testes de look-ahead. O mais instrutivo foi um erro — código gerado devolvia a série de regime com tipo incorreto e o gráfico marcava todo o período como BEAR; o backtest estava certo, apenas a figura mentia. Desde então nenhuma saída da IA vira resultado sem teste ou inspeção.
