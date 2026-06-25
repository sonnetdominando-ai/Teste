"""
Configuracao da automacao de fechamento.

Este arquivo concentra TODAS as regras de negocio. Para alterar qualquer
comportamento do script edite somente este arquivo - nao mexa em
fechamento.py salvo se for mudar a logica.

Cada bloco abaixo e independente. Mude apenas os valores apos o "=".
"""

from __future__ import annotations


# ============================================================================
# 1) PASTAS
# ============================================================================
# Pasta raiz onde os arquivos do cliente sao despejados. Subpasta de saida
# e onde caem os arquivos finais (TIF / CDR) ja conferidos.

RAIZ_PADRAO    = r"C:\2026\Fechamento"
SUBPASTA_SAIDA = "Saida"


# ============================================================================
# 2) NOMENCLATURA DOS ARQUIVOS DO CLIENTE
# ============================================================================
# Padrao esperado no nome:
#     <quantidade>x_<produto>_<largura>x<altura>.<ext>
# Exemplos validos:
#     1x_vinil_fosco_100x100.pdf
#     5x_lona_banner_150x80.pdf
#     1x_adesivo_recorte_50x30.cdr
# Medidas SEMPRE em centimetros.

# Prefixo aplicado quando a dimensao real nao bate com o nome.
# Esses arquivos sao ignorados em execucoes seguintes (nao reprocessa).
PREFIXO_FORA_PROPORCAO = "FORA_PROPORCAO_"


# ============================================================================
# 3) VALIDACAO DA PROPORCAO
# ============================================================================
# Folga aceita ao comparar dimensao do nome com dimensao real do documento.
# 0.1 cm = 1 mm. Aumente se receber arquivos com pequenas variacoes de bleed.

TOLERANCIA_CM = 0.1


# ============================================================================
# 4) ROTEAMENTO POR EXTENSAO
# ============================================================================
# Define qual programa abre cada tipo de arquivo. Para mudar a regra basta
# mover a extensao de um conjunto para o outro.

EXT_PHOTOSHOP = {".pdf"}
EXT_COREL     = {".cdr", ".eps", ".ai"}


# ============================================================================
# 5) SAIDA PHOTOSHOP  ->  TIF para impressao
# ============================================================================
# Formato final de impressao. Regra de DPI baseada no LADO MAIOR do arquivo.
#
# Cada tupla e (lado_maior_ate_cm, dpi). A primeira regra cujo limite
# >= lado maior do arquivo vence. Use None no limite para "sem teto".
# Pode adicionar quantas faixas quiser, basta manter ordenado do menor
# para o maior.

DPI_POR_TAMANHO = [
    # (lado_maior_ate_cm, dpi)
    (60,   300),   # arquivos ate 60 cm   -> 300 dpi
    (None, 100),   # acima de 60 cm        -> 100 dpi
]

# Modo de cor com que o PDF de entrada e aberto e o TIF e salvo.
# Valores aceitos:
#     "CMYK" -> impressao (padrao)
#     "RGB"  -> tela / web
PHOTOSHOP_MODO_COR = "CMYK"

# Qual "caixa" do PDF define o tamanho da pagina aberta no Photoshop.
# Em geral o cliente envia o PDF com a medida final na MEDIABOX. Se vier
# com sangra/bleed, troque para "TRIMBOX" para validar o tamanho de
# corte em vez do tamanho da pagina inteira.
# Valores aceitos: "MEDIABOX", "BOUNDINGBOX", "CROPBOX",
#                  "BLEEDBOX", "TRIMBOX", "ARTBOX"
PHOTOSHOP_CROP_PDF = "MEDIABOX"

# Compressao do TIF final.
# Valores aceitos: "NENHUMA", "LZW", "ZIP", "JPEG"
TIF_COMPRESSAO = "LZW"

# Embute o perfil de cor (ICC) no TIF salvo.
TIF_EMBUTIR_PERFIL = True


# ============================================================================
# 6) SAIDA CORELDRAW  ->  CDR para corte (router / corte e contorno)
# ============================================================================
# Por enquanto so existe um caminho: salva como CDR na pasta de saida.
# Se um dia quiser exportar tambem PLT/EPS para a router, e aqui que
# adicionamos a opcao.

COREL_FORMATO_SAIDA = "cdr"   # extensao do arquivo gerado


# ============================================================================
# 7) AJUSTES INTERNOS (raramente precisam mudar)
# ============================================================================

# Mostra ou nao a janela do Photoshop/Corel enquanto processa.
# Deixe True para acompanhar visualmente; False roda silencioso.
APLICATIVOS_VISIVEIS = True


# ----------------------------------------------------------------------------
# Helpers - nao edite abaixo desta linha salvo se souber o que esta fazendo.
# ----------------------------------------------------------------------------

def dpi_para(larg_cm: float, alt_cm: float) -> int:
    """Retorna o DPI conforme a faixa em DPI_POR_TAMANHO."""
    lado = max(larg_cm, alt_cm)
    for limite, dpi in DPI_POR_TAMANHO:
        if limite is None or lado <= limite:
            return dpi
    return DPI_POR_TAMANHO[-1][1]
