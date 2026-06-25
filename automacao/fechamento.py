"""
Automacao de fechamento de arquivos de producao - arquivo unico.
VERSAO V16 - Photoshop abre uma vez so + Corel salva CDR vetorial.

Mudancas principais da V16 em relacao a V15:
    1) Para PDF no Photoshop o tamanho da pagina e lido por fora com pypdf.
       O Photoshop abre UMA UNICA VEZ no DPI calculado, ja na medida pedida
       no nome do arquivo - sem render em 72 dpi e depois ampliar.
       Se pypdf nao estiver instalado, cai para o fluxo antigo de duas
       passadas, com aviso.
    2) Para corte/router/laser a saida e CDR vetorial (nao PDF).
       O SaveAs do Corel e chamado com varias estrategias de fallback
       (versao explicita, sem versao, filtro CDR) para sobreviver entre
       versoes do Corel.
    3) O PDF temporario publicado pelo Corel para virar TIF tambem e
       medido por fora antes do Photoshop abrir.

Regras principais (iguais as da V15):
    Arquivos de impressao:
        PDF/PSD/PSB/JPG/JPEG/PNG/TIF/TIFF/BMP -> Photoshop -> TIF LZW
        CDR/EPS/AI/SVG/DXF                    -> CorelDRAW -> PDF temp -> Photoshop -> TIF LZW

    Arquivos com CORTE E CONTORNO / ROUTER / LASER no nome:
        CDR/EPS/AI/SVG/DXF/PDF -> CorelDRAW -> CDR vetorial na pasta Saida
        NUNCA vira TIF: corte/router/laser precisa preservar vetor.

Nomenclatura esperada no nome do arquivo:
    <quantidade>x_<produto>_<largura>x<altura>.<ext>      (medidas em cm)

Uso:
    python fechamento.py
    python fechamento.py "C:\\2026\\Fechamento"
    python fechamento.py --arquivo "C:\\2026\\Fechamento\\1x_vinil_100x100.pdf"
    python fechamento.py "C:\\2026\\Fechamento" --dry-run

Requer Windows com Photoshop e CorelDRAW + dois pacotes Python:
    pip install pywin32 pypdf
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    import win32com.client  # type: ignore
except ImportError:
    win32com = None  # checado no main()

try:
    from pypdf import PdfReader  # type: ignore
except ImportError:
    PdfReader = None  # opcional; se faltar, o script cai num fluxo de fallback


# ############################################################################
# #                          BLOCO DE CONFIGURACAO                           #
# #                                                                          #
# #  Edite somente os valores apos o "=". Cada secao e independente.         #
# ############################################################################


# ---- 1) PASTAS -------------------------------------------------------------
RAIZ_PADRAO = r"C:\2026\Fechamento"
SUBPASTA_SAIDA = "Saida"


# ---- 2) NOMENCLATURA / IGNORADOS ------------------------------------------
PREFIXO_FORA_PROPORCAO = "FORA_PROPORCAO_"
MARCADOR_FORA_MEDIDA = "FORA"
PALAVRAS_IGNORAR_NOME = {"IGNORAR", "NAO FAZER", "NÃO FAZER"}

GERAR_RELATORIO_TXT = True
NOME_RELATORIO_TXT = "_relatorio_fechamento.txt"


# ---- 3) ROTEAMENTO POR EXTENSAO -------------------------------------------
EXT_PHOTOSHOP = {
    ".pdf",
    ".psd", ".psb",
    ".jpg", ".jpeg", ".png",
    ".tif", ".tiff", ".bmp",
}

EXT_COREL = {
    ".cdr", ".eps", ".ai",
    ".svg", ".dxf",
}

# PDF tambem pode ser vetorial: se o nome citar CORTE E CONTORNO/ROUTER/LASER
# o PDF entra no CorelDRAW em vez de rasterizar no Photoshop.
EXT_COREL_VETOR_EXTRA = {".pdf"}

EXT_BITMAP = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".psd", ".psb"}

PALAVRAS_SAIDA_VETORIAL = {
    "CORTE E CONTORNO",
    "ROUTER",
    "LASER",
    "CORTE ROUTER",
    "CORTE LASER",
}

# V16: corte/router/laser sai CDR vetorial (era PDF na V15).
FORMATO_VETORIAL_CORTE = "cdr"

MOSTRAR_EXTENSOES_NAO_SUPORTADAS = True


# ---- 4) VALIDACAO DE MEDIDA / PROPORCAO -----------------------------------
TOLERANCIA_CM = 0.5
TOL_PROPORCAO = 0.005


# ---- 5) SAIDA PHOTOSHOP -> TIF --------------------------------------------
DPI_POR_TAMANHO = [
    (60, 300),      # ate 60 cm no lado maior -> 300 dpi
    (None, 100),    # acima disso -> 100 dpi
]
PHOTOSHOP_MODO_COR = "CMYK"           # "CMYK" ou "RGB"
PHOTOSHOP_CROP_PDF = "ARTBOX"          # "ARTBOX","MEDIABOX","BOUNDINGBOX",
                                       #   "CROPBOX","BLEEDBOX","TRIMBOX"
TIF_COMPRESSAO = "LZW"                # "NENHUMA","LZW","ZIP","JPEG"
TIF_EMBUTIR_PERFIL = True


# ---- 6) SAIDA CORELDRAW ---------------------------------------------------
# Para impressao normal o Corel publica PDF temporario e o Photoshop vira TIF.
# A caixa que o Corel publica costuma ser MEDIABOX = tamanho da pagina.
COREL_PDF_CROP_PHOTOSHOP = "MEDIABOX"

# Versao de CDR para tentar no SaveAs (lista de fallbacks; a primeira que
# funcionar e usada). Numeros maiores = arquivos compativeis somente com
# Corel novo. Coloque a versao do Corel da sua maquina no topo.
COREL_CDR_VERSOES_TENTAR = [None, 2020, 2019, 2018, 17, 16, 15, 14]


# ---- 7) AJUSTES INTERNOS ---------------------------------------------------
APLICATIVOS_VISIVEIS = True
SOBRESCREVER_SAIDA = True


# ############################################################################
# #                                                                          #
# #              LOGICA DE EXECUCAO - nao precisa editar abaixo              #
# #                                                                          #
# ############################################################################


_PADRAO_NOME = re.compile(
    r"^"
    r"(?P<qtd>\d+)\s*x\s*[_\-\s]+"
    r"(?P<produto>.+?)"
    r"[_\-\s]+"
    r"(?P<larg>\d+(?:[.,]\d+)?)\s*(?:cm)?\s*x\s*"
    r"(?P<alt>\d+(?:[.,]\d+)?)\s*(?:cm)?"
    r"(?![0-9])",
    re.IGNORECASE,
)

_PADRAO_MEDIDA = re.compile(
    r"(?P<larg>\d+(?:[.,]\d+)?)\s*(?:cm)?\s*x\s*"
    r"(?P<alt>\d+(?:[.,]\d+)?)\s*(?:cm)?",
    re.IGNORECASE,
)


@dataclass
class InfoArquivo:
    caminho: Path
    qtd: int
    produto: str
    larg_cm: float
    alt_cm: float
    medidas_cm: list[tuple[float, float]]

    @property
    def rota(self) -> str:
        ext = self.caminho.suffix.lower()
        if eh_saida_vetorial_obrigatoria(self.caminho):
            if ext in (EXT_COREL | EXT_COREL_VETOR_EXTRA):
                return "corel_vetor"
            if ext in EXT_BITMAP:
                return "vetor_bitmap_invalido"
            return "vetor_extensao_nao_suportada"
        if ext in EXT_PHOTOSHOP:
            return "photoshop"
        if ext in EXT_COREL:
            return "corel"
        return "ignorar"

    @property
    def extensao_saida(self) -> str:
        if self.rota in ("photoshop", "corel"):
            return ".tif"
        if self.rota == "corel_vetor":
            return "." + FORMATO_VETORIAL_CORTE.lower().lstrip(".")
        return ""


def _sem_acentos_upper(s: str) -> str:
    normalizado = unicodedata.normalize("NFKD", s)
    sem_acentos = "".join(ch for ch in normalizado if not unicodedata.combining(ch))
    return sem_acentos.upper()


def eh_saida_vetorial_obrigatoria(caminho: Path) -> bool:
    nome = _sem_acentos_upper(caminho.stem)
    return any(_sem_acentos_upper(p) in nome for p in PALAVRAS_SAIDA_VETORIAL)


def _limpar_produto(s: str) -> str:
    s = re.sub(r"[_\-\s]+", " ", s).strip()
    return re.sub(r"\s+", " ", s)


def deve_ignorar(caminho: Path) -> bool:
    nome = _sem_acentos_upper(caminho.name)
    if nome.startswith(_sem_acentos_upper(PREFIXO_FORA_PROPORCAO)):
        return True
    return any(_sem_acentos_upper(p) in nome for p in PALAVRAS_IGNORAR_NOME)


def extensao_suportada(caminho: Path) -> bool:
    return caminho.suffix.lower() in (
        EXT_PHOTOSHOP | EXT_COREL | EXT_COREL_VETOR_EXTRA
    )


def extrair_medidas_nome(nome: str) -> list[tuple[float, float]]:
    medidas: list[tuple[float, float]] = []
    for m in _PADRAO_MEDIDA.finditer(nome):
        larg = float(m.group("larg").replace(",", "."))
        alt = float(m.group("alt").replace(",", "."))
        if (larg, alt) not in medidas:
            medidas.append((larg, alt))
    return medidas


def parse_nome(caminho: Path) -> InfoArquivo | None:
    m = _PADRAO_NOME.match(caminho.stem)
    if not m:
        return None
    larg = float(m.group("larg").replace(",", "."))
    alt = float(m.group("alt").replace(",", "."))
    return InfoArquivo(
        caminho=caminho,
        qtd=int(m.group("qtd")),
        produto=_limpar_produto(m.group("produto")),
        larg_cm=larg,
        alt_cm=alt,
        medidas_cm=[(larg, alt)],
    )


def dpi_para(larg_cm: float, alt_cm: float) -> int:
    lado = max(larg_cm, alt_cm)
    for limite, dpi in DPI_POR_TAMANHO:
        if limite is None or lado <= limite:
            return int(dpi)
    return int(DPI_POR_TAMANHO[-1][1])


def dentro_da_tolerancia(esperado: float, real: float) -> bool:
    return abs(esperado - real) <= TOLERANCIA_CM


def proporcao_bate(larg_real: float, alt_real: float,
                   larg_pedida: float, alt_pedida: float) -> bool:
    if min(larg_real, alt_real, larg_pedida, alt_pedida) <= 0:
        return False
    return (abs((larg_real / alt_real) - (larg_pedida / alt_pedida))
            / (larg_pedida / alt_pedida) < TOL_PROPORCAO)


def medida_txt(larg_cm: float, alt_cm: float) -> str:
    return f"{larg_cm:.2f}x{alt_cm:.2f}"


def nome_saida_fora(caminho: Path, larg_real: float, alt_real: float,
                    extensao_saida: str) -> str:
    ext = extensao_saida.lower().lstrip(".")
    return f"{caminho.stem} {MARCADOR_FORA_MEDIDA} {medida_txt(larg_real, alt_real)}.{ext}"


def preparar_destino(destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if SOBRESCREVER_SAIDA and destino.exists():
        destino.unlink()


# ============================================================================
# MEDIDOR EXTERNO DE PDF  (pypdf) - evita abrir no Photoshop so para medir
# ============================================================================

_PYPDF_BOX_ATTR = {
    "ARTBOX":      "artbox",
    "MEDIABOX":    "mediabox",
    "CROPBOX":     "cropbox",
    "BLEEDBOX":    "bleedbox",
    "TRIMBOX":     "trimbox",
    "BOUNDINGBOX": "mediabox",  # pypdf nao tem boundingbox; usa mediabox
}


def medir_caixa_pdf(pdf_path: Path, caixa: str) -> tuple[float, float] | None:
    """Le largura/altura (em cm) da caixa pedida na primeira pagina do PDF.

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


# ============================================================================
# PHOTOSHOP
# ============================================================================

_PS_MODE_PDF_JSX = {"CMYK": "OpenDocumentMode.CMYK", "RGB": "OpenDocumentMode.RGB"}
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
    return str(p).replace("\\", "/")


def _ps_render_pdf_para_tif(
    pdf_origem: Path,
    destino_tif: Path,
    larg_final_cm: float,
    alt_final_cm: float,
    target_dpi: int,
    relabel_para_pedido: bool,
    caixa: str,
) -> tuple[float, float]:
    """Renderiza um PDF como TIF LZW UMA UNICA VEZ no Photoshop.

    Pre-requisito: a largura/altura natural ja foram medidas por fora
    (com pypdf) e foi calculado o DPI de abertura de forma que a imagem
    aberta tenha ja o tamanho final pedido. Aqui apenas:
        1) abre o PDF no DPI calculado
        2) se relabel_para_pedido=True, ajusta apenas cm/dpi na metadata,
           sem reamostrar
        3) salva como TIF LZW

    Retorna a medida real lida APOS o open (em cm) para diagnostico.
    """
    import json

    preparar_destino(destino_tif)
    ps = win32com.client.Dispatch("Photoshop.Application")
    ps.Visible = APLICATIVOS_VISIVEIS

    modo_pdf_jsx = _PS_MODE_PDF_JSX[PHOTOSHOP_MODO_COR.upper()]
    comp_jsx = _PS_TIF_COMPRESSION_JSX[TIF_COMPRESSAO.upper()]
    crop_jsx = _PS_CROP_JSX[caixa.upper()]
    embed = "true" if TIF_EMBUTIR_PERFIL else "false"

    pdf_lit = json.dumps(_jsx_path(pdf_origem))
    out_lit = json.dumps(_jsx_path(destino_tif))
    relabel_lit = "true" if relabel_para_pedido else "false"

    # OBS: target_dpi pode ser float (calculo de open_dpi); arredondamos
    # para inteiro apenas no resize/relabel final.
    target_dpi_int = int(round(target_dpi))

    jsx = f"""
    var __resultado, __step = "inicio";
    var doc = null;
    function fecharSemSalvar(d) {{
      try {{ if (d) d.close(SaveOptions.DONOTSAVECHANGES); }} catch(e) {{}}
    }}
    try {{
      __step = "prefs";
      app.preferences.rulerUnits = Units.CM;

      __step = "open.opts";
      var opts = new PDFOpenOptions();
      opts.resolution = {float(target_dpi)};
      opts.mode       = {modo_pdf_jsx};
      opts.antiAlias  = true;
      opts.cropPage   = {crop_jsx};

      __step = "app.open";
      doc = app.open(new File({pdf_lit}), opts);

      var natW = doc.width.as("cm");
      var natH = doc.height.as("cm");

      if ({relabel_lit}) {{
        __step = "relabel";
        doc.resizeImage(undefined, undefined, {target_dpi_int}, ResampleMethod.NONE);
      }}

      __step = "save_tif";
      var out = new File({out_lit});
      if (out.exists) out.remove();
      var tif = new TiffSaveOptions();
      tif.imageCompression  = {comp_jsx};
      tif.byteOrder         = ByteOrder.IBM;
      tif.embedColorProfile = {embed};
      tif.transparency      = false;
      doc.saveAs(out, tif, true);

      __step = "close";
      fecharSemSalvar(doc); doc = null;
      __resultado = "OK|" + natW.toFixed(2) + "|" + natH.toFixed(2);
    }} catch(e) {{
      fecharSemSalvar(doc);
      __resultado = "ERRO|step=" + __step + "|" + e.toString();
    }}
    __resultado;
    """

    resultado = str(ps.DoJavaScript(jsx)).strip()
    partes = resultado.split("|")
    if partes[0] == "OK" and len(partes) >= 3:
        return float(partes[1]), float(partes[2])
    raise RuntimeError(f"Photoshop PDF -> TIF: {resultado}")


def _ps_render_pdf_duas_passadas(
    pdf_origem: Path,
    destino_tif: Path,
    nameW: float, nameH: float,
    target_dpi: int,
    caixa: str,
) -> tuple[float, float, bool, bool]:
    """Fallback (sem pypdf): faz duas passadas no Photoshop.

    Retorna (natW, natH, proporcional, bateuMedidaExata).
    """
    import json

    preparar_destino(destino_tif)
    ps = win32com.client.Dispatch("Photoshop.Application")
    ps.Visible = APLICATIVOS_VISIVEIS

    modo_pdf_jsx = _PS_MODE_PDF_JSX[PHOTOSHOP_MODO_COR.upper()]
    comp_jsx = _PS_TIF_COMPRESSION_JSX[TIF_COMPRESSAO.upper()]
    crop_jsx = _PS_CROP_JSX[caixa.upper()]
    embed = "true" if TIF_EMBUTIR_PERFIL else "false"

    pdf_lit = json.dumps(_jsx_path(pdf_origem))
    out_lit = json.dumps(_jsx_path(destino_tif))

    jsx = f"""
    var __resultado, __step = "inicio";
    var doc = null;
    function fecharSemSalvar(d) {{
      try {{ if (d) d.close(SaveOptions.DONOTSAVECHANGES); }} catch(e) {{}}
    }}
    try {{
      app.preferences.rulerUnits = Units.CM;
      var nameW = {float(nameW)}, nameH = {float(nameH)};
      var targetDPI = {int(target_dpi)};
      var TOL_RATIO = {TOL_PROPORCAO};
      var TOL_CM = {TOLERANCIA_CM};

      __step = "pass1.open";
      var o1 = new PDFOpenOptions();
      o1.resolution = 72;
      o1.mode = {modo_pdf_jsx}; o1.antiAlias = true; o1.cropPage = {crop_jsx};
      doc = app.open(new File({pdf_lit}), o1);
      var natW = doc.width.as("cm"); var natH = doc.height.as("cm");
      fecharSemSalvar(doc); doc = null;

      var bateuMedida = Math.abs(natW - nameW) <= TOL_CM && Math.abs(natH - nameH) <= TOL_CM;
      var proporcaoBateu = Math.abs((natW/natH) - (nameW/nameH))/(nameW/nameH) < TOL_RATIO;
      var proporcional = bateuMedida || proporcaoBateu;
      var openDPI = proporcional ? (targetDPI * nameW / natW) : targetDPI;

      __step = "pass2.open";
      var o2 = new PDFOpenOptions();
      o2.resolution = openDPI;
      o2.mode = {modo_pdf_jsx}; o2.antiAlias = true; o2.cropPage = {crop_jsx};
      doc = app.open(new File({pdf_lit}), o2);
      if (proporcional) {{
        doc.resizeImage(undefined, undefined, targetDPI, ResampleMethod.NONE);
      }}

      __step = "save";
      var out = new File({out_lit});
      if (out.exists) out.remove();
      var tif = new TiffSaveOptions();
      tif.imageCompression = {comp_jsx};
      tif.byteOrder = ByteOrder.IBM;
      tif.embedColorProfile = {embed};
      tif.transparency = false;
      doc.saveAs(out, tif, true);
      fecharSemSalvar(doc); doc = null;

      __resultado = "OK|" + natW.toFixed(2) + "|" + natH.toFixed(2)
                  + "|" + (proporcional?"PROP":"FORA")
                  + "|" + (bateuMedida?"MATCH":(proporcaoBateu?"AJUSTADO":"FORA"));
    }} catch(e) {{
      fecharSemSalvar(doc);
      __resultado = "ERRO|step=" + __step + "|" + e.toString();
    }}
    __resultado;
    """

    resultado = str(ps.DoJavaScript(jsx)).strip()
    p = resultado.split("|")
    if p[0] == "OK" and len(p) >= 5:
        return (float(p[1]), float(p[2]), p[3] == "PROP", p[4] == "MATCH")
    raise RuntimeError(f"Photoshop (fallback 2 passadas): {resultado}")


def processar_photoshop(info: InfoArquivo, pasta_saida: Path) -> str:
    """
    Para PDF:
        - Se pypdf instalado: mede a caixa por fora -> calcula open_dpi
          -> abre UMA UNICA VEZ no PS no DPI calculado -> relabela cm/dpi
          sem reamostrar -> salva TIF. Zero render perdido, zero ampliacao.
        - Se pypdf NAO instalado: cai para duas passadas (a versao da V15).
    Para PSD/TIF/JPG/PNG/BMP:
        - Abre no PS, mede, e ou redimensiona para o pedido (proporcao
          bate) ou salva como esta com marcador FORA.
    """
    if info.caminho.suffix.lower() == ".pdf":
        return _processar_pdf_no_photoshop(info, pasta_saida)
    return _processar_imagem_no_photoshop(info, pasta_saida)


def _processar_pdf_no_photoshop(info: InfoArquivo, pasta_saida: Path) -> str:
    pasta_saida.mkdir(parents=True, exist_ok=True)
    target_dpi = dpi_para(info.larg_cm, info.alt_cm)

    medida = medir_caixa_pdf(info.caminho, PHOTOSHOP_CROP_PDF)

    # ---------------- caminho "via pypdf" (preferido) ----------------------
    if medida is not None:
        nat_w, nat_h = medida
        bateu_medida = (dentro_da_tolerancia(info.larg_cm, nat_w)
                        and dentro_da_tolerancia(info.alt_cm, nat_h))
        prop_ok = proporcao_bate(nat_w, nat_h, info.larg_cm, info.alt_cm)
        proporcional = bateu_medida or prop_ok

        if proporcional:
            # abre direto no DPI que produz a quantidade de pixels desejada
            open_dpi = target_dpi * info.larg_cm / nat_w
            nome_arq = info.caminho.with_suffix(".tif").name
        else:
            open_dpi = target_dpi
            nome_arq = nome_saida_fora(info.caminho, nat_w, nat_h, ".tif")

        destino = pasta_saida / nome_arq

        try:
            _ps_render_pdf_para_tif(
                info.caminho, destino,
                info.larg_cm, info.alt_cm,
                open_dpi, proporcional, PHOTOSHOP_CROP_PDF,
            )
        except Exception as exc:  # noqa: BLE001
            return f"[ERRO] {info.caminho.name}: {exc}"

        if proporcional:
            tipo = "medida bateu" if bateu_medida else "proporcao bateu; ajustado para o pedido"
            return (f"[OK]   {info.caminho.name}: PDF -> TIF {target_dpi} dpi, {tipo}, "
                    f"pedido {info.larg_cm:g}x{info.alt_cm:g}cm "
                    f"(ArtBox real {nat_w:.2f}x{nat_h:.2f}cm; "
                    f"abriu @ {open_dpi:.0f} dpi, 1 passada, sem reamostragem) "
                    f"-> {destino}")
        return (f"[FORA] {info.caminho.name}: PDF -> TIF, nao deu para colocar no "
                f"pedido {info.larg_cm:g}x{info.alt_cm:g}cm sem distorcer; arquivo "
                f"esta {nat_w:.2f}x{nat_h:.2f}cm -> {destino}")

    # ---------------- caminho fallback (sem pypdf) -------------------------
    nome_arq_provavel = info.caminho.with_suffix(".tif").name
    destino = pasta_saida / nome_arq_provavel
    try:
        natW, natH, proporcional, bateu = _ps_render_pdf_duas_passadas(
            info.caminho, destino,
            info.larg_cm, info.alt_cm,
            target_dpi, PHOTOSHOP_CROP_PDF,
        )
    except Exception as exc:  # noqa: BLE001
        return f"[ERRO] {info.caminho.name}: {exc}"

    if not proporcional:
        # Renomeia para refletir o FORA (o jsx ja salvou como nome_arq_provavel).
        novo_nome = nome_saida_fora(info.caminho, natW, natH, ".tif")
        novo_destino = pasta_saida / novo_nome
        if destino.exists():
            preparar_destino(novo_destino)
            destino.rename(novo_destino)
            destino = novo_destino
        return (f"[FORA] {info.caminho.name}: PDF -> TIF (fallback 2 passadas, instale "
                f"pypdf para 1 passada). Arquivo esta {natW:.2f}x{natH:.2f}cm -> {destino}")

    tipo = "medida bateu" if bateu else "proporcao bateu; ajustado"
    return (f"[OK*]  {info.caminho.name}: PDF -> TIF {target_dpi} dpi, {tipo}, "
            f"fallback 2 passadas (instale `pip install pypdf` para abrir 1 vez so) "
            f"-> {destino}")


def _processar_imagem_no_photoshop(info: InfoArquivo, pasta_saida: Path) -> str:
    """PSD/TIF/JPG/PNG/BMP: abre no Photoshop, mede, redimensiona se bater."""
    import json
    pasta_saida.mkdir(parents=True, exist_ok=True)

    ps = win32com.client.Dispatch("Photoshop.Application")
    ps.Visible = APLICATIVOS_VISIVEIS

    modo_cor = PHOTOSHOP_MODO_COR.upper()
    comp_jsx = _PS_TIF_COMPRESSION_JSX[TIF_COMPRESSAO.upper()]
    embed = "true" if TIF_EMBUTIR_PERFIL else "false"
    in_lit = json.dumps(_jsx_path(info.caminho))
    saida_lit = json.dumps(_jsx_path(pasta_saida))
    base_lit = json.dumps(info.caminho.stem)
    modo_lit = json.dumps(modo_cor)

    jsx = f"""
    var __resultado, __step = "inicio"; var doc = null;
    function fecharSemSalvar(d) {{
      try {{ if (d) d.close(SaveOptions.DONOTSAVECHANGES); }} catch(e) {{}}
    }}
    try {{
      app.preferences.rulerUnits = Units.CM;
      var nameW = {info.larg_cm}, nameH = {info.alt_cm};
      var TOL_CM = {TOLERANCIA_CM}, TOL_RATIO = {TOL_PROPORCAO};
      var modoAlvo = {modo_lit};
      var dpiRegras = [
        {", ".join(f"[{limite!s},{dpi}]" if limite is not None else f"[null,{dpi}]"
                  for limite, dpi in DPI_POR_TAMANHO)}
      ];
      function dpiPara(w, h) {{
        var lado = Math.max(w, h);
        for (var i=0;i<dpiRegras.length;i++) {{
          var lim = dpiRegras[i][0], d = dpiRegras[i][1];
          if (lim === null || lado <= lim) return d;
        }}
        return dpiRegras[dpiRegras.length-1][1];
      }}

      __step = "open";
      doc = app.open(new File({in_lit}));
      var natW = doc.width.as("cm");
      var natH = doc.height.as("cm");

      __step = "mode";
      if (modoAlvo == "CMYK" && doc.mode != DocumentMode.CMYK) doc.changeMode(ChangeMode.CMYK);
      if (modoAlvo == "RGB"  && doc.mode != DocumentMode.RGB)  doc.changeMode(ChangeMode.RGB);

      var bateuMedida = Math.abs(natW - nameW) <= TOL_CM && Math.abs(natH - nameH) <= TOL_CM;
      var proporcaoBateu = Math.abs((natW/natH) - (nameW/nameH))/(nameW/nameH) < TOL_RATIO;
      var proporcional = bateuMedida || proporcaoBateu;
      var targetDPI = dpiPara(nameW, nameH);

      var nomeArq;
      if (proporcional) {{
        __step = "resize";
        doc.resizeImage(UnitValue(nameW, "cm"), UnitValue(nameH, "cm"),
                        targetDPI, ResampleMethod.BICUBIC);
        nomeArq = {base_lit} + ".tif";
      }} else {{
        nomeArq = {base_lit} + " {MARCADOR_FORA_MEDIDA} " + natW.toFixed(2) + "x" + natH.toFixed(2) + ".tif";
      }}

      __step = "save";
      var out = new File({saida_lit} + "/" + nomeArq);
      if (out.exists) out.remove();
      var tif = new TiffSaveOptions();
      tif.imageCompression  = {comp_jsx};
      tif.byteOrder         = ByteOrder.IBM;
      tif.embedColorProfile = {embed};
      tif.transparency      = false;
      doc.saveAs(out, tif, true);
      fecharSemSalvar(doc); doc = null;

      __resultado = "OK|" + (proporcional?"PROP":"FORA") + "|"
                  + natW.toFixed(2) + "|" + natH.toFixed(2) + "|"
                  + targetDPI + "|" + (bateuMedida?"MATCH":(proporcaoBateu?"AJUSTADO":"FORA"))
                  + "|" + nomeArq;
    }} catch(e) {{
      fecharSemSalvar(doc);
      __resultado = "ERRO|step=" + __step + "|" + e.toString();
    }}
    __resultado;
    """

    resultado = str(ps.DoJavaScript(jsx)).strip()
    p = resultado.split("|")
    if p[0] == "OK" and len(p) >= 7:
        modo, natW, natH, dpi, tipo, nome = p[1], p[2], p[3], p[4], p[5], p[6]
        destino = pasta_saida / nome
        if modo == "PROP":
            extra = ("medida bateu" if tipo == "MATCH"
                     else "proporcao bateu; ajustado")
            return (f"[OK]   {info.caminho.name}: Photoshop -> TIF {dpi} dpi, "
                    f"{extra}, pedido {info.larg_cm:g}x{info.alt_cm:g}cm "
                    f"(real {natW}x{natH}cm) -> {destino}")
        return (f"[FORA] {info.caminho.name}: Photoshop -> TIF, nao deu para colocar no "
                f"pedido {info.larg_cm:g}x{info.alt_cm:g}cm; arquivo esta "
                f"{natW}x{natH}cm -> {destino}")
    return f"[ERRO] {info.caminho.name}: {resultado}"


# ============================================================================
# CORELDRAW
# ============================================================================

CDR_CENTIMETER = 5


def _como_float(valor) -> float:
    try:
        return float(valor)
    except Exception:
        return float(str(valor).replace(",", "."))


def abrir_corel():
    """Abre o CorelDRAW preferindo EARLY-binding (gencache.EnsureDispatch).

    Por que EnsureDispatch e nao Dispatch?
        O CorelDRAW SaveAs tem parametros opcionais com tipos de enum
        proprios (cdrFileVersion, cdrFilter etc.). Em late-binding o
        pywin32 nao conhece esses tipos e gera o erro:
            "The Python instance can not be converted to a COM object"
        EnsureDispatch gera stubs Python a partir do type library do
        Corel e o pywin32 passa a saber marshallar tudo direito.

    Primeira chamada pode demorar 10-30s gerando %TEMP%/gen_py/...
    Se a geracao falhar (permissao, typelib quebrada), cai para
    Dispatch tardio com aviso - nesse caso o SaveAs CDR pode falhar
    e a unica saida e regenerar manualmente:
        python -m win32com.client.makepy "CorelDRAW.Application"
    ou apagar a pasta %TEMP%/gen_py e rodar de novo.
    """
    try:
        from win32com.client import gencache
        corel = gencache.EnsureDispatch("CorelDRAW.Application")
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(
            f"[AVISO] EnsureDispatch falhou ({exc}); usando Dispatch tardio. "
            "SaveAs como CDR pode falhar. Tente apagar %TEMP%/gen_py e rodar de novo.\n"
        )
        corel = win32com.client.Dispatch("CorelDRAW.Application")
    corel.Visible = APLICATIVOS_VISIVEIS
    return corel


def medir_pagina_corel_cm(doc, _corel) -> tuple[float, float]:
    try:
        doc.Unit = CDR_CENTIMETER
    except Exception:
        pass
    pagina = doc.ActivePage
    return _como_float(pagina.SizeWidth), _como_float(pagina.SizeHeight)


def fechar_corel_sem_salvar(doc) -> None:
    if doc is None:
        return
    try:
        doc.Close()
    except Exception:
        pass


def publicar_corel_pdf_temporario(doc, destino_pdf: Path) -> None:
    destino_pdf.parent.mkdir(parents=True, exist_ok=True)
    if destino_pdf.exists():
        try:
            destino_pdf.unlink()
        except Exception:
            pass

    caminho = str(destino_pdf.resolve())
    erros: list[str] = []

    try:
        pdf_settings = doc.PDFSettings
        for attr, value in (
            ("PublishRange", 1),
            ("ColorMode", 1),
            ("EmbedFonts", True),
            ("BitmapCompression", 1),
        ):
            try:
                setattr(pdf_settings, attr, value)
            except Exception:
                pass
    except Exception:
        pass

    try:
        doc.PublishToPDF(caminho)
        if destino_pdf.exists() and destino_pdf.stat().st_size > 0:
            return
        erros.append("PublishToPDF executou mas PDF nao apareceu/vazio")
    except Exception as exc:  # noqa: BLE001
        erros.append(f"doc.PublishToPDF: {exc}")

    try:
        doc.Application.ActiveDocument.PublishToPDF(caminho)
        if destino_pdf.exists() and destino_pdf.stat().st_size > 0:
            return
    except Exception as exc:  # noqa: BLE001
        erros.append(f"ActiveDocument.PublishToPDF: {exc}")

    raise RuntimeError("; ".join(erros))


def salvar_cdr_corel(doc, destino_cdr: Path) -> None:
    """SaveAs como CDR. Depende do Corel ter sido aberto via
    abrir_corel() -> EnsureDispatch (early-binding); caso contrario o
    pywin32 nao consegue marshalar o SaveAs.

    Estrategias em cascata:
        1) doc.SaveAs(path)
        2) doc.Application.ActiveDocument.SaveAs(path)  (caso doc esteja stale)
        3) doc.SaveAs(path, versao) para cada versao em COREL_CDR_VERSOES_TENTAR
    """
    destino_cdr.parent.mkdir(parents=True, exist_ok=True)
    if destino_cdr.exists():
        try:
            destino_cdr.unlink()
        except Exception:
            pass

    caminho = str(destino_cdr.resolve())
    erros: list[str] = []

    def tentar(desc: str, chamada) -> bool:
        try:
            chamada()
            if destino_cdr.exists() and destino_cdr.stat().st_size > 0:
                return True
            erros.append(f"{desc}: arquivo nao apareceu")
        except Exception as exc:  # noqa: BLE001
            erros.append(f"{desc}: {exc}")
        return False

    # 1) SaveAs simples no doc atual
    if tentar("doc.SaveAs(path)", lambda: doc.SaveAs(caminho)):
        return

    # 2) Re-pega o ActiveDocument (defensivo)
    try:
        active = doc.Application.ActiveDocument
        if tentar("ActiveDocument.SaveAs(path)",
                  lambda: active.SaveAs(caminho)):
            return
    except Exception as exc:  # noqa: BLE001
        erros.append(f"ActiveDocument acesso: {exc}")

    # 3) Com versao explicita
    for versao in COREL_CDR_VERSOES_TENTAR:
        if versao is None:
            continue
        if tentar(f"doc.SaveAs(path, v={versao})",
                  lambda v=versao: doc.SaveAs(caminho, int(v))):
            return

    raise RuntimeError("; ".join(erros))


# ---- CDR/EPS/AI/SVG/DXF em IMPRESSAO normal: Corel -> PDF temp -> PS TIF ---

def processar_corel(info: InfoArquivo, pasta_saida: Path) -> str:
    corel = abrir_corel()
    doc = None
    step = "inicio"
    temp_pdf: Path | None = None
    try:
        step = "abrir_documento"
        doc = corel.OpenDocument(str(info.caminho.resolve()))

        step = "medir_pagina_cm"
        larg_real, alt_real = medir_pagina_corel_cm(doc, corel)

        bateu = (dentro_da_tolerancia(info.larg_cm, larg_real)
                 and dentro_da_tolerancia(info.alt_cm, alt_real))
        prop_ok = proporcao_bate(larg_real, alt_real, info.larg_cm, info.alt_cm)
        ajustar = bateu or prop_ok

        if ajustar:
            nome_final = info.caminho.with_suffix(".tif").name
            larg_final, alt_final = info.larg_cm, info.alt_cm
            dpi = dpi_para(info.larg_cm, info.alt_cm)
        else:
            nome_final = nome_saida_fora(info.caminho, larg_real, alt_real, ".tif")
            larg_final, alt_final = larg_real, alt_real
            dpi = dpi_para(larg_real, alt_real)

        destino = pasta_saida / nome_final
        temp_dir = pasta_saida / "_tmp_corel_pdf"
        temp_pdf = temp_dir / (info.caminho.stem + "__corel_temp.pdf")

        step = "publicar_pdf_temporario"
        publicar_corel_pdf_temporario(doc, temp_pdf)

        # MEDE o PDF temporario por fora (pypdf) para abrir 1 vez so no PS.
        step = "medir_pdf_temp"
        medida_temp = medir_caixa_pdf(temp_pdf, COREL_PDF_CROP_PHOTOSHOP)

        step = "photoshop_pdf_para_tif"
        if medida_temp is not None and ajustar:
            temp_w, _temp_h = medida_temp
            open_dpi = dpi * larg_final / temp_w
            _ps_render_pdf_para_tif(temp_pdf, destino, larg_final, alt_final,
                                    open_dpi, True, COREL_PDF_CROP_PHOTOSHOP)
            modo_msg = f"1 passada (abriu @ {open_dpi:.0f} dpi)"
        elif medida_temp is not None and not ajustar:
            _ps_render_pdf_para_tif(temp_pdf, destino, larg_final, alt_final,
                                    dpi, False, COREL_PDF_CROP_PHOTOSHOP)
            modo_msg = "1 passada no tamanho natural"
        else:
            # Sem pypdf, cai pra 2 passadas
            _ps_render_pdf_duas_passadas(temp_pdf, destino, larg_final, alt_final,
                                          dpi, COREL_PDF_CROP_PHOTOSHOP)
            modo_msg = "2 passadas (instale pypdf)"

        if ajustar:
            extra = "pagina bateu" if bateu else "proporcao bateu; ajustado"
            return (f"[OK]   {info.caminho.name}: Corel -> PDF temp -> Photoshop TIF "
                    f"{dpi} dpi, {extra}, {modo_msg}, pedido "
                    f"{info.larg_cm:g}x{info.alt_cm:g}cm "
                    f"(pagina Corel {larg_real:.2f}x{alt_real:.2f}cm) -> {destino}")
        return (f"[FORA] {info.caminho.name}: Corel -> PDF temp -> Photoshop TIF "
                f"{dpi} dpi, nao deu para colocar no pedido "
                f"{info.larg_cm:g}x{info.alt_cm:g}cm; pagina esta "
                f"{larg_real:.2f}x{alt_real:.2f}cm -> {destino}")

    except Exception as exc:  # noqa: BLE001
        return f"[ERRO] {info.caminho.name}: Corel step={step}: {exc}"
    finally:
        fechar_corel_sem_salvar(doc)
        if temp_pdf is not None:
            try:
                if temp_pdf.exists():
                    temp_pdf.unlink()
                temp_pdf.parent.rmdir()
            except Exception:
                pass


# ---- CORTE/ROUTER/LASER: Corel -> CDR vetorial -----------------------------

def _ajustar_corel_para_medida(doc, larg_cm: float, alt_cm: float) -> str:
    """Coloca a pagina e o desenho no tamanho pedido (proporcao bate)."""
    erros: list[str] = []
    try:
        doc.Unit = CDR_CENTIMETER
    except Exception as exc:  # noqa: BLE001
        erros.append(f"doc.Unit: {exc}")

    pagina = doc.ActivePage
    try:
        pagina.SetSize(float(larg_cm), float(alt_cm))
    except Exception as exc:  # noqa: BLE001
        erros.append(f"SetSize: {exc}")
        try:
            pagina.SizeWidth = float(larg_cm)
            pagina.SizeHeight = float(alt_cm)
        except Exception as exc2:  # noqa: BLE001
            erros.append(f"SizeWidth/Height: {exc2}")

    try:
        sr = pagina.Shapes.All
        if callable(sr):
            sr = sr()
        try:
            doc.ReferencePoint = 4   # cdrCenter
        except Exception:
            pass
        for desc, chamada in (
            ("SetBoundingBox", lambda: sr.SetBoundingBox(
                float(larg_cm)/2, float(alt_cm)/2, float(larg_cm), float(alt_cm), False)),
            ("SetSize", lambda: sr.SetSize(float(larg_cm), float(alt_cm))),
        ):
            try:
                chamada()
                try:
                    sr.AlignToPageCenter()
                except Exception:
                    pass
                return "pagina e objetos ajustados"
            except Exception as exc:  # noqa: BLE001
                erros.append(f"{desc}: {exc}")
    except Exception as exc:  # noqa: BLE001
        erros.append(f"shapes: {exc}")

    return "pagina ajustada; objetos nao confirmados (" + "; ".join(erros) + ")"


def processar_corel_vetor(info: InfoArquivo, pasta_saida: Path) -> str:
    """Corte/router/laser. Saida CDR vetorial. NUNCA vira TIF."""
    corel = abrir_corel()
    doc = None
    step = "inicio"
    try:
        step = "abrir_documento_vetorial"
        doc = corel.OpenDocument(str(info.caminho.resolve()))

        step = "medir_pagina_cm"
        larg_real, alt_real = medir_pagina_corel_cm(doc, corel)

        bateu = (dentro_da_tolerancia(info.larg_cm, larg_real)
                 and dentro_da_tolerancia(info.alt_cm, alt_real))
        prop_ok = proporcao_bate(larg_real, alt_real, info.larg_cm, info.alt_cm)

        ajustou_info = ""
        if bateu:
            nome_final = info.caminho.with_suffix("." + FORMATO_VETORIAL_CORTE).name
            status = "MATCH"
        elif prop_ok:
            step = "ajustar_vetor"
            ajustou_info = _ajustar_corel_para_medida(doc, info.larg_cm, info.alt_cm)
            nome_final = info.caminho.with_suffix("." + FORMATO_VETORIAL_CORTE).name
            status = "AJUSTADO"
        else:
            nome_final = nome_saida_fora(info.caminho, larg_real, alt_real,
                                         "." + FORMATO_VETORIAL_CORTE)
            status = "FORA"

        destino = pasta_saida / nome_final

        step = "salvar_cdr"
        salvar_cdr_corel(doc, destino)

        if status == "MATCH":
            return (f"[OK-VETOR] {info.caminho.name}: corte/router/laser, pagina bateu; "
                    f"saiu CDR vetorial -> {destino}")
        if status == "AJUSTADO":
            return (f"[OK-VETOR] {info.caminho.name}: corte/router/laser, proporcao bateu; "
                    f"{ajustou_info}; saiu CDR vetorial -> {destino}")
        return (f"[FORA-VETOR] {info.caminho.name}: corte/router/laser nao pode virar TIF e "
                f"nao deu para colocar em {info.larg_cm:g}x{info.alt_cm:g}cm sem risco; "
                f"saiu CDR {larg_real:.2f}x{alt_real:.2f}cm -> {destino}")
    except Exception as exc:  # noqa: BLE001
        return f"[ERRO] {info.caminho.name}: CorelDRAW VETOR step={step}: {exc}"
    finally:
        fechar_corel_sem_salvar(doc)


# ============================================================================
# LOOP
# ============================================================================


def listar_arquivos(raiz: Path) -> list[Path]:
    if not raiz.exists():
        return []
    arquivos: list[Path] = []
    for p in raiz.iterdir():
        if not p.is_file():
            continue
        if deve_ignorar(p):
            continue
        if extensao_suportada(p) or MOSTRAR_EXTENSOES_NAO_SUPORTADAS:
            arquivos.append(p)
    return sorted(arquivos, key=lambda x: x.name.lower())


def descrever_dry_run(info: InfoArquivo) -> str:
    if info.rota == "photoshop":
        return (f"[DRY]  {info.caminho.name}: qtd={info.qtd}, produto='{info.produto}', "
                f"{info.larg_cm:g}x{info.alt_cm:g}cm, Photoshop -> .tif")
    if info.rota == "corel":
        return (f"[DRY]  {info.caminho.name}: qtd={info.qtd}, produto='{info.produto}', "
                f"{info.larg_cm:g}x{info.alt_cm:g}cm, CorelDRAW -> PDF temp -> .tif LZW")
    if info.rota == "corel_vetor":
        return (f"[DRY]  {info.caminho.name}: qtd={info.qtd}, produto='{info.produto}', "
                f"{info.larg_cm:g}x{info.alt_cm:g}cm, CorelDRAW -> .cdr VETORIAL "
                f"(corte/router/laser, nunca TIF)")
    if info.rota == "vetor_bitmap_invalido":
        return (f"[BLOQ] {info.caminho.name}: nome indica corte/router/laser, mas a extensao "
                f"'{info.caminho.suffix.lower()}' e bitmap. Nao gero TIF para corte.")
    return f"[SKIP] {info.caminho.name}: extensao nao suportada"


def gravar_relatorio(pasta_saida: Path, linhas: list[str]) -> None:
    if not GERAR_RELATORIO_TXT:
        return
    pasta_saida.mkdir(parents=True, exist_ok=True)
    relatorio = pasta_saida / NOME_RELATORIO_TXT
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    conteudo = [f"Relatorio de fechamento - {agora}", ""] + linhas + [""]
    relatorio.write_text("\n".join(conteudo), encoding="utf-8")


def processar(arquivos: list[Path], pasta_saida: Path, dry_run: bool = False) -> list[str]:
    resultados: list[str] = []
    for caminho in arquivos:
        if deve_ignorar(caminho):
            msg = f"[SKIP] {caminho.name}: arquivo marcado para ignorar"
        elif not extensao_suportada(caminho):
            msg = (f"[SKIP] {caminho.name}: extensao '{caminho.suffix.lower()}' "
                   f"nao suportada pela regra")
        else:
            info = parse_nome(caminho)
            if info is None:
                msg = (f"[SKIP] {caminho.name}: nome fora do padrao "
                       f"<qtd>x_<produto>_<LxA>")
            else:
                try:
                    if dry_run:
                        msg = descrever_dry_run(info)
                    elif info.rota == "photoshop":
                        msg = processar_photoshop(info, pasta_saida)
                    elif info.rota == "corel":
                        msg = processar_corel(info, pasta_saida)
                    elif info.rota == "corel_vetor":
                        msg = processar_corel_vetor(info, pasta_saida)
                    elif info.rota == "vetor_bitmap_invalido":
                        msg = (f"[BLOQ] {caminho.name}: nome indica corte/router/laser, mas "
                               f"o arquivo e bitmap. Nao e seguro gerar TIF para corte; "
                               f"envie vetor CDR/PDF/AI/EPS/SVG/DXF.")
                    else:
                        msg = f"[SKIP] {caminho.name}: extensao nao suportada"
                except Exception as exc:  # noqa: BLE001
                    msg = f"[ERRO] {caminho.name}: {exc}"
        print(msg)
        resultados.append(msg)
    gravar_relatorio(pasta_saida, resultados)
    return resultados


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raiz", nargs="?", default=RAIZ_PADRAO,
                        help=f"Pasta raiz (padrao: {RAIZ_PADRAO})")
    parser.add_argument("--arquivo", help="Processa um unico arquivo")
    parser.add_argument("--dry-run", action="store_true",
                        help="Apenas interpreta os nomes; nao abre Photoshop/Corel")
    args = parser.parse_args()

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

    if win32com is None and not args.dry_run:
        print("ERRO: pywin32 nao instalado. Rode: pip install pywin32 pypdf")
        return 1

    if PdfReader is None and not args.dry_run:
        print("AVISO: pypdf nao instalado. PDFs vao usar fallback de 2 passadas. "
              "Rode: pip install pypdf  para abrir 1 vez so.")

    pasta_saida = raiz / SUBPASTA_SAIDA
    processar(arquivos, pasta_saida, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
