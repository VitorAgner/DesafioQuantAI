"""Monta o relatório final: 5 páginas 16:9 em PDF único.

Fonte do texto: reports/RELATORIO_TEXTO.md (parseado, para não haver duas versões).
Fonte das figuras: reports/figures/F*.png.
Saída: reports/Sentinel_Relatorio.pdf — metadados limpos (anonimato eliminatório).
"""
import re
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

FIG_DIR = ROOT / "reports" / "figures"
OUT_PDF = ROOT / "reports" / "Sentinel_Relatorio.pdf"

W, H = 16.0, 9.0                 # sistema de coordenadas 16:9
FIGSIZE = (13.333, 7.5)          # polegadas, 16:9

NAVY = "#1f3b73"
ALERT = "#c0392b"
GRAY = "#7f8c8d"
INK = "#1a1a1a"
CARD = "#eef1f6"
PAPER = "#ffffff"
ON_DARK = "#f2f5fa"
ON_DARK_SOFT = "#9db4d8"


# ------------------------------------------------------------------ utilidades
def parse_texto():
    """Lê RELATORIO_TEXTO.md e devolve [{titulo, blocos:[(header, corpo)]}]."""
    raw = (ROOT / "reports" / "RELATORIO_TEXTO.md").read_text(encoding="utf-8")
    paginas = []
    for chunk in re.split(r"^## ", raw, flags=re.M)[1:]:
        linhas = chunk.split("\n")
        titulo = linhas[0].split("—", 1)[-1].strip()
        blocos = []
        # cabeçalho obrigatoriamente em linha própria: [^*\n] impede que o DOTALL
        # do corpo engula o bloco seguinte (a linha "**Figuras:** ..." não casa)
        for m in re.finditer(r"^\*\*([^*\n]+)\*\*\n(.+?)(?=\n\s*\n|\Z)",
                             "\n".join(linhas[1:]), flags=re.M | re.S):
            head, body = m.group(1).strip(), m.group(2).strip()
            if head.startswith("Figuras"):
                continue
            body = re.sub(r"\*(.+?)\*", r"\1", body)      # sem itálico inline
            blocos.append((head, " ".join(body.split())))
        paginas.append({"titulo": titulo, "blocos": blocos})
    return paginas


def new_page(dark=False):
    fig = plt.figure(figsize=FIGSIZE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), W, H, facecolor=NAVY if dark else PAPER, zorder=-10))
    return fig, ax


def page_title(ax, texto, subtitulo=None, dark=False, y=8.6):
    ax.text(0.55, y, texto, fontsize=25, weight="bold",
            color=ON_DARK if dark else NAVY, va="top")
    if subtitulo:
        ax.text(0.55, y - 0.58, subtitulo, fontsize=12.5, style="italic",
                color=ON_DARK_SOFT if dark else GRAY, va="top")


def text_block(ax, x, y_top, w, header, body, *, dark=False, fs=10.5, hfs=11.5):
    """Desenha cabeçalho + corpo com quebra de linha manual. Devolve o y final."""
    ax.text(x, y_top, header.upper(), fontsize=hfs, weight="bold",
            color=ON_DARK_SOFT if dark else NAVY, va="top")
    y = y_top - 0.42
    chars = max(20, int(100 * w / fs))
    linhas = textwrap.wrap(body, width=chars)
    lh = fs * 0.0225
    for ln in linhas:
        ax.text(x, y, ln, fontsize=fs, color=ON_DARK if dark else INK, va="top")
        y -= lh
    return y - 0.18


def place_image(fig, nome, x, y_top, w):
    """Insere PNG mantendo o aspecto real do arquivo. Devolve o y inferior."""
    img = mpimg.imread(FIG_DIR / nome)
    h = w * img.shape[0] / img.shape[1]
    axi = fig.add_axes([x / W, (y_top - h) / H, w / W, h / H])
    axi.imshow(img)
    axi.axis("off")
    for s in axi.spines.values():
        s.set_visible(False)
    return y_top - h


def card(ax, x, y_top, w, h, *, fc=CARD, ec=NAVY, lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y_top - h), w, h,
                                boxstyle="round,pad=0.06,rounding_size=0.14",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=-5))


def page_number(ax, n, dark=False):
    ax.text(W - 0.55, 0.35, f"{n}/5", fontsize=10,
            color=ON_DARK_SOFT if dark else GRAY, ha="right", va="center")


QA_PNG = "--png" in sys.argv


def emit(pp, fig, n):
    """Salva a página no PDF e, em modo QA, também como PNG para inspeção visual."""
    pp.savefig(fig)
    if QA_PNG:
        qa = ROOT / "reports" / "qa"
        qa.mkdir(parents=True, exist_ok=True)
        fig.savefig(qa / f"pagina_{n}.png", dpi=110)
    plt.close(fig)


# -------------------------------------------------------------------- páginas
def pagina_1(pp, pg):
    fig, ax = new_page(dark=True)
    ax.text(0.55, 8.5, "SENTINEL", fontsize=44, weight="bold", color=ON_DARK, va="top")
    ax.text(0.55, 7.55,
            "A sentinela que vigia o regime do mercado antes de deixar a carteira avançar",
            fontsize=13.5, style="italic", color=ON_DARK_SOFT, va="top")

    # espaço reservado para o emblema do robô
    card(ax, 13.6, 8.45, 1.8, 1.8, fc="#16294f", ec=ON_DARK_SOFT, lw=1.2)
    ax.text(14.5, 7.55, "emblema\ndo robô", fontsize=10, color=ON_DARK_SOFT,
            ha="center", va="center", linespacing=1.5)

    y = 6.6
    for head, body in pg["blocos"]:
        y = text_block(ax, 0.55, y, 6.4, head, body, dark=True, fs=10)
        y -= 0.2

    place_image(fig, "F6_diagrama_camadas.png", 7.4, 6.35, 8.2)
    page_number(ax, 1, dark=True)
    emit(pp, fig, 1)


def pagina_2(pp, pg):
    fig, ax = new_page()
    page_title(ax, "Modelagem", "Duas camadas, um vetor de pesos auditável por mês")

    y = 7.15
    for head, body in pg["blocos"]:
        y = text_block(ax, 0.55, y, 4.75, head, body)
        y -= 0.25

    place_image(fig, "F7_fluxo_modelagem.png", 5.7, 7.2, 9.75)
    page_number(ax, 2)
    emit(pp, fig, 2)


def pagina_3(pp, pg):
    fig, ax = new_page()
    page_title(ax, "Backtest", "Janela longa, vieses declarados e ablação contra o momentum sem filtro")

    xs = [0.65, 5.85, 11.05]
    for (head, body), x in zip(pg["blocos"], xs):
        text_block(ax, x, 7.35, 4.6, head, body, fs=9.5)

    place_image(fig, "F1_curvas_patrimonio.png", 0.65, 4.4, 6.9)
    place_image(fig, "F5_sensibilidade.png", 8.45, 4.4, 6.9)
    page_number(ax, 3)
    emit(pp, fig, 3)


def tabela_metricas(ax, y_top):
    df = pd.read_csv(ROOT / "reports" / "tabela_metricas.csv").set_index("Estratégia")
    cols = ["CAGR", "Vol anual", "Sharpe", "Max DD", "Calmar", "% meses positivos",
            "Exposição a risco"]
    heads = ["CAGR", "Vol. anual", "Sharpe", "Máx. DD", "Calmar", "% meses +",
             "Exposição"]

    def fmt(c, v):
        if pd.isna(v):
            return "—"
        s = f"{v:.2f}" if c in ("Sharpe", "Calmar") else f"{v:.1%}"
        return s.replace(".", ",")

    x_lab, x0, cw = 0.75, 3.9, 1.63
    ax.text(x_lab, y_top, "Estratégia", fontsize=10, weight="bold", color=GRAY, va="center")
    for j, h in enumerate(heads):
        ax.text(x0 + j * cw, y_top, h, fontsize=10, weight="bold", color=GRAY,
                ha="center", va="center")

    for i, nome in enumerate(["Sentinel", "Momentum puro", "IBOV", "CDI"]):
        y = y_top - 0.55 - i * 0.45
        destaque = nome == "Sentinel"
        if destaque:
            card(ax, 0.55, y + 0.22, 14.9, 0.44, fc=CARD, ec=NAVY, lw=1.2)
        ax.text(x_lab, y, nome, fontsize=11, weight="bold" if destaque else "normal",
                color=NAVY if destaque else INK, va="center")
        for j, c in enumerate(cols):
            ax.text(x0 + j * cw, y, fmt(c, df.loc[nome, c]), fontsize=11,
                    weight="bold" if destaque else "normal",
                    color=NAVY if destaque else INK, ha="center", va="center")
    return y_top - 0.55 - 3 * 0.5 - 0.45


def pagina_4(pp, pg):
    fig, ax = new_page()
    page_title(ax, "Resultados", "Menos drawdown, menos retorno: o trade-off medido")

    tabela_metricas(ax, 7.3)
    ax.text(0.65, 5.02,
            "Sharpe = média aritmética do excesso diário sobre o CDI, anualizada por √252; "
            "não equivale a (CAGR − CDI)/volatilidade. CDI é a taxa livre de risco, portanto sem Sharpe.",
            fontsize=8.5, color=GRAY, va="top")

    xs = [0.65, 5.85, 11.05]
    for (head, body), x in zip(pg["blocos"], xs):
        text_block(ax, x, 4.72, 4.6, head, body, fs=9, hfs=10.5)

    place_image(fig, "F2W_drawdown_wide.png", 0.55, 2.85, 7.3)
    place_image(fig, "F3W_crises_wide.png", 8.15, 2.85, 7.3)
    page_number(ax, 4)
    emit(pp, fig, 4)


def pagina_5(pp, pg):
    fig, ax = new_page(dark=True)
    page_title(ax, "Conclusão e uso de IA", "Veredito proporcional às evidências", dark=True)

    xs = [0.65, 5.85, 11.05]
    for (head, body), x in zip(pg["blocos"], xs):
        text_block(ax, x, 7.35, 4.6, head, body, dark=True, fs=9.5)

    place_image(fig, "F9_uso_genai.png", 0.65, 4.4, 7.0)
    place_image(fig, "F4_decomposicao_regime.png", 8.45, 4.4, 6.9)
    page_number(ax, 5, dark=True)
    emit(pp, fig, 5)


def main():
    paginas = parse_texto()
    assert len(paginas) == 5, f"esperadas 5 páginas, encontradas {len(paginas)}"

    # metadados neutros — anonimato é critério eliminatório
    meta = {"Title": "Sentinel", "Author": "", "Subject": "", "Keywords": "",
            "Creator": "", "Producer": ""}
    with PdfPages(OUT_PDF, metadata=meta) as pp:
        pagina_1(pp, paginas[0])
        pagina_2(pp, paginas[1])
        pagina_3(pp, paginas[2])
        pagina_4(pp, paginas[3])
        pagina_5(pp, paginas[4])
    print(f"[pdf] {OUT_PDF.relative_to(ROOT)} — {len(paginas)} páginas")


if __name__ == "__main__":
    main()
