"""
Automacao de fechamento de arquivos de producao.

Le arquivos da pasta raiz (C:\\2026\\Fechamento por padrao), interpreta o nome
no padrao  <qtd>x_<produto>_<largura>x<altura>.<ext>  (medidas em cm), abre no
Photoshop (PDF) ou CorelDRAW (CDR/EPS/AI), valida se a proporcao do arquivo
bate com o nome e, se bater, exporta um PDF final para a subpasta "Saida".

Se a dimensao real NAO bater com o nome o arquivo de origem e renomeado com o
prefixo  FORA_PROPORCAO_  e nada e exportado. O arquivo nunca e redimensionado.

Uso:
    python fechamento.py                    # processa C:\\2026\\Fechamento
    python fechamento.py "C:\\outra\\pasta" # processa outra pasta
    python fechamento.py --arquivo "C:\\...\\1x_vinil_fosco_100x100.pdf"

Requer Windows com Photoshop e/ou CorelDRAW instalados e o pacote pywin32:
    pip install pywin32
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import win32com.client  # type: ignore
except ImportError:
    win32com = None  # checado no main()

RAIZ_PADRAO = r"C:\2026\Fechamento"
SUBPASTA_SAIDA = "Saida"
PREFIXO_FORA = "FORA_PROPORCAO_"
TOLERANCIA_CM = 0.1  # 1 mm de folga na conferencia de proporcao
DPI_PDF = 300

EXT_PHOTOSHOP = {".pdf"}
EXT_COREL = {".cdr", ".eps", ".ai"}

# 1x_vinil_fosco_100x100.pdf  -> qtd=1, produto="vinil_fosco", larg=100, alt=100
PADRAO_NOME = re.compile(
    r"^(?P<qtd>\d+)x[_\-\s]+"
    r"(?P<produto>.+?)[_\-\s]+"
    r"(?P<larg>\d+(?:[.,]\d+)?)x(?P<alt>\d+(?:[.,]\d+)?)"
    r"$",
    re.IGNORECASE,
)


@dataclass
class InfoArquivo:
    caminho: Path
    qtd: int
    produto: str
    larg_cm: float
    alt_cm: float

    @property
    def destino(self) -> str:
        if self.caminho.suffix.lower() in EXT_PHOTOSHOP:
            return "photoshop"
        if self.caminho.suffix.lower() in EXT_COREL:
            return "corel"
        return "ignorar"


def parse_nome(caminho: Path) -> InfoArquivo | None:
    nome = caminho.stem
    m = PADRAO_NOME.match(nome)
    if not m:
        return None
    larg = float(m.group("larg").replace(",", "."))
    alt = float(m.group("alt").replace(",", "."))
    return InfoArquivo(
        caminho=caminho,
        qtd=int(m.group("qtd")),
        produto=m.group("produto").strip("_- "),
        larg_cm=larg,
        alt_cm=alt,
    )


def marcar_fora_proporcao(caminho: Path, larg_real: float, alt_real: float) -> Path:
    sufixo = f"{PREFIXO_FORA}real_{larg_real:.1f}x{alt_real:.1f}_"
    novo = caminho.with_name(sufixo + caminho.name)
    caminho.rename(novo)
    return novo


def dentro_da_tolerancia(esperado: float, real: float) -> bool:
    return abs(esperado - real) <= TOLERANCIA_CM


# ---------------------------------------------------------------- Photoshop

def processar_photoshop(info: InfoArquivo, pasta_saida: Path) -> str:
    ps = win32com.client.Dispatch("Photoshop.Application")
    ps.Visible = True
    # cm como unidade de regua
    ps.Preferences.RulerUnits = 3  # psCm
    ps.Preferences.TypeUnits = 3

    opcoes = win32com.client.Dispatch("Photoshop.PDFOpenOptions")
    opcoes.Resolution = DPI_PDF
    opcoes.Mode = 3  # psOpenCMYK; mude para 2 (RGB) se preferir
    opcoes.AntiAlias = True
    opcoes.CropPage = 1  # psBoundingBox

    doc = ps.Open(str(info.caminho), opcoes)

    larg_real = float(doc.Width)
    alt_real = float(doc.Height)

    ok = (
        dentro_da_tolerancia(info.larg_cm, larg_real)
        and dentro_da_tolerancia(info.alt_cm, alt_real)
    )

    if not ok:
        doc.Close(2)  # psDoNotSaveChanges
        novo = marcar_fora_proporcao(info.caminho, larg_real, alt_real)
        return (
            f"[FORA] {info.caminho.name}: nome={info.larg_cm}x{info.alt_cm}cm, "
            f"real={larg_real:.2f}x{alt_real:.2f}cm. Renomeado para {novo.name}"
        )

    pasta_saida.mkdir(parents=True, exist_ok=True)
    destino_pdf = pasta_saida / info.caminho.with_suffix(".pdf").name

    pdf_opts = win32com.client.Dispatch("Photoshop.PDFSaveOptions")
    pdf_opts.EmbedColorProfile = True
    pdf_opts.PDFStandard = 0
    pdf_opts.PreserveEditing = False
    doc.SaveAs(str(destino_pdf), pdf_opts, True)

    return f"[OK]   {info.caminho.name}: exportado para {destino_pdf}"


# ----------------------------------------------------------------- CorelDRAW

def processar_corel(info: InfoArquivo, pasta_saida: Path) -> str:
    corel = win32com.client.Dispatch("CorelDRAW.Application")
    corel.Visible = True

    doc = corel.OpenDocument(str(info.caminho))
    # Corel usa "unidades" que dependem do doc; forcamos para cm.
    cdrCentimeter = 5
    pagina = doc.ActivePage
    larg_real = float(corel.ConvertUnits(pagina.SizeWidth, doc.Unit, cdrCentimeter))
    alt_real = float(corel.ConvertUnits(pagina.SizeHeight, doc.Unit, cdrCentimeter))

    ok = (
        dentro_da_tolerancia(info.larg_cm, larg_real)
        and dentro_da_tolerancia(info.alt_cm, alt_real)
    )

    if not ok:
        doc.Close()
        novo = marcar_fora_proporcao(info.caminho, larg_real, alt_real)
        return (
            f"[FORA] {info.caminho.name}: nome={info.larg_cm}x{info.alt_cm}cm, "
            f"real={larg_real:.2f}x{alt_real:.2f}cm. Renomeado para {novo.name}"
        )

    pasta_saida.mkdir(parents=True, exist_ok=True)
    destino_pdf = pasta_saida / info.caminho.with_suffix(".pdf").name
    doc.PublishToPDF(str(destino_pdf))

    return f"[OK]   {info.caminho.name}: exportado para {destino_pdf}"


# --------------------------------------------------------------------- loop

def listar_arquivos(raiz: Path) -> list[Path]:
    if not raiz.exists():
        return []
    exts = EXT_PHOTOSHOP | EXT_COREL
    return [
        p for p in raiz.iterdir()
        if p.is_file() and p.suffix.lower() in exts
        and not p.name.startswith(PREFIXO_FORA)
    ]


def processar(arquivos: list[Path], pasta_saida: Path) -> None:
    for caminho in arquivos:
        info = parse_nome(caminho)
        if info is None:
            print(f"[SKIP] {caminho.name}: nome fora do padrao "
                  f"<qtd>x_<produto>_<LxA>")
            continue
        try:
            if info.destino == "photoshop":
                print(processar_photoshop(info, pasta_saida))
            elif info.destino == "corel":
                print(processar_corel(info, pasta_saida))
            else:
                print(f"[SKIP] {caminho.name}: extensao nao suportada")
        except Exception as exc:  # noqa: BLE001
            print(f"[ERRO] {caminho.name}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raiz", nargs="?", default=RAIZ_PADRAO,
                        help=f"Pasta raiz (padrao: {RAIZ_PADRAO})")
    parser.add_argument("--arquivo", help="Processa um unico arquivo")
    args = parser.parse_args()

    if win32com is None:
        print("ERRO: pywin32 nao instalado. Rode: pip install pywin32")
        return 1

    if args.arquivo:
        caminho = Path(args.arquivo)
        raiz = caminho.parent
        arquivos = [caminho]
    else:
        raiz = Path(args.raiz)
        arquivos = listar_arquivos(raiz)
        if not arquivos:
            print(f"Nenhum arquivo encontrado em {raiz}")
            return 0

    pasta_saida = raiz / SUBPASTA_SAIDA
    processar(arquivos, pasta_saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
