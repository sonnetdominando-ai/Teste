# Automação de Fechamento

Roteiro em Python (Windows) que processa arquivos enviados pelo cliente,
abre no Photoshop ou no CorelDRAW conforme a extensão, valida a
proporção contra o nome do arquivo e gera o arquivo final na pasta
`Saida\`.

> **Onde mexer:** todas as regras (pasta, tolerância, DPI, modo de cor,
> compressão, formatos) ficam em `config.py`. Cada bloco é numerado e
> tem um cabeçalho explicando o que faz. **Não edite `fechamento.py`
> para mudar regra de negócio** — só `config.py`.

---

## 📋 Tabela de regras (resumo)

| # | Bloco do `config.py`     | Define                                        | Valor padrão                              |
|--:|--------------------------|-----------------------------------------------|-------------------------------------------|
| 1 | **Pastas**               | Raiz e subpasta de saída                      | `C:\2026\Fechamento` → `Saida\`           |
| 2 | **Nomenclatura**         | Padrão do nome e prefixo de arquivo fora      | `<qtd>x_<produto>_<LxA>` · `FORA_PROPORCAO_` |
| 3 | **Validação**            | Tolerância na conferência da dimensão         | 1 mm                                      |
| 4 | **Roteamento**           | Extensão → programa                           | `.pdf` → Photoshop · `.cdr/.eps/.ai` → Corel |
| 5 | **Saída Photoshop**      | Formato final, modo de cor, regra de DPI, compressão | TIF · CMYK · 300 dpi (≤60 cm) / 100 dpi (>60 cm) · LZW |
| 6 | **Saída CorelDRAW**      | Formato final                                 | CDR                                       |
| 7 | **Ajustes internos**     | Aplicativos visíveis durante o processamento  | sim                                       |

### Regra de DPI do TIF

| Lado maior do arquivo | DPI |
|-----------------------|----:|
| até **60 cm**         | 300 |
| acima de **60 cm**    | 100 |

> A regra é uma lista de faixas em `DPI_POR_TAMANHO`. Para adicionar
> uma faixa intermediária (ex.: 200 dpi entre 40 e 60 cm), basta
> incluir uma tupla nova mantendo a ordem do menor para o maior.

---

## 🏷️ Convenção de nome

```
<quantidade>x_<produto>_<largura>x<altura>.<ext>
```

| Arquivo                            | Quantidade | Produto      | L × A (cm) | Abre em    | Saída em      |
|------------------------------------|-----------:|--------------|-----------:|------------|---------------|
| `1x_vinil_fosco_100x100.pdf`       | 1          | vinil_fosco  | 100 × 100  | Photoshop  | TIF 100 dpi   |
| `5x_lona_banner_150x80.pdf`        | 5          | lona_banner  | 150 × 80   | Photoshop  | TIF 100 dpi   |
| `1x_adesivo_30x40.pdf`             | 1          | adesivo      | 30 × 40    | Photoshop  | TIF 300 dpi   |
| `1x_adesivo_recorte_50x30.cdr`     | 1          | adesivo_rec. | 50 × 30    | CorelDRAW  | CDR           |
| `2x_logo_corte_contorno_40x40.eps` | 2          | logo…        | 40 × 40    | CorelDRAW  | CDR           |

Medidas **sempre em centímetros**.

---

## ⚙️ O que o script faz

1. Lê todos os arquivos da pasta raiz.
2. Extrai do nome a quantidade, o produto e a dimensão esperada.
3. Abre no programa correto (Photoshop ou CorelDRAW).
4. Compara a dimensão real do documento com a do nome
   (tolerância configurável, padrão 1 mm).
5. **Se bater** → gera o arquivo final em `Saida\` (TIF ou CDR) e
   deixa o arquivo aberto para você terminar a arte.
6. **Se NÃO bater** → fecha o documento sem salvar e renomeia o
   original com o prefixo `FORA_PROPORCAO_real_<L>x<A>_…`.
   O arquivo **nunca** é redimensionado.

---

## 🛠️ Instalação (Windows)

1. Instale Python 3.10+ ([python.org](https://www.python.org/downloads/)).
2. Em um Prompt de Comando:
   ```bat
   pip install pywin32
   ```
3. Copie esta pasta `automacao\` para um lugar fixo (ex.: `C:\automacao\`).

## ▶️ Uso

Forma 1 — clique duplo em `processar.bat`. Processa tudo que está em
`C:\2026\Fechamento`.

Forma 2 — pelo terminal:

```bat
python fechamento.py                                   :: pasta padrao
python fechamento.py "D:\OutroDisco\Fechamento"        :: outra pasta
python fechamento.py --arquivo "C:\...\1x_vinil_fosco_100x100.pdf"
```

---

## 🔧 Como alterar (receitas rápidas)

Tudo abaixo é em `config.py`.

- **Mudar a pasta raiz** → bloco 1, `RAIZ_PADRAO`.
- **Aumentar/diminuir a tolerância** (ex.: aceitar 2 mm de variação)
  → bloco 3, `TOLERANCIA_CM = 0.2`.
- **Adicionar extensão nova ao Photoshop** (ex.: `.jpg`) → bloco 4,
  inclua `".jpg"` em `EXT_PHOTOSHOP`.
- **Mudar o ponto de corte do DPI** (ex.: virar 80 cm) → bloco 5,
  troque o `60` em `DPI_POR_TAMANHO` por `80`.
- **Inserir uma faixa intermediária de DPI**
  → bloco 5, edite `DPI_POR_TAMANHO` para algo como:
  ```python
  DPI_POR_TAMANHO = [
      (40,   300),
      (80,   200),
      (None, 100),
  ]
  ```
- **Saída em RGB em vez de CMYK** → bloco 5,
  `PHOTOSHOP_MODO_COR = "RGB"`.
- **TIF sem compressão** (para RIPs antigos) → bloco 5,
  `TIF_COMPRESSAO = "NENHUMA"`.
- **Rodar silencioso, sem abrir as janelas** → bloco 7,
  `APLICATIVOS_VISIVEIS = False`.

---

## 🚑 Resolução de problemas

- **`pywin32 nao instalado`** → `pip install pywin32`.
- **`Invalid class string` ao abrir Photoshop/Corel** → abra o
  programa uma vez manualmente antes (com o mesmo usuário do Windows
  que vai rodar o script).
- **CorelDRAW lento na primeira abertura** → normal; o COM aquece
  na segunda chamada em diante.
- **Arquivo `FORA_PROPORCAO_…` reaparecendo na lista** → não
  reaparece; o script ignora arquivos com esse prefixo.
