"""
Automacao de fechamento de arquivos de producao - arquivo unico.

Le arquivos da pasta raiz, interpreta o nome no padrao
    <quantidade>x_<produto>_<largura>x<altura>.<ext>   (medidas em cm)
abre no programa certo, valida a proporcao e gera o arquivo final em "Saida\\":

    PDF        -> Photoshop  -> TIF (DPI conforme tamanho)
    CDR/EPS/AI -> CorelDRAW  -> CDR (corte router / corte e contorno)

Se a dimensao real do arquivo nao bater com o nome, o arquivo de origem
e renomeado com o prefixo FORA_PROPORCAO_ e nada e exportado. O arquivo
NUNCA e redimensionado.

PARA ALTERAR QUALQUER REGRA, edite apenas o BLOCO DE CONFIGURACAO logo
abaixo. Nao precisa mexer no resto do arquivo.

Uso:
    python fechamento.py                            # pasta raiz padrao
    python fechamento.py "D:\\outra\\pasta"         # outra pasta
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

try:
    import win32com.client  # type: ignore
except ImportError:
    win32com = None  # checado no main()


# ############################################################################
# #                          BLOCO DE CONFIGURACAO                           #
# #                                                                          #
# #  Edite somente os valores apos o "=". Cada secao e independente.         #
# ############################################################################


# ---- 1) PASTAS -------------------------------------------------------------
# Pasta raiz onde os arquivos do cliente caem.
# Subpasta de saida e onde gravamos os TIF/CDR ja conferidos.
RAIZ_PADRAO    = r"C:\2026\Fechamento"
SUBPASTA_SAIDA = "Saida"


# ---- 2) NOMENCLATURA DOS ARQUIVOS ------------------------------------------
# Esperado:  <quantidade>x_<produto>_<largura>x<altura>.<ext>   em cm.
# Exemplos:  1x_vinil_fosco_100x100.pdf
#            5x_lona_banner_150x80.pdf
#            1x_adesivo_recorte_50x30.cdr
#
# Arquivos que ja receberam este prefixo sao ignorados em execucoes futuras
# (nao reprocessa) - mantenha conforme abaixo a menos que tenha um motivo.
PREFIXO_FORA_PROPORCAO = "FORA_PROPORCAO_"


# ---- 3) VALIDACAO DA PROPORCAO ---------------------------------------------
# Folga aceita ao comparar a dimensao do nome com a dimensao real do arquivo.
# 0.1 cm = 1 mm. Aumente se receber arquivos com pequenas variacoes de bleed.
TOLERANCIA_CM = 0.1


# ---- 4) ROTEAMENTO POR EXTENSAO --------------------------------------------
# Define qual programa abre cada tipo de arquivo.
# Para mudar a regra basta mover a extensao de um conjunto para o outro.
EXT_PHOTOSHOP = {".pdf"}
EXT_COREL     = {".cdr", ".eps", ".ai"}


# ---- 5) SAIDA PHOTOSHOP  ->  TIF para impressao ----------------------------
# Regra de DPI pelo LADO MAIOR do arquivo. Cada tupla e
# (lado_maior_ate_cm, dpi). A primeira regra cujo limite >= lado maior vence.
# Use None no limite para "sem teto". Pode incluir quantas faixas quiser
# (mantendo a ordem do menor para o maior).
DPI_POR_TAMANHO = [
    # (lado_maior_ate_cm, dpi)
    (60,   300),   # ate 60 cm    -> 300 dpi
    (None, 100),   # acima de 60  -> 100 dpi
]

# Modo de cor com que o PDF e aberto e o TIF e salvo.
# Aceita: "CMYK" (impressao) ou "RGB" (tela / web)
PHOTOSHOP_MODO_COR = "CMYK"

# Qual "caixa" do PDF define o tamanho da pagina. Em geral o cliente
# manda a medida final na MEDIABOX. Se vier com sangra/bleed e a validacao
# acusar fora, troque para "TRIMBOX".
# Aceita: "MEDIABOX", "BOUNDINGBOX", "CROPBOX", "BLEEDBOX", "TRIMBOX", "ARTBOX"
PHOTOSHOP_CROP_PDF = "MEDIABOX"

# Compressao do TIF final.
# Aceita: "NENHUMA", "LZW", "ZIP", "JPEG"
TIF_COMPRESSAO = "LZW"

# Embute o perfil de cor (ICC) no TIF salvo.
TIF_EMBUTIR_PERFIL = True


# ---- 6) SAIDA CORELDRAW  ->  CDR para corte --------------------------------
# Extensao do arquivo gerado pelo Corel na pasta Saida.
COREL_FORMATO_SAIDA = "cdr"


# ---- 7) AJUSTES INTERNOS (raramente precisam mudar) ------------------------
# Mostra a janela do Photoshop/Corel enquanto processa.
# True acompanha visualmente, False roda silencioso.
APLICATIVOS_VISIVEIS = True


# ############################################################################
# #                                                                          #
# #              LOGICA DE EXECUCAO  -  nao precisa editar abaixo             #
# #                                                                          #
# ############################################################################


# 1x_vinil_fosco_100x100  ->  qtd=1, produto="vinil_fosco", larg=100, alt=100
_PADRAO_NOME = re.compile(
    r"^(?P<qtd>\d+)x[_\-\s]+"
    r"(?P<produto>.+?)[_\-\s]+"
    r"(?P<larg>\d+(?:[.,]\d+)?)x(?P<alt>\d+(?:[.,]\d+)?)"
    r"$",
    re.IGNORECASE,
)


def dpi_para(larg_cm: float, alt_cm: float) -> int:
    """Retorna o DPI conforme a faixa em DPI_POR_TAMANHO."""
    lado = max(larg_cm, alt_cm)
    for limite, dpi in DPI_POR_TAMANHO:
        if limite is None or lado <= limite:
            return dpi
    return DPI_POR_TAMANHO[-1][1]


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
        if ext in EXT_PHOTOSHOP:
            return "photoshop"
        if ext in EXT_COREL:
            return "corel"
        return "ignorar"


def parse_nome(caminho: Path) -> InfoArquivo | None:
    m = _PADRAO_NOME.match(caminho.stem)
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
    return abs(esperado - real) <= TOLERANCIA_CM


def marcar_fora_proporcao(caminho: Path, larg_real: float, alt_real: float) -> Path:
    sufixo = f"{PREFIXO_FORA_PROPORCAO}real_{larg_real:.1f}x{alt_real:.1f}_"
    novo = caminho.with_name(sufixo + caminho.name)
    caminho.rename(novo)
    return novo


# ---------------------------------------------------------------- Photoshop

# Constantes JSX nativas do Photoshop (sem ginastica de COM enum).
_PS_MODE_JSX = {"CMYK": "OpenDocumentMode.CMYK", "RGB": "OpenDocumentMode.RGB"}
_PS_TIF_COMPRESSION_JSX = {
    "NENHUMA": "TIFFEncoding.NONE",
    "LZW":     "TIFFEncoding.TIFFLZW",
    "ZIP":     "TIFFEncoding.TIFFZIP",
    "JPEG":    "TIFFEncoding.JPEG",
}
_PS_CROP_JSX = {
    "BOUNDINGBOX": "CropToType.BOUNDINGBOX",
    "MEDIABOX":    "CropToType.MEDIABOX",
    "CROPBOX":     "CropToType.CROPBOX",
    "BLEEDBOX":    "CropToType.BLEEDBOX",
    "TRIMBOX":     "CropToType.TRIMBOX",
    "ARTBOX":      "CropToType.ARTBOX",
}


def _jsx_path(p: Path) -> str:
    # File() do JSX usa forward-slash no Windows tambem.
    return str(p).replace("\\", "/")


def processar_photoshop(info: InfoArquivo, pasta_saida: Path) -> str:
    ps = win32com.client.Dispatch("Photoshop.Application")
    ps.Visible = APLICATIVOS_VISIVEIS

    dpi = dpi_para(info.larg_cm, info.alt_cm)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    destino = pasta_saida / info.caminho.with_suffix(".tif").name

    modo_jsx = _PS_MODE_JSX[PHOTOSHOP_MODO_COR.upper()]
    comp_jsx = _PS_TIF_COMPRESSION_JSX[TIF_COMPRESSAO.upper()]
    crop_jsx = _PS_CROP_JSX[PHOTOSHOP_CROP_PDF.upper()]
    embed = "true" if TIF_EMBUTIR_PERFIL else "false"

    jsx = f"""
    var __resultado;
    try {{
      app.preferences.rulerUnits = Units.CM;
      app.preferences.typeUnits  = TypeUnits.CM;

      var f = new File("{_jsx_path(info.caminho)}");
      var opts = new PDFOpenOptions();
      opts.resolution = {dpi};
      opts.mode       = {modo_jsx};
      opts.antiAlias  = true;
      opts.cropPage   = {crop_jsx};
      opts.suppressWarnings = true;

      var doc = app.open(f, opts);
      var w = doc.width.as("cm");
      var h = doc.height.as("cm");
      var expW = {info.larg_cm}, expH = {info.alt_cm}, tol = {TOLERANCIA_CM};

      if (Math.abs(w - expW) > tol || Math.abs(h - expH) > tol) {{
        doc.close(SaveOptions.DONOTSAVECHANGES);
        __resultado = "FORA|" + w.toFixed(2) + "|" + h.toFixed(2);
      }} else {{
        var out = new File("{_jsx_path(destino)}");
        var tif = new TiffSaveOptions();
        tif.imageCompression  = {comp_jsx};
        tif.byteOrder         = ByteOrder.IBM;
        tif.layerCompression  = LayerCompression.RLE;
        tif.embedColorProfile = {embed};
        tif.transparency      = false;
        doc.saveAs(out, tif, true);
        __resultado = "OK|" + w.toFixed(2) + "|" + h.toFixed(2);
      }}
    }} catch (e) {{
      __resultado = "ERRO|" + e.toString();
    }}
    __resultado;
    """

    resultado = str(ps.DoJavaScript(jsx)).strip()
    status, _, resto = resultado.partition("|")

    if status == "OK":
        return f"[OK]   {info.caminho.name}: {dpi} dpi -> {destino}"
    if status == "FORA":
        larg_real, _, alt_real = resto.partition("|")
        larg_real, alt_real = float(larg_real), float(alt_real)
        novo = marcar_fora_proporcao(info.caminho, larg_real, alt_real)
        return (f"[FORA] {info.caminho.name}: nome={info.larg_cm}x{info.alt_cm}cm, "
                f"real={larg_real:.2f}x{alt_real:.2f}cm -> {novo.name}")
    return f"[ERRO] {info.caminho.name}: {resto or resultado}"


# ----------------------------------------------------------------- CorelDRAW

def processar_corel(info: InfoArquivo, pasta_saida: Path) -> str:
    corel = win32com.client.Dispatch("CorelDRAW.Application")
    corel.Visible = APLICATIVOS_VISIVEIS

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
    destino = pasta_saida / info.caminho.with_suffix("." + COREL_FORMATO_SAIDA).name
    doc.SaveAs(str(destino))  # SaveAs detecta o formato pela extensao
    return f"[OK]   {info.caminho.name}: exportado para {destino}"


# --------------------------------------------------------------------- loop

def listar_arquivos(raiz: Path) -> list[Path]:
    if not raiz.exists():
        return []
    exts = EXT_PHOTOSHOP | EXT_COREL
    return [p for p in raiz.iterdir()
            if p.is_file()
            and p.suffix.lower() in exts
            and not p.name.startswith(PREFIXO_FORA_PROPORCAO)]


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
