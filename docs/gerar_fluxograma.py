"""Gera o fluxograma do pipeline DevOps implementado no projeto.

Uso:
    python docs/gerar_fluxograma.py

O diagrama é desenhado por código para que possa ser versionado junto com o
restante do projeto e regerado sempre que o pipeline mudar.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "fluxograma-devops.png"

CORES = {
    "dev": "#3D5A80",
    "ci": "#2A9D8F",
    "gate": "#E9C46A",
    "cd": "#E76F51",
    "obs": "#6D597A",
    "falha": "#B23A48",
    "linha": "#2B2B2B",
}

LARGURA = 3.0
ALTURA = 0.92


def caixa(eixo, x, y, texto, cor, largura=LARGURA, altura=ALTURA, cor_texto="white"):
    """Desenha uma caixa arredondada centrada em (x, y) com o texto informado."""
    eixo.add_patch(
        FancyBboxPatch(
            (x - largura / 2, y - altura / 2),
            largura,
            altura,
            boxstyle="round,pad=0.05,rounding_size=0.16",
            linewidth=1.1,
            edgecolor="#1D1D1D",
            facecolor=cor,
            zorder=3,
        )
    )
    eixo.text(
        x,
        y,
        texto,
        ha="center",
        va="center",
        fontsize=8.6,
        color=cor_texto,
        linespacing=1.35,
        zorder=4,
    )


def caminho(eixo, pontos, cor=CORES["linha"], estilo="-", rotulo=None, rotulo_em=None):
    """Liga uma sequência de pontos com segmentos retos e ponta de seta no fim."""
    for inicio, fim in zip(pontos[:-2], pontos[1:-1], strict=False):
        eixo.add_line(
            Line2D(
                [inicio[0], fim[0]],
                [inicio[1], fim[1]],
                color=cor,
                linewidth=1.3,
                linestyle=estilo,
                solid_capstyle="round",
                zorder=2,
            )
        )
    eixo.add_patch(
        FancyArrowPatch(
            pontos[-2],
            pontos[-1],
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.3,
            color=cor,
            linestyle=estilo,
            shrinkA=0,
            shrinkB=0,
            zorder=2,
        )
    )
    if rotulo is not None:
        posicao = rotulo_em or (
            (pontos[0][0] + pontos[1][0]) / 2,
            (pontos[0][1] + pontos[1][1]) / 2,
        )
        eixo.text(
            posicao[0],
            posicao[1],
            rotulo,
            ha="center",
            va="center",
            fontsize=7.6,
            color=cor,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5},
            zorder=5,
        )


def barramento(eixo, x_inicial, x_final, y, cor=CORES["linha"], estilo="-"):
    """Desenha a linha horizontal que distribui ou recolhe várias conexões."""
    eixo.add_line(
        Line2D(
            [x_inicial, x_final],
            [y, y],
            color=cor,
            linewidth=1.3,
            linestyle=estilo,
            solid_capstyle="round",
            zorder=2,
        )
    )


def faixa(eixo, y_inferior, altura, titulo, cor):
    """Desenha a faixa horizontal que identifica cada etapa do fluxo."""
    eixo.add_patch(
        FancyBboxPatch(
            (1.05, y_inferior),
            17.5,
            altura,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=0,
            facecolor=cor,
            alpha=0.10,
            zorder=1,
        )
    )
    eixo.text(
        1.35,
        y_inferior + altura - 0.3,
        titulo,
        ha="left",
        va="center",
        fontsize=9.4,
        color=cor,
        fontweight="bold",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 2.0},
        zorder=4,
    )


def etapa_desenvolvimento(eixo):
    """Desenha a faixa de desenvolvimento e as conexões internas."""
    y = 10.95
    faixa(eixo, 10.5, 1.45, "1. Desenvolvimento", CORES["dev"])
    caixa(eixo, 3.2, y, "Desenvolvedor\nbranch feature/*", CORES["dev"])
    caixa(eixo, 7.4, y, "git push\npara o GitHub", CORES["dev"])
    caixa(eixo, 11.6, y, "Pull request\naberto para a main", CORES["dev"])
    caixa(eixo, 15.8, y, "GitHub Actions\ndispara o pipeline de CI", CORES["dev"])
    for origem, destino in ((4.7, 5.9), (8.9, 10.1), (13.1, 14.3)):
        caminho(eixo, [(origem, y), (destino, y)])


def etapa_integracao(eixo, colunas):
    """Desenha a faixa de integração contínua e o barramento de distribuição."""
    y = 9.05
    faixa(eixo, 8.2, 1.95, "2. Integração Contínua (Fase 1) — .github/workflows/ci.yml", CORES["ci"])
    rotulos = (
        "Análise estática\nruff check\nruff format",
        "Testes\npytest 3.11 e 3.12\ncobertura ≥ 90%",
        "Segurança\nbandit\npip-audit",
        "Infraestrutura\nterraform validate\nansible-lint",
        "Imagem\nbuild + healthcheck\nteste de fumaça",
    )
    for x, rotulo in zip(colunas, rotulos, strict=True):
        caixa(eixo, x, y, rotulo, CORES["ci"], altura=1.18)

    caminho(eixo, [(15.8, 10.49), (15.8, 10.25)])
    barramento(eixo, colunas[0], colunas[-1], 10.25)
    for x in colunas:
        caminho(eixo, [(x, 10.25), (x, 9.64)])
    eixo.text(
        8.0,
        10.25,
        "as cinco verificações são executadas em paralelo",
        ha="center",
        va="center",
        fontsize=7.6,
        color="#4A4A4A",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.8},
        zorder=5,
    )


def etapa_portao(eixo, colunas):
    """Desenha o portão de integração, o barramento de retorno e o caminho de falha."""
    y = 7.05
    faixa(eixo, 6.4, 1.45, "3. Portão de integração", CORES["gate"])
    caixa(eixo, 6.2, y, "Todas as verificações\nforam aprovadas?", CORES["gate"], largura=3.3, cor_texto="#1D1D1D")
    caixa(eixo, 10.6, y, "Merge na main\ncódigo integrado", CORES["gate"], cor_texto="#1D1D1D")
    caixa(eixo, 15.8, y, "Correção na\nbranch de origem", CORES["falha"], largura=2.8)

    for x in colunas:
        caminho(eixo, [(x, 8.46), (x, 8.0)])
    barramento(eixo, colunas[0], colunas[-1], 8.0)
    caminho(eixo, [(6.2, 8.0), (6.2, 7.51)])

    caminho(eixo, [(7.85, y), (9.1, y)], rotulo="sim", rotulo_em=(8.5, 7.28))
    caminho(
        eixo,
        [(6.2, 6.59), (6.2, 6.34), (15.8, 6.34), (15.8, 6.59)],
        cor=CORES["falha"],
        estilo=(0, (5, 3)),
        rotulo="não",
        rotulo_em=(6.2, 6.47),
    )
    caminho(
        eixo,
        [(17.2, y), (18.75, y), (18.75, 12.1), (3.2, 12.1), (3.2, 11.41)],
        cor=CORES["falha"],
        estilo=(0, (5, 3)),
        rotulo="nova iteração após a correção",
        rotulo_em=(11.0, 12.1),
    )


def etapa_entrega(eixo):
    """Desenha a faixa de entrega contínua, o rollback e a entrada vinda do merge."""
    y = 5.0
    faixa(eixo, 3.5, 2.55, "4. Entrega Contínua (Fase 2) — .github/workflows/cd.yml", CORES["cd"])
    colunas = (2.9, 6.35, 9.8, 13.25, 16.7)
    rotulos = (
        "CI verde na main\naciona a esteira de CD",
        "Publicar imagem\nGHCR: latest, versão\ne versão-commit",
        "Analisar imagem\nTrivy CRITICAL e HIGH",
        "Implantar\nscripts/deploy.sh\ndocker compose",
        "Teste de fumaça\nscripts/smoke-test.sh",
    )
    for x, rotulo in zip(colunas, rotulos, strict=True):
        caixa(eixo, x, y, rotulo, CORES["cd"], largura=3.1, altura=1.18)
    for origem, destino in zip(colunas[:-1], colunas[1:], strict=True):
        caminho(eixo, [(origem + 1.6, y), (destino - 1.6, y)])

    caminho(
        eixo,
        [(10.6, 6.59), (10.6, 6.06), (2.9, 6.06), (2.9, 5.64)],
        rotulo="somente com a CI aprovada",
        rotulo_em=(8.2, 6.06),
    )

    caixa(eixo, 6.35, 4.0, "Rollback automático\npara a versão anterior", CORES["falha"], largura=3.4, altura=0.72)
    caminho(
        eixo,
        [(16.7, 4.41), (16.7, 4.0), (8.1, 4.0)],
        cor=CORES["falha"],
        estilo=(0, (5, 3)),
        rotulo="falhou",
        rotulo_em=(12.6, 4.0),
    )
    return colunas


def etapa_operacao(eixo):
    """Desenha a faixa de operação e o retorno do monitoramento."""
    y = 2.1
    faixa(eixo, 1.25, 1.9, "5. Operação, monitoramento e retorno", CORES["obs"])
    caixa(eixo, 3.4, y, "Aplicação em execução\ncontainer sem privilégios", CORES["obs"], largura=3.6)
    caixa(eixo, 7.8, y, "Métricas\nPrometheus /metrics", CORES["obs"])
    caixa(eixo, 12.0, y, "Painéis e alertas\nGrafana e alerts.yml", CORES["obs"], largura=3.2)
    caixa(eixo, 16.2, y, "Logs em JSON\npor requisição", CORES["obs"])
    for origem, destino in ((5.25, 6.25), (9.35, 10.35), (13.65, 14.65)):
        caminho(eixo, [(origem, y), (destino, y)])

    caminho(
        eixo,
        [(17.55, 4.41), (17.55, 3.3), (3.4, 3.3), (3.4, 2.6)],
        rotulo="aprovado",
        rotulo_em=(10.5, 3.3),
    )
    caminho(
        eixo,
        [(16.2, 1.64), (16.2, 0.75), (0.6, 0.75), (0.6, 10.95), (1.65, 10.95)],
        cor=CORES["obs"],
        estilo=(0, (6, 4)),
        rotulo="retorno do monitoramento para o desenvolvimento",
        rotulo_em=(8.4, 0.75),
    )


def main() -> None:
    """Monta a figura completa e grava o arquivo PNG."""
    figura, eixo = plt.subplots(figsize=(16.4, 11.2))
    eixo.set_xlim(0, 19.4)
    eixo.set_ylim(0.2, 13.1)
    eixo.axis("off")
    figura.patch.set_facecolor("white")

    eixo.text(
        9.7,
        12.82,
        "Fluxo DevOps implementado — Inventário de Rede",
        ha="center",
        fontsize=15.5,
        fontweight="bold",
        color="#1D1D1D",
    )
    eixo.text(
        9.7,
        12.48,
        "Da alteração de código à aplicação em execução, com portões de qualidade, "
        "segurança e retorno de monitoramento",
        ha="center",
        fontsize=9.6,
        color="#4A4A4A",
    )

    colunas_ci = (2.9, 6.3, 9.7, 13.1, 16.5)
    etapa_desenvolvimento(eixo)
    etapa_integracao(eixo, colunas_ci)
    etapa_portao(eixo, colunas_ci)
    etapa_entrega(eixo)
    etapa_operacao(eixo)

    figura.savefig(SAIDA, dpi=170, bbox_inches="tight", facecolor="white")
    print(f"Fluxograma gerado em {SAIDA}")


if __name__ == "__main__":
    main()
