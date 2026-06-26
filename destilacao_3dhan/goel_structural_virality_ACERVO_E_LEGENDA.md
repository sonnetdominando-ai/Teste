# DESTILAÇÃO 3DHAN — Artefatos 2, 3 e 4 + Conferência de Cobertura

Obra destilada: **Sharad Goel, Ashton Anderson, Jake Hofman & Duncan J. Watts — "The Structural Virality of Online Diffusion"** · *Management Science* 62(1):180–196 (2016) · DOI 10.1287/mnsc.2015.2158 · tipo: **ARTIGO CIENTÍFICO** (revisado por pares, INFORMS).
Data da destilação: **2026-06-26**.

---

## ARTEFATO 2 — COFRE DE ESQUELETO/VOZ (.md)
**Nenhum nesta obra.** Paper acadêmico de método/empiria; não contém beat sheets, arcos de roteiro ou few-shots de voz a extrair para `knowledge/REFERENCIAS_<nó>.md`. O Algoritmo 1 (índice de Wiener) e a reconstrução de árvore são metodologia de pesquisa (roteadas a EXP/EPI como unidades atômicas), não gabarito de output.

---

## ARTEFATO 3 — LINHA DO ACERVO

```
★★★★★ Goel, Anderson, Hofman & Watts — The Structural Virality of Online Diffusion (2016)
      [tipo: ARTIGO · Management Science 62(1):180-196 · DOI 10.1287/mnsc.2015.2158]
      → viralidade_difusao.xml (VIR-S01..S13)
      · epistemologia_metodo_cientifico.xml (EPI-S01..S05)
      · experimentacao_validacao.xml (EXP-S01..S02)
      [2026-06-26] [renumerar]
```

Notas do acervo:
- Fonte **N1 de ofício** (paper revisado por pares) — todas as unidades começam em N1. Mecanismos sustentados por estudos primários citados pela obra receberam `<fonte_primaria tier="N1">` (Wiener 1947; Barabási & Albert 1999; Pastor-Satorras & Vespignani 2001; Lloyd & May 2001; Van den Bulte & Lilien 2001; Goel et al. 2012; Liben-Nowell & Kleinberg 2008; Shalizi & Thomas 2011; Ijiri et al. 1977).
- **Obra-âncora do domínio VIR** nomeada no contrato 3DHAN (Goel listado ao lado de Berger, Salganik, Rogers). Complementa a destilação Rogers já no acervo: Rogers dá a TEORIA clássica da difusão (curva-S, líderes de opinião, atributos da inovação); Goel et al. dá a MEDIDA estrutural e o veredito empírico de bilhão-de-eventos (popularidade ≈ maior broadcast; tipping point dissolvido). Esperar sobreposição/tensão produtiva na ingestão (ex.: a curva-S de Rogers vs. VIR-S06 "curva-S não prova contágio").
- Balizas estatísticas-chave preservadas como `<condicoes>`: n≈1,2 bi adoções; 219.855 cascatas ≥100 nós; correlação tamanho×ν (news 0.2 / petições 0.04 / fotos-vídeos ≈0); melhor ajuste scale-free α≈2,3, r≈0,5; reconstrução 95%; controle off-channel 58k hashtags longas.
- **[V] declarado:** a explicação "disponibilidade de canal de broadcast" para o efeito-domínio (VIR-S08) é especulação dos próprios autores ("we can only speculate") — marcada na unidade como hipótese de menor confiança sobre achado [C].
- **Limite em aberto preservado (VIR-S13):** nenhum modelo reproduz a diversidade de ν a tamanho fixo — resultado negativo honesto, não descartado.

---

## ARTEFATO 4 — DELTA DA LEGENDA (por domínio tocado)

```
VIR: +13 unidades — fonte: Goel, Anderson, Hofman & Watts (Structural Virality, 2016)
EPI:  +5 unidades — fonte: Goel, Anderson, Hofman & Watts (Structural Virality, 2016)
EXP:  +2 unidades — fonte: Goel, Anderson, Hofman & Watts (Structural Virality, 2016)
```

---

## CONFERÊNCIA DE COBERTURA (obrigatória)

- **Manifesto (scratchpad_phd, passo 7): 20 candidatos.**
- **Unidades gravadas: 20**, distribuídas em **2 arquivos staging**:
  - `goel_structural_virality_staging_parte1.xml` — 13 unidades (VIR-S01..S13)
  - `goel_structural_virality_staging_parte2.xml` — 7 unidades (EPI-S01..S05 + EXP-S01..S02)
- **20 candidatos do manifesto = 20 unidades gravadas nos 2 arquivos.** Bate unidade a unidade. Zero truncamento.
- Distribuição de tipo: **13 `principio`**, **5 `modelo_mental`**, **2 `heuristica`** (ambas EXP). Todo `principio` tem `<mecanismo>` causal; nenhum GAB (a obra não entrega molde de output).
- Distribuição de tier: **20 unidades N1** (paper revisado por pares); `<fonte_primaria tier="N1">` adicionada onde a obra cita o estudo fundacional do mecanismo.
- IDs de staging contíguos e únicos por-obra (VIR-S01..S13; EPI-S01..S05; EXP-S01..S02); cada bloco-alvo com comentário de renumeração para a INGESTÃO.
- Ambos os arquivos validados como XML bem-formado.
- **Caça à profundidade:** `reverte_quando` buscado ativamente — presente onde o texto sustenta (VIR-S01 caso patológico; VIR-S05 cascata reconstruída; VIR-S10/S11 rede ER inverte o ajuste). Onde os autores afirmam NÃO haver inversão (tamanho→virality), isso foi registrado explicitamente em vez de fabricar uma.
- **Nota de integridade (anti-fabricação):** Figuras 4 e 7 (páginas-imagem 8 e 12 do PDF) não renderizaram texto no extrator; nenhum número exclusivo dessas figuras foi destilado por inferência — só o que o texto corrido referencia. Declarado no scratchpad.

---

## OBSERVAÇÕES PARA A INGESTÃO (conta integrada / MCP)
1. Renumerar VIR-S##, EPI-S## e EXP-S## a partir do último ID real de cada domínio no Cérebro vivo.
2. Os ids de staging VIR-S01..S13 **colidem por desenho** com VIR-S01..S63 da destilação Rogers neste mesmo folder — comportamento esperado do protocolo (staging por-obra). Deduplicar/merge na ingestão; checar especialmente a fronteira Rogers↔Goel (curva-S, líderes de opinião como hubs, massa crítica vs. tipping point).
3. As relações internas (`alvo="VIR-S##"`/`"EPI-S##"`/`"EXP-S##"`) usam ids de staging desta obra — reapontar para os ids reais após renumeração. Relações com `alvo=""` são elos a fonte externa/conceito (ex.: índice de Wiener, tradição tipping point) sem id-alvo no Cérebro.
4. Esta é EXTRAÇÃO PURA — nenhum HTML gerado. O guia visual é prompt atômico separado (`docs/PROMPT_GERAR_GUIA_HTML.md`), só sob pedido, após a cobertura.
