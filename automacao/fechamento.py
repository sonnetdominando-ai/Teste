"""
Automacao de fechamento de arquivos de producao.

Roteia arquivos pelo programa correto, confere a proporcao e gera o
arquivo final na pasta de saida:

    PDF          -> Photoshop -> TIF (DPI conforme tamanho)
    CDR/EPS/AI   -> CorelDRAW -> CDR (corte router / corte e contorno)

TODAS as regras (pasta, tolerancia, DPI, modo de cor, compressao, etc.)
ficam em  config.py . Este arquivo so contem a logica de execucao.

Uso:
    python fechamento.py                        # processa pasta raiz
    python fechamento.py "D:\\outra\\pasta"     # processa outra pasta
    python fechamento.py --arquivo "C:\\...\\1x_vinil_fosco_100x100.pdf"

Requer Windows com Photoshop e/ou CorelDRAW instalados e pywin32:
    pip install pywin32
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import config as cfg

try:
    import win32com.client  # type: ignore
except ImportError:
    win32com = None  # checado no main()


# 1x_vinil_fosco_100x100  ->  qtd=1, produto="vinil_fosco", larg=100, alt=100
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
        ext = self.caminho.suffix.lower()
        if ext in cfg.EXT_PHOTOSHOP:
            return "photoshop"
        if ext in cfg.EXT_COREL:
            return "corel"
        return "ignorar"


def parse_nome(caminho: Path) -> InfoArquivo | None:
    m = PADRAO_NOME.match(caminho.stem)
    if not m:
        return None
    return InfoArquivo(
        caminho=caminho,
        qtd=int(m.group("qtd")),
        produto=m.group("produto").strip("_- "),
        larg_cm=float(m.group("larg").replace(",", ".")),
        alt_cm=float(m.group("alt").replace(",", ".")),
    )


def dentro_da_tolerancia(esperado: float, real: float) -> bool:
    return abs(esperado - real) <= cfg.TOLERANCIA_CM


def marcar_fora_proporcao(caminho: Path, larg_real: float, alt_real: float) -> Path:
    sufixo = f"{cfg.PREFIXO_FORA_PROPORCAO}real_{larg_real:.1f}x{alt_real:.1f}_"
    novo = caminho.with_name(sufixo + caminho.name)
    caminho.rename(novo)
    return novo


# ---------------------------------------------------------------- Photoshop

def processar_photoshop(info: InfoArquivo, pasta_saida: Path) -> str:
    ps = win32com.client.Dispatch("Photoshop.Application")
    ps.Visible = cfg.APLICATIVOS_VISIVEIS
    ps.Preferences.RulerUnits = 3  # psCm
    ps.Preferences.TypeUnits = 3

    dpi = cfg.dpi_para(info.larg_cm, info.alt_cm)

    opcoes = win32com.client.Dispatch("Photoshop.PDFOpenOptions")
    opcoes.Resolution = dpi
    opcoes.Mode = cfg.ps_modo_cor_codigo()
    opcoes.AntiAlias = True
    opcoes.CropPage = 1  # psBoundingBox

    doc = ps.Open(str(info.caminho), opcoes)
    larg_real, alt_real = float(doc.Width), float(doc.Height)

    if not (dentro_da_tolerancia(info.larg_cm, larg_real)
            and dentro_da_tolerancia(info.alt_cm, alt_real)):
        doc.Close(2)  # psDoNotSaveChanges
        novo = marcar_fora_proporcao(info.caminho, larg_real, alt_real)
        return (f"[FORA] {info.caminho.name}: nome={info.larg_cm}x{info.alt_cm}cm, "
                f"real={larg_real:.2f}x{alt_real:.2f}cm -> {novo.name}")

    pasta_saida.mkdir(parents=True, exist_ok=True)
    destino = pasta_saida / info.caminho.with_suffix(".tif").name

    tif = win32com.client.Dispatch("Photoshop.TiffSaveOptions")
    tif.ImageCompression = cfg.ps_compressao_tif_codigo()
    tif.ByteOrder = 2  # psIBMByteOrder
    tif.LayerCompression = 2
    tif.EmbedColorProfile = cfg.TIF_EMBUTIR_PERFIL
    tif.Transparency = False
    doc.SaveAs(str(destino), tif, True)

    return f"[OK]   {info.caminho.name}: {dpi} dpi -> {destino}"


# ----------------------------------------------------------------- CorelDRAW

def processar_corel(info: InfoArquivo, pasta_saida: Path) -> str:
    corel = win32com.client.Dispatch("CorelDRAW.Application")
    corel.Visible = cfg.APLICATIVOS_VISIVEIS

    doc = corel.OpenDocument(str(info.caminho))
    cdrCentimeter = 5
    pagina = doc.ActivePage
    larg_real = float(corel.ConvertUnits(pagina.SizeWidth, doc.Unit, cdrCentimeter))
    alt_real = float(corel.ConvertUnits(pagina.SizeHeight, doc.Unit, cdrCentimeter))

    if not (dentro_da_tolerancia(info.larg_cm, larg_real)
            and dentro_da_tolerancia(info.alt_cm, alt_real)):
        doc.Close()
        novo = marcar_fora_proporcao(info.caminho, larg_real, alt_real)
        return (f"[FORA] {info.caminho.name}: nome={info.larg_cm}x{info.alt_cm}cm, "
                f"real={larg_real:.2f}x{alt_real:.2f}cm -> {novo.name}")

    pasta_saida.mkdir(parents=True, exist_ok=True)
    destino = pasta_saida / info.caminho.with_suffix("." + cfg.COREL_FORMATO_SAIDA).name
    doc.SaveAs(str(destino))  # SaveAs detecta o formato pela extensao
    return f"[OK]   {info.caminho.name}: exportado para {destino}"


# --------------------------------------------------------------------- loop

def listar_arquivos(raiz: Path) -> list[Path]:
    if not raiz.exists():
        return []
    exts = cfg.EXT_PHOTOSHOP | cfg.EXT_COREL
    return [p for p in raiz.iterdir()
            if p.is_file()
            and p.suffix.lower() in exts
            and not p.name.startswith(cfg.PREFIXO_FORA_PROPORCAO)]


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
    parser.add_argument("raiz", nargs="?", default=cfg.RAIZ_PADRAO,
                        help=f"Pasta raiz (padrao: {cfg.RAIZ_PADRAO})")
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

    pasta_saida = raiz / cfg.SUBPASTA_SAIDA
    processar(arquivos, pasta_saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
