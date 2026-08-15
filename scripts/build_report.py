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


def draw_emblema(fig, x, y_top, size):
    """Emblema do robô: torre de vigia com varredura de radar.

    Redesenhado a partir do SVG de origem em primitivas do matplotlib (o Windows
    desta máquina não tem as bibliotecas do cairo para rasterizar SVG). Sai
    vetorial no PDF, então mantém nitidez em qualquer zoom.
    """
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, to_rgb
    from matplotlib.patches import Circle, FancyBboxPatch, Polygon

    axi = fig.add_axes([x / W, (y_top - size) / H, size / W, size / H])
    axi.set_xlim(0, 512)
    axi.set_ylim(512, 0)          # y cresce para baixo, como no SVG
    axi.set_aspect("equal")
    axi.axis("off")
    for s in axi.spines.values():
        s.set_visible(False)
    k = size * (13.333 / 16) * 72 / 512     # larguras de traço SVG → pontos

    def metal(y):
        t = min(max((y - 120) / 320.0, 0.0), 1.0)
        a, b = np.array(to_rgb("#dbe4f7")), np.array(to_rgb("#8ea3d4"))
        return tuple(a + (b - a) * t)

    # disco de fundo e anéis
    axi.add_patch(Circle((256, 256), 248, facecolor="#0e1c38", edgecolor="none"))
    axi.add_patch(Circle((256, 256), 248, facecolor="none", edgecolor="#1f3b73", lw=16 * k))

    # campo interno: gradiente radial deslocado, recortado pelo círculo
    cmap = LinearSegmentedColormap.from_list(
        "field", [(0.0, "#2b4d8f"), (0.55, "#1f3b73"), (1.0, "#0e1c38")])
    n = 320
    gx, gy = np.meshgrid(np.linspace(30, 482, n), np.linspace(30, 482, n))
    dist = np.hypot(gx - 219.8, gy - 165.6) / 384.2
    im = axi.imshow(np.clip(dist, 0, 1), cmap=cmap, vmin=0, vmax=1,
                    extent=[30, 482, 482, 30], origin="upper", zorder=1,
                    interpolation="bilinear")
    im.set_clip_path(Circle((256, 256), 226, transform=axi.transData))
    axi.add_patch(Circle((256, 256), 226, facecolor="none", edgecolor="#7f94c4",
                         lw=3 * k, alpha=0.55, zorder=2))
    axi.add_patch(Circle((256, 256), 206, facecolor="none", edgecolor="#7f94c4",
                         lw=2 * k, alpha=0.25, ls=(0, (0.4, 2.6)), zorder=2))

    # varredura do radar: três arcos concêntricos a partir do farol da torre
    for raio, swidth in ((54, 9), (80, 8), (106, 7)):
        ang = np.linspace(np.radians(-75), np.radians(-15), 60)
        px, py = 262 + raio * np.cos(ang), 148 + raio * np.sin(ang)
        # o gradiente original vai do canto inferior-esquerdo ao superior-direito
        proj = (np.cos(ang) - np.sin(ang)) / np.sqrt(2)
        alpha = 0.05 + 0.85 * np.clip((proj - 0.85) / 0.15, 0, 1)
        for i in range(len(ang) - 1):
            axi.plot(px[i:i + 2], py[i:i + 2], color="#ff4d4d",
                     alpha=float(alpha[i]), lw=swidth * k, solid_capstyle="round",
                     zorder=3)

    # antena parabólica e mastro
    ang = np.linspace(np.radians(146.25), np.radians(213.75), 40)
    axi.plot(269.93 + 36 * np.cos(ang), 148 + 36 * np.sin(ang), color=metal(148),
             lw=15 * k, solid_capstyle="round", zorder=4)
    axi.plot([248, 256], [154, 190], color=metal(172), lw=7 * k,
             solid_capstyle="round", zorder=4)

    # cabine e plataforma
    axi.add_patch(Polygon([(214, 190), (298, 190), (294, 240), (218, 240)],
                          closed=True, facecolor="#122548", edgecolor=metal(215),
                          lw=9 * k, joinstyle="round", zorder=5))
    axi.plot([218, 294], [214, 214], color=metal(214), lw=5 * k, alpha=0.5, zorder=6)
    axi.add_patch(Polygon([(200, 240), (312, 240), (306, 256), (206, 256)],
                          closed=True, facecolor="#16305e", edgecolor=metal(248),
                          lw=8 * k, joinstyle="round", zorder=5))

    # estrutura: pernas, travessas e contraventamentos
    estrutura = [
        ([206, 188], [256, 430], 11, 1.0), ([306, 324], [256, 430], 11, 1.0),
        ([222, 232], [256, 430], 6, 0.7), ([290, 280], [256, 430], 6, 0.7),
        ([204, 308], [300, 300], 6, 1.0), ([198, 314], [356, 356], 6, 1.0),
        ([205, 306], [268, 296], 4, 0.6), ([307, 204], [268, 296], 4, 0.6),
        ([202, 310], [312, 348], 4, 0.6), ([309, 199], [312, 348], 4, 0.6),
        ([197, 316], [368, 414], 4, 0.6), ([315, 189], [368, 414], 4, 0.6),
        ([170, 342], [430, 430], 12, 1.0),
    ]
    for xs, ys, swidth, alpha in estrutura:
        axi.plot(xs, ys, color=metal(sum(ys) / 2), lw=swidth * k, alpha=alpha,
                 solid_capstyle="round", zorder=5)

    # janela iluminada e luzes de base (tom de alerta)
    axi.add_patch(FancyBboxPatch((228, 202), 56, 18,
                                 boxstyle="round,pad=0,rounding_size=4",
                                 facecolor="#ff4d4d", alpha=0.18, edgecolor="none",
                                 zorder=6))
    axi.add_patch(FancyBboxPatch((233, 206), 46, 10,
                                 boxstyle="round,pad=0,rounding_size=3",
                                 facecolor="#ff5252", edgecolor="none", zorder=7))
    axi.add_patch(Circle((256, 452), 9, facecolor="#e03131", edgecolor="none", zorder=6))
    axi.add_patch(Circle((196, 444), 5, facecolor="#e03131", alpha=0.7,
                         edgecolor="none", zorder=6))
    axi.add_patch(Circle((316, 444), 5, facecolor="#e03131", alpha=0.7,
                         edgecolor="none", zorder=6))


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

    draw_emblema(fig, 13.45, 8.6, 2.0)

    y = 6.6
    for head, body in pg["blocos"]:
        y = text_block(ax, 0.55, y, 5.5, head, body, dark=True, fs=10)
        y -= 0.2

    place_image(fig, "F6_diagrama_camadas.png", 6.5, 6.5, 9.0)
    page_number(ax, 1, dark=True)
    emit(pp, fig, 1)


def pagina_2(pp, pg):
    fig, ax = new_page()
    page_title(ax, "Modelagem", "Duas camadas, um vetor de pesos auditável por mês")

    y = 7.15
    for head, body in pg["blocos"]:
        y = text_block(ax, 0.55, y, 4.3, head, body, fs=10)
        y -= 0.25

    place_image(fig, "F7_fluxo_modelagem.png", 5.2, 7.25, 10.3)
    page_number(ax, 2)
    emit(pp, fig, 2)


def tabela_sensibilidade(ax, x0, y_top, w):
    """Robustez desenhada nativamente na página: fontes em tamanho real."""
    df = pd.read_csv(ROOT / "reports" / "sensibilidade.csv").set_index("Cenário")
    linhas = [("Caso-base (SMA200 · 12-1)", "SMA200 (base)"),
              ("Janela do regime: SMA 100", "SMA100"),
              ("Janela do regime: SMA 150", "SMA150"),
              ("Momentum 6-1", "Mom 6-1"),
              ("Momentum 9-1", "Mom 9-1"),
              ("Custo 0,10% por perna", "Custo 0,10%"),
              ("Custo 0,20% por perna", "Custo 0,20%")]
    cols = ["CAGR", "Sharpe", "MaxDD", "Calmar"]

    def fmt(c, v):
        s = f"{v:.2f}" if c in ("Sharpe", "Calmar") else f"{v:.1%}"
        return s.replace(".", ",")

    cw = (w - 2.9) / 4
    xv = x0 + 2.9
    ax.text(x0, y_top, "Cenário", fontsize=8.5, weight="bold", color=GRAY, va="center")
    for j, c in enumerate(cols):
        ax.text(xv + j * cw + cw / 2, y_top, c, fontsize=8.5, weight="bold",
                color=GRAY, ha="center", va="center")
    for i, (rotulo, chave) in enumerate(linhas):
        y = y_top - 0.45 - i * 0.4
        base = i == 0
        if base:
            card(ax, x0 - 0.15, y + 0.2, w + 0.3, 0.4, fc=CARD, ec=NAVY, lw=1.0)
        ax.text(x0, y, rotulo, fontsize=9, weight="bold" if base else "normal",
                color=NAVY if base else INK, va="center")
        for j, c in enumerate(cols):
            ax.text(xv + j * cw + cw / 2, y, fmt(c, df.loc[chave, c]), fontsize=9,
                    weight="bold" if base else "normal",
                    color=NAVY if base else INK, ha="center", va="center")


def pagina_3(pp, pg):
    fig, ax = new_page()
    page_title(ax, "Backtest", "Janela longa, vieses declarados e ablação contra o momentum sem filtro")

    xs = [0.65, 5.85, 11.05]
    for (head, body), x in zip(pg["blocos"], xs):
        text_block(ax, x, 7.35, 4.6, head, body, fs=9)

    ax.text(0.65, 4.98, "Curvas de patrimônio 2010–2026 (base 1,0; escala log; faixas = BEAR)",
            fontsize=9, weight="bold", color=NAVY, va="center")
    place_image(fig, "P3_curvas.png", 0.65, 4.78, 6.9)

    ax.text(8.4, 4.98, "Robustez: sensibilidade a parâmetros e custos",
            fontsize=9, weight="bold", color=NAVY, va="center")
    tabela_sensibilidade(ax, 8.4, 4.55, 6.95)
    ax.text(8.4, 1.35,
            "A variação entre parâmetros é a medida honesta da fragilidade da estratégia. "
            "O ganho da SMA100 nesta amostra é hipótese para validação out-of-sample,\nnão "
            "fundamento para trocar o caso-base a posteriori.",
            fontsize=8, color=GRAY, va="top", linespacing=1.5)
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
    ax.text(0.65, 5.18,
            "Sharpe = média aritmética do excesso diário sobre o CDI, anualizada por √252; "
            "não equivale a (CAGR − CDI)/volatilidade. CDI é a taxa livre de risco, portanto sem Sharpe.",
            fontsize=8.5, color=GRAY, va="top")

    xs = [0.65, 5.85, 11.05]
    for (head, body), x in zip(pg["blocos"], xs):
        text_block(ax, x, 4.85, 4.6, head, body, fs=9, hfs=10.5)

    ax.text(0.65, 3.1, "Drawdown: Sentinel × momentum puro",
            fontsize=9, weight="bold", color=NAVY, va="center")
    ax.text(8.25, 3.1, "Crises: curvas normalizadas em 100 (faixas = BEAR)",
            fontsize=9, weight="bold", color=NAVY, va="center")
    place_image(fig, "P4_drawdown.png", 0.65, 2.9, 7.3)
    place_image(fig, "P4_crises.png", 8.25, 2.9, 7.3)
    page_number(ax, 4)
    emit(pp, fig, 4)


def pagina_5(pp, pg):
    fig, ax = new_page(dark=True)
    page_title(ax, "Conclusão e uso de IA", "Veredito proporcional às evidências", dark=True)

    xs = [0.65, 5.85, 11.05]
    for (head, body), x in zip(pg["blocos"], xs):
        text_block(ax, x, 7.35, 4.6, head, body, dark=True, fs=9.5)

    place_image(fig, "F9W_uso_genai_wide.png", 1.0, 4.6, 14.0)
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
