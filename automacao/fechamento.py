"""
Automacao de fechamento de arquivos de producao - arquivo unico.

Le arquivos da pasta raiz, interpreta o nome no padrao
    <quantidade>x_<produto>_<largura>x<altura>.<ext>   (medidas em cm)
abre no programa certo, valida a proporcao e gera o arquivo final em "Saida\\":

    PDF        -> Photoshop  -> TIF (DPI conforme tamanho)
    CDR/EPS/AI -> CorelDRAW  -> CDR (corte router / corte e contorno)

Comportamento do Photoshop quanto a proporcao:
  - Se a Art Box (ou caixa configurada) tem a MESMA proporcao do nome
    do arquivo, a imagem e renderizada exatamente em <largura>x<altura> cm
    no DPI alvo. Salva como  base.tif .
  - Se NAO tem a mesma proporcao, salva no tamanho natural e adiciona a
    medida real entre parenteses no nome:
        1X VINIL FOSCO 60X75 (29.69x37.09).tif
    Arquivos JAMAIS sao distorcidos.

PARA ALTERAR QUALQUER REGRA, edite apenas o BLOCO DE CONFIGURACAO logo
abaixo. Nao precisa mexer no resto do arquivo.

Uso:
    python fechamento.py                            # pasta raiz padrao
    python fechamento.py "D:\\outra\\pasta"         # outra pasta
    python fechamento.py --arquivo "C:\\...\\1x_vinil_fosco_100x100.pdf"

Requer Windows com Photoshop e/ou CorelDRAW instalados, mais:
    pip install pywin32 pypdf

(pywin32 = controle do Photoshop/Corel via COM;
 pypdf  = leitura da Art Box do PDF sem precisar abri-lo no Photoshop,
         para que o Photoshop abra direto na resolucao final.)
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

try:
    from pypdf import PdfReader  # type: ignore
except ImportError:
    PdfReader = None  # checado em processar_photoshop()


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

# Qual "caixa" do PDF define o tamanho da pagina. O cliente normalmente
# exporta a arte na Art Box, entao esse e o padrao. Troque se a sua
# pre-impressao definir a medida final em outra caixa do PDF.
# Aceita: "ARTBOX", "MEDIABOX", "BOUNDINGBOX", "CROPBOX", "BLEEDBOX", "TRIMBOX"
PHOTOSHOP_CROP_PDF = "ARTBOX"

# Folga aceita na conferencia da PROPORCAO (relacao largura/altura).
# 0.005 = 0.5%. Aumente se o PDF do cliente vier com sangra leve que
# distorce a proporcao.
TOL_PROPORCAO = 0.005

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


# Exemplos validos (e como o script interpreta):
#   1x_vinil_fosco_100x100.pdf
#       -> qtd=1, produto="vinil fosco", 100x100
#   1X ADESIVO FOSCO 145X87 - COLLER NETSHOES.pdf
#       -> qtd=1, produto="ADESIVO FOSCO", 145x87  (resto: cliente)
#   1X_LONA_-_MV_-_120X310.pdf
#       -> qtd=1, produto="LONA MV", 120x310
#   1X LONA FOSCA 120X320 _-_MV_-_120X310 - (EXEMPLO).pdf
#       -> qtd=1, produto="LONA FOSCA", 120x320   (pega o PRIMEIRO L x A;
#                                                  120x310 e a referencia
#                                                  interna do cliente)
#   1X VINIL FOSCO 145X87 1X ADESIVO FOSCO 145X87 - COLLER NETSHOES.pdf
#       -> qtd=1, produto="VINIL FOSCO", 145x87   (pega o PRIMEIRO; o
#                                                  segundo item precisa
#                                                  ser um arquivo separado)
#
# Aceita como separadores: "_", "-" e espaco (em qualquer combinacao).
# Medidas SEMPRE em centimetros.
_PADRAO_NOME = re.compile(
    r"^"
    r"(?P<qtd>\d+)x[_\-\s]+"
    r"(?P<produto>.+?)"
    r"[_\-\s]+"
    r"(?P<larg>\d+(?:[.,]\d+)?)x(?P<alt>\d+(?:[.,]\d+)?)"
    r"(?![0-9])",          # garante que largura/altura nao sao prefixo
    re.IGNORECASE,         #   de outro numero maior
)


def _limpar_produto(s: str) -> str:
    # transforma separadores soltos ("_-_", "_-", " - ", etc.) em espaco
    s = re.sub(r"[_\-\s]+", " ", s).strip()
    # tira pedacos vazios entre separadores (ex.: "LONA - - MV" -> "LONA MV")
    return re.sub(r"\s+", " ", s)


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
        produto=_limpar_produto(m.group("produto")),
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


# Mapa de qual atributo do pypdf corresponde a cada caixa do PDF.
_PYPDF_BOX_ATTR = {
    "ARTBOX":      "artbox",
    "MEDIABOX":    "mediabox",
    "CROPBOX":     "cropbox",
    "BLEEDBOX":    "bleedbox",
    "TRIMBOX":     "trimbox",
    "BOUNDINGBOX": "mediabox",  # pypdf nao tem boundingbox: cai pra mediabox
}


def _medir_caixa_pdf(pdf_path: Path, caixa: str) -> tuple[float, float] | None:
    """Le a largura/altura (em cm) da caixa pedida na primeira pagina do PDF.

    Retorna None se pypdf nao estiver instalado, o PDF nao puder ser lido
    ou a caixa nao existir.
    """
    if PdfReader is None:
        return None
    attr = _PYPDF_BOX_ATTR.get(caixa.upper(), "mediabox")
    try:
        reader = PdfReader(str(pdf_path))
        page = reader.pages[0]
        box = getattr(page, attr, None) or page.mediabox
        # PDF unit = ponto = 1/72 polegada; 1 polegada = 2,54 cm.
        w_cm = float(box.width)  / 72.0 * 2.54
        h_cm = float(box.height) / 72.0 * 2.54
        return (w_cm, h_cm)
    except Exception:
        return None


def processar_photoshop(info: InfoArquivo, pasta_saida: Path) -> str:
    """
    Passada UNICA no Photoshop. A caixa do PDF e lida antes via pypdf
    (sem abrir o arquivo no Photoshop), o que permite calcular o DPI de
    abertura de forma que o documento aberto ja tenha o tamanho final
    correto - nao ha render em resolucao menor seguido de ampliacao.

    Se a proporcao da caixa bate com o nome:
        DPI de abertura = DPI_alvo * largura_nome / largura_da_caixa
        -> apos abrir, relabela a metadata para nameW x nameH @ DPI_alvo
           sem reamostrar (mesmos pixels).
    Se NAO bate:
        DPI de abertura = DPI_alvo
        -> abre no tamanho natural e salva com a medida real entre
           parenteses no nome do TIF. Arquivo jamais e distorcido.
    """
    import json

    if PdfReader is None:
        return (f"[ERRO] {info.caminho.name}: pypdf nao instalado. "
                "Rode: pip install pypdf")

    medida = _medir_caixa_pdf(info.caminho, PHOTOSHOP_CROP_PDF)
    if medida is None:
        return (f"[ERRO] {info.caminho.name}: nao consegui ler a "
                f"{PHOTOSHOP_CROP_PDF} do PDF.")
    nat_w, nat_h = medida

    name_ratio = info.larg_cm / info.alt_cm
    nat_ratio  = nat_w / nat_h
    proporcional = abs(nat_ratio - name_ratio) / name_ratio < TOL_PROPORCAO

    target_dpi = dpi_para(info.larg_cm, info.alt_cm)
    open_dpi = (target_dpi * info.larg_cm / nat_w) if proporcional else target_dpi

    pasta_saida.mkdir(parents=True, exist_ok=True)
    if proporcional:
        nome_arq = info.caminho.with_suffix(".tif").name
    else:
        nome_arq = f"{info.caminho.stem} ({nat_w:.2f}x{nat_h:.2f}).tif"
    destino = pasta_saida / nome_arq

    ps = win32com.client.Dispatch("Photoshop.Application")
    ps.Visible = APLICATIVOS_VISIVEIS

    modo_jsx = _PS_MODE_JSX[PHOTOSHOP_MODO_COR.upper()]
    comp_jsx = _PS_TIF_COMPRESSION_JSX[TIF_COMPRESSAO.upper()]
    crop_jsx = _PS_CROP_JSX[PHOTOSHOP_CROP_PDF.upper()]
    embed    = "true" if TIF_EMBUTIR_PERFIL else "false"

    input_lit   = json.dumps(_jsx_path(info.caminho))
    destino_lit = json.dumps(_jsx_path(destino))
    relabel = "true" if proporcional else "false"

    jsx = f"""
    var __resultado, __step = "inicio";
    try {{
      __step = "prefs.rulerUnits";
      app.preferences.rulerUnits = Units.CM;

      __step = "open.opts";
      var opts = new PDFOpenOptions();
      opts.resolution = {open_dpi};
      opts.mode       = {modo_jsx};
      opts.antiAlias  = true;
      opts.cropPage   = {crop_jsx};

      __step = "app.open";
      var doc = app.open(new File({input_lit}), opts);

      if ({relabel}) {{
        __step = "relabel";
        // mesma quantidade de pixels, ajusta apenas cm/dpi na metadata
        doc.resizeImage(undefined, undefined, {target_dpi}, ResampleMethod.NONE);
      }}

      __step = "saveAs";
      var tif = new TiffSaveOptions();
      tif.imageCompression  = {comp_jsx};
      tif.byteOrder         = ByteOrder.IBM;
      tif.embedColorProfile = {embed};
      tif.transparency      = false;
      doc.saveAs(new File({destino_lit}), tif, true);

      __resultado = "OK";
    }} catch (e) {{
      __resultado = "ERRO|step=" + __step + "|" + e.toString();
    }}
    __resultado;
    """

    resultado = str(ps.DoJavaScript(jsx)).strip()
    if resultado == "OK":
        if proporcional:
            return (f"[OK]   {info.caminho.name}: ArtBox {nat_w:.2f}x{nat_h:.2f}cm "
                    f"-> {info.larg_cm}x{info.alt_cm}cm @ {target_dpi} dpi "
                    f"(abriu @ {open_dpi:.0f} dpi, sem reamostragem) -> {destino.name}")
        return (f"[OK*]  {info.caminho.name}: proporcao nao bate "
                f"(natural {nat_w:.2f}x{nat_h:.2f}cm) @ {target_dpi} dpi "
                f"-> {destino.name}")
    return f"[ERRO] {info.caminho.name}: {resultado}"


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
