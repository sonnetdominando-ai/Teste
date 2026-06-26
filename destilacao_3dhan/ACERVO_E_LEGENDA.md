# DESTILAÇÃO 3DHAN — Artefatos 2, 3 e 4 + Conferência de Cobertura

Obra destilada: **Everett M. Rogers — *Diffusion of Innovations* (5ª ed., Free Press, 2003)** · tipo: LIVRO (síntese acadêmica fundacional).
Data da destilação: **2026-06-26**.

---

## ARTEFATO 2 — COFRE DE ESQUELETO/VOZ (.md)
**Nenhum nesta obra.** Rogers é um tratado teórico-empírico de síntese; não contém beat sheets, arcos de roteiro ou few-shots de voz a extrair para `knowledge/REFERENCIAS_<nó>.md`.

---

## ARTEFATO 3 — LINHA DO ACERVO

```
★★★★★ Everett M. Rogers — Diffusion of Innovations (5ª ed., 2003) [tipo: LIVRO]
      → viralidade_difusao.xml (VIR-S01..S56) · modelos_output.xml (GAB-S01..S03)
      [2026-06-26] [renumerar]
```

Notas do acervo:
- Obra canônica e fonte-âncora do domínio **VIR** (viralidade_difusao.xml), até aqui VAZIO. Rogers é nomeado no contrato como autor-alvo de VIR (ao lado de Berger, Salganik, Goel).
- Tier do livro: **N2** (autoridade que sintetiza 5.200+ estudos). Mecanismos sustentados por estudos primários receberam `<fonte_primaria tier="N1">` (Ryan & Gross 1943; Coleman/Katz/Menzel 1966; Lazarsfeld et al. 1944; Granovetter 1973/1978; Bass 1969; RCTs de líderes de opinião; Havens & Flinn 1974; etc.).

---

## ARTEFATO 4 — DELTA DA LEGENDA (por domínio tocado)

```
VIR: +56 unidades — fonte: Everett M. Rogers (Diffusion of Innovations, 5ª ed.)
GAB:  +3 unidades — fonte: Everett M. Rogers (Diffusion of Innovations, 5ª ed.)
```

---

## CONFERÊNCIA DE COBERTURA (obrigatória)

- **Manifesto (scratchpad_phd, passo 7): 59 candidatos.**
- **Unidades gravadas: 59**, distribuídas em **3 arquivos staging**:
  - `diffusion_of_innovations_rogers_staging_parte1.xml` — 20 unidades (VIR-S01..S20)
  - `diffusion_of_innovations_rogers_staging_parte2.xml` — 20 unidades (VIR-S21..S40)
  - `diffusion_of_innovations_rogers_staging_parte3.xml` — 19 unidades (VIR-S41..S56 + GAB-S01..S03)
- **59 candidatos do manifesto = 59 unidades gravadas nos 3 arquivos.** Bate unidade a unidade. Zero truncamento.
- IDs de staging contíguos e únicos (VIR-S01..S56; GAB-S01..S03), cada bloco-alvo com comentário de renumeração para a INGESTÃO.
- Todos os 3 arquivos validados como XML bem-formado.
- Distribuição de tipo: 45 `principio`, 11 `modelo_mental`, 3 `gabarito`. Todo `principio` tem `<mecanismo>` causal; todo GAB tem `<no_alvo>` e `instancia_de` apontando à lei VIR de fundo.

---

## OBSERVAÇÕES PARA A INGESTÃO (conta integrada / MCP)
1. Renumerar VIR-S## e GAB-S## a partir do último ID real de cada domínio no Cérebro vivo.
2. Deduplicar/merge contra unidades VIR pré-existentes (o domínio estava vazio; esperar poucas colisões, exceto possíveis sobreposições com futuras destilações de Berger/Heath sobre boca-a-boca, massa crítica e curva de adoção).
3. As relações internas (`alvo="VIR-S##"`/`"GAB-S##"`) usam ids de staging — reapontar para os ids reais após renumeração.
4. Esta é EXTRAÇÃO PURA — nenhum HTML gerado. O guia visual é prompt atômico separado (`docs/PROMPT_GERAR_GUIA_HTML.md`), só sob pedido, após a cobertura.
