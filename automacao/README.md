# Automação de Fechamento

Roteiro em Python (Windows) que processa arquivos enviados pelo cliente,
abre no Photoshop ou no CorelDRAW de acordo com a extensão, confere se a
dimensão do arquivo bate com o nome e, se estiver correto, gera o
arquivo final de produção na subpasta `Saida`:

- Photoshop → **TIF** para impressão.
- CorelDRAW → **CDR** para corte em router / corte e contorno.

### Regra de DPI do TIF

| Lado maior   | DPI  |
|--------------|-----:|
| até 60 cm    | 300  |
| acima de 60 cm | 100 |

## Convenção de nome

```
<quantidade>x_<produto>_<largura>x<altura>.<ext>
```

Exemplos:

| Arquivo                            | Quantidade | Produto      | L × A (cm) | Abre em    |
|------------------------------------|-----------:|--------------|-----------:|------------|
| `1x_vinil_fosco_100x100.pdf`       | 1          | vinil_fosco  | 100 × 100  | Photoshop  |
| `5x_lona_banner_150x80.pdf`        | 5          | lona_banner  | 150 × 80   | Photoshop  |
| `1x_adesivo_recorte_50x30.cdr`     | 1          | adesivo_rec. | 50 × 30    | CorelDRAW  |
| `2x_logo_corte_contorno_40x40.eps` | 2          | logo…        | 40 × 40    | CorelDRAW  |

Medidas sempre em centímetros.

Roteamento por extensão:

- `.pdf` → **Photoshop**
- `.cdr`, `.eps`, `.ai` → **CorelDRAW**

## O que o script faz

1. Lê todos os arquivos da pasta raiz (padrão `C:\2026\Fechamento`).
2. Extrai do nome a quantidade, o produto e a dimensão esperada.
3. Abre o arquivo no programa correto.
4. Compara a dimensão real do documento com a do nome
   (tolerância de **1 mm**).
5. **Se bater** → gera o arquivo final em `C:\2026\Fechamento\Saida\`
   (TIF para PDFs no Photoshop, CDR para CDR/EPS/AI no CorelDRAW)
   e deixa o arquivo aberto para você terminar a arte.
6. **Se NÃO bater** → fecha o documento sem salvar e renomeia o
   original com o prefixo `FORA_PROPORCAO_real_<L>x<A>_…`.
   O arquivo nunca é redimensionado.

## Instalação (Windows)

1. Instale Python 3.10+ ([python.org](https://www.python.org/downloads/)).
2. Em um Prompt de Comando:
   ```bat
   pip install pywin32
   ```
3. Copie esta pasta `automacao\` para um lugar fixo (ex.: `C:\automacao\`).

## Uso

Forma 1 — clique duplo em `processar.bat`. Ele processa tudo que estiver
em `C:\2026\Fechamento`.

Forma 2 — pelo terminal:

```bat
python fechamento.py                                   :: pasta padrao
python fechamento.py "D:\OutroDisco\Fechamento"        :: outra pasta
python fechamento.py --arquivo "C:\...\1x_vinil_fosco_100x100.pdf"
```

## Ajustes rápidos

Abra `fechamento.py` e edite no topo:

- `RAIZ_PADRAO`     — pasta monitorada.
- `SUBPASTA_SAIDA`  — onde caem os arquivos finais (padrão `Saida`).
- `TOLERANCIA_CM`   — folga aceita na conferência (padrão `0.1` cm = 1 mm).
- `LIMITE_DPI_CM`   — corte para mudar o DPI do TIF (padrão `60` cm).
- `DPI_PEQUENO`     — DPI usado abaixo do limite (padrão `300`).
- `DPI_GRANDE`      — DPI usado acima do limite (padrão `100`).
- No bloco do Photoshop, o modo de cor está em **CMYK** (`Mode = 3`).
  Troque para `2` para abrir em RGB.

## Resolução de problemas

- **`pywin32 nao instalado`** → rode `pip install pywin32`.
- **`Invalid class string`** ao chamar `Dispatch("Photoshop.Application")`
  → o Photoshop não está instalado ou foi instalado por outro usuário.
  Abra o Photoshop uma vez manualmente como o mesmo usuário antes de
  rodar o script.
- **CorelDRAW não responde** → abra o Corel uma vez antes; a primeira
  abertura por COM costuma ser lenta.
- Arquivo `FORA_PROPORCAO_…` reaparecendo na lista? Não reaparece —
  o script ignora arquivos que já começam com esse prefixo.
