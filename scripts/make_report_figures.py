"""Figuras conceituais do relatório final (F6–F9).

Complementam F1–F5 (geradas por run_analysis.py). Todas 16:9, paleta sóbria,
sem qualquer informação identificadora (nomes, usuário, caminhos de máquina).
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

FIG_DIR = ROOT / "reports" / "figures"
FIGSIZE, DPI = (16, 9), 150

C_SENT = "#1f3b73"    # azul-escuro Sentinel
C_ALERT = "#c0392b"   # tom de alerta (BEAR)
C_GRAY = "#7f8c8d"
C_FILL = "#eef1f6"
C_FILL_ALERT = "#fbeeec"
C_INK = "#1a1a1a"


def canvas():
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, *, fc=C_FILL, ec=C_SENT, fs=15, weight="normal",
        tc=C_INK, lw=2.0, align="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.18",
                                facecolor=fc, edgecolor=ec, linewidth=lw))
    ha = {"center": "center", "left": "left"}[align]
    tx = x + w / 2 if align == "center" else x + 0.25
    ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=fs,
            color=tc, weight=weight, linespacing=1.5)


def arrow(ax, x1, y1, x2, y2, color=C_SENT, label=None, lw=2.2, lfs=14):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, linewidth=lw,
                                shrinkA=0, shrinkB=0))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.28, label, ha="center", va="bottom",
                fontsize=lfs, color=color, weight="bold")


def save(fig, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / name, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[fig] {name}")


# --------------------------------------------------------------- F6: 2 camadas
def fig_camadas():
    fig, ax = canvas()
    ax.text(8, 8.5, "Sentinel — duas camadas de decisão", ha="center", fontsize=24,
            weight="bold", color=C_SENT)
    ax.text(8, 7.95, "A sentinela verifica o regime antes de deixar a carteira avançar",
            ha="center", fontsize=15, color=C_GRAY, style="italic")

    box(ax, 0.3, 4.15, 2.4, 1.6,
        "ENTRADA\n\nIBOV (índice)\n10 ações da B3", fs=13.5, ec=C_GRAY)

    box(ax, 3.25, 3.55, 4.15, 2.8,
        "CAMADA 1 — VIGIA\n\nO IBOV está acima\nda SMA de 200 dias?",
        fs=14, weight="bold", ec=C_SENT)

    box(ax, 9.0, 5.5, 4.3, 2.1,
        "CAMADA 2 — MOMENTUM\n\nRanking por retorno de 12 meses\nexcluindo o último (12-1)",
        fs=13.5, ec=C_SENT)

    box(ax, 9.0, 1.1, 4.3, 2.1,
        "RECUO PARA CAIXA\n\nRisco desligado:\no regime invalida o sinal",
        fs=13.5, ec=C_ALERT, fc=C_FILL_ALERT)

    box(ax, 13.85, 5.5, 1.95, 2.1, "Compra os 3\nprimeiros\n\n⅓ · ⅓ · ⅓",
        fs=13.5, weight="bold", ec=C_SENT)
    box(ax, 13.85, 1.1, 1.95, 2.1, "100% CDI", fs=16, weight="bold",
        ec=C_ALERT, fc=C_FILL_ALERT, tc=C_ALERT)

    arrow(ax, 2.8, 4.95, 3.2, 4.95, color=C_GRAY)
    arrow(ax, 7.5, 5.5, 8.95, 6.35, label="SIM\nBULL", lfs=13.5)
    arrow(ax, 7.5, 4.4, 8.95, 2.45, color=C_ALERT, label="NÃO\nBEAR", lfs=13.5)
    arrow(ax, 13.4, 6.55, 13.8, 6.55)
    arrow(ax, 13.4, 2.15, 13.8, 2.15, color=C_ALERT)

    ax.text(8, 0.35,
            "Avaliação mensal, no último pregão do mês · execução no primeiro pregão do mês seguinte",
            ha="center", fontsize=14, color=C_GRAY)
    save(fig, "F6_diagrama_camadas.png")


# ------------------------------------------------------- F7: fluxo de modelagem
def fig_fluxo():
    fig, ax = canvas()
    ax.text(8, 8.55, "Da série de preços ao vetor de pesos", ha="center", fontsize=23,
            weight="bold", color=C_SENT)

    etapas = [
        "DADOS\n\nPreços ajustados\n(dividendos e\ndesdobramentos)\nCDI diário oficial",
        "SINAL EM t\n\nÚltimo pregão\ndo mês\nSomente dados\naté t",
        "REGIME\n\nIBOV vs SMA200\n\nBULL ou BEAR",
        "RANKING\n\nMomentum 12-1\nTop 3 do universo\nPesos iguais",
        "EXECUÇÃO EM t+1\n\nPrimeiro pregão\ndo mês seguinte\n\nSem look-ahead",
    ]
    w, gap = 2.75, 0.42
    x0 = 0.35
    for i, txt in enumerate(etapas):
        x = x0 + i * (w + gap)
        ec = C_SENT if i in (2, 3) else C_GRAY
        box(ax, x, 5.5, w, 2.5, txt, fs=12.5, ec=ec)
        if i < 4:
            arrow(ax, x + w + 0.04, 6.75, x + w + gap - 0.04, 6.75, color=C_GRAY, lw=2)

    # parâmetros
    box(ax, 0.35, 0.5, 6.9, 4.4, "", fc="white", ec=C_GRAY, lw=1.5)
    ax.text(3.8, 4.4, "PARÂMETROS DO CASO-BASE", ha="center", fontsize=14.5,
            weight="bold", color=C_SENT)
    params = [
        ("Universo", "10 ações líquidas da B3"),
        ("Janela do regime", "SMA de 200 dias"),
        ("Sinal de momentum", "12 meses, sem o último"),
        ("Ativos comprados", "3, com pesos iguais"),
        ("Rebalanceamento", "Mensal"),
        ("Custos", "0% base; 0,10% e 0,20% testados"),
    ]
    for i, (k, v) in enumerate(params):
        y = 3.75 - i * 0.56
        ax.text(0.7, y, k, fontsize=12.5, color=C_SENT, weight="bold", va="center")
        ax.text(3.35, y, v, fontsize=12.5, color=C_INK, va="center")

    # exemplo real de decisão
    box(ax, 7.75, 0.5, 7.9, 4.4, "", fc=C_FILL, ec=C_SENT, lw=1.5)
    ax.text(11.7, 4.4, "EXEMPLO REAL DE DECISÃO — COVID/2020", ha="center", fontsize=14.5,
            weight="bold", color=C_SENT)
    linhas = [
        ("31/01/2020", "BULL", "Compra WEGE3, RENT3 e B3SA3", C_SENT),
        ("28/02/2020", "BEAR", "Zera ações e migra 100% para CDI", C_ALERT),
        ("31/07/2020", "BULL", "Volta ao risco: WEGE3, B3SA3, SUZB3", C_SENT),
    ]
    for i, (data, reg, acao, cor) in enumerate(linhas):
        y = 3.7 - i * 0.8
        ax.text(8.1, y, data, fontsize=12.5, weight="bold", color=C_INK, va="center")
        ax.text(9.95, y, reg, fontsize=12.5, weight="bold", color=cor, va="center")
        ax.text(10.9, y, acao, fontsize=12, color=C_INK, va="center")

    ax.text(11.7, 1.05,
            "A saída de fevereiro foi executada no primeiro pregão de março,\n"
            "antes do fundo do mercado em 23/03 — sem uso de informação futura.",
            ha="center", fontsize=12, color=C_GRAY, style="italic", linespacing=1.5)
    save(fig, "F7_fluxo_modelagem.png")


# --------------------------------------------------------- F8: tabela métricas
def fig_tabela():
    df = pd.read_csv(ROOT / "reports" / "tabela_metricas.csv").set_index("Estratégia")
    fig, ax = canvas()
    ax.text(8, 8.4, "Resultados 2010–2026 · caso-base sem custos", ha="center",
            fontsize=23, weight="bold", color=C_SENT)

    cols = ["CAGR", "Vol anual", "Sharpe", "Max DD", "Calmar", "% meses positivos",
            "Exposição a risco"]
    heads = ["CAGR", "Vol.\nanual", "Sharpe", "Máx.\ndrawdown", "Calmar",
             "% meses\npositivos", "Exposição\na risco"]

    def fmt(col, v):
        if pd.isna(v):
            return "—"
        s = f"{v:.2f}" if col in ("Sharpe", "Calmar") else f"{v:.1%}"
        return s.replace(".", ",")  # separador decimal pt-BR

    x_lab, x0, cw = 0.4, 3.6, 1.70
    ax.text(x_lab + 0.1, 7.1, "Estratégia", fontsize=14, weight="bold", color=C_GRAY)
    for j, h in enumerate(heads):
        ax.text(x0 + j * cw + cw / 2, 7.1, h, ha="center", va="center", fontsize=13.5,
                weight="bold", color=C_GRAY, linespacing=1.4)

    for i, name in enumerate(["Sentinel", "Momentum puro", "IBOV", "CDI"]):
        y = 6.0 - i * 1.15
        destaque = name == "Sentinel"
        if destaque:
            ax.add_patch(FancyBboxPatch((x_lab, y - 0.45), 15.2, 0.92,
                                        boxstyle="round,pad=0.02,rounding_size=0.1",
                                        facecolor=C_FILL, edgecolor=C_SENT, linewidth=2))
        ax.text(x_lab + 0.25, y, name, fontsize=15,
                weight="bold" if destaque else "normal",
                color=C_SENT if destaque else C_INK, va="center")
        for j, c in enumerate(cols):
            ax.text(x0 + j * cw + cw / 2, y, fmt(c, df.loc[name, c]), ha="center",
                    va="center", fontsize=14.5, weight="bold" if destaque else "normal",
                    color=C_SENT if destaque else C_INK)

    ax.text(0.4, 1.15,
            "O filtro de regime corta o drawdown de 47,1% para 27,9% e eleva o Calmar de 0,39 para 0,43,\n"
            "ao custo de retorno: o momentum sem filtro entrega CAGR e Sharpe maiores nesta amostra.",
            fontsize=14.5, color=C_INK, linespacing=1.6)
    ax.text(0.4, 0.3,
            "Sharpe = média aritmética do excesso diário sobre o CDI, anualizada por √252; não equivale a (CAGR − CDI)/volatilidade.\n"
            "CDI é a taxa livre de risco da estratégia, portanto não se reporta Sharpe para ele.",
            fontsize=11.5, color=C_GRAY, linespacing=1.5)
    save(fig, "F8_tabela_resultados.png")


# ------------------------------------------------------------------- F9: GenAI
def fig_genai():
    fig, ax = canvas()
    ax.text(8, 8.55, "Uso de IA generativa: etapa → aplicação → impacto", ha="center",
            fontsize=23, weight="bold", color=C_SENT)

    linhas = [
        ("Ideação", "Refinar a hipótese e listar vieses da tese",
         "Tese no formato testável e checklist anti-viés"),
        ("Código", "Gerar e revisar os módulos do backtest",
         "Esqueleto ponta a ponta funcional em um dia"),
        ("Validação", "Pedir à IA que atacasse a própria estratégia",
         "Auditoria do Sharpe e testes de look-ahead"),
        ("Interpretação", "Discutir crises, whipsaws e limitações",
         "Análise crítica em vez de métricas descritivas"),
        ("Comunicação", "Estruturar o relatório e a identidade visual",
         "Narrativa e figuras coerentes com a estratégia"),
    ]
    ax.text(1.5, 7.5, "ETAPA", ha="center", fontsize=14, weight="bold", color=C_GRAY)
    ax.text(6.2, 7.5, "COMO A IA FOI USADA", ha="center", fontsize=14, weight="bold", color=C_GRAY)
    ax.text(12.2, 7.5, "IMPACTO PRÁTICO", ha="center", fontsize=14, weight="bold", color=C_GRAY)

    for i, (etapa, uso, impacto) in enumerate(linhas):
        y = 6.55 - i * 0.92
        box(ax, 0.4, y - 0.34, 2.2, 0.68, etapa, fs=13.5, weight="bold", ec=C_SENT)
        box(ax, 3.15, y - 0.34, 6.1, 0.68, uso, fs=12.5, ec=C_GRAY, fc="white")
        box(ax, 9.75, y - 0.34, 5.85, 0.68, impacto, fs=12.5, ec=C_GRAY, fc="white")
        arrow(ax, 2.68, y, 3.1, y, color=C_GRAY, lw=1.6)
        arrow(ax, 9.3, y, 9.7, y, color=C_GRAY, lw=1.6)

    box(ax, 0.4, 0.35, 15.2, 1.5, "", fc=C_FILL_ALERT, ec=C_ALERT, lw=2)
    ax.text(0.85, 1.5, "LIMITAÇÃO ENCONTRADA", fontsize=14, weight="bold", color=C_ALERT)
    ax.text(0.85, 0.9,
            "Um trecho gerado pela IA devolvia a série de regime com tipo genérico: a negação lógica virava aritmética e o gráfico\n"
            "marcava todo o período como BEAR. O backtest estava correto, apenas a figura mentia — o erro só apareceu na conferência\n"
            "visual. Desde então, toda saída da IA passa por teste ou inspeção antes de virar resultado.",
            fontsize=12.5, color=C_INK, va="center", linespacing=1.6)
    save(fig, "F9_uso_genai.png")


if __name__ == "__main__":
    fig_camadas()
    fig_fluxo()
    fig_tabela()
    fig_genai()
