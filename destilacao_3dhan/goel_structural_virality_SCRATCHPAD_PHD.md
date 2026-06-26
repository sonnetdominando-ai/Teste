<scratchpad_phd>

# DESTILAÇÃO 3DHAN — Goel, Anderson, Hofman & Watts, "The Structural Virality of Online Diffusion"

## 0. INTEGRIDADE (prova de acesso à fonte)
- **Tipo:** ARTIGO CIENTÍFICO revisado por pares → tier **N1** de ofício.
- **Autores:** Sharad Goel, Ashton Anderson (Stanford); Jake Hofman, Duncan J. Watts (Microsoft Research).
- **Periódico:** *Management Science* 62(1), janeiro 2016, pp. 180–196. ISSN 0025-1909 / 1526-5501.
- **DOI:** 10.1287/mnsc.2015.2158. Recebido ago/2013; aceito nov/2014 (Lorin Hitt, editor); publicado online jul/2015. © INFORMS.
- **Seções enxergadas no PDF (18 págs):** Abstract; §1 Introduction; §2 Defining Structural Virality; §3 Data and Methods; §4 Results (4.1 Structural Diversity, 4.2 [Fig.4, por domínio], 4.3 Relationship Between Popularity and Structural Virality); §5 Theoretical Modeling; §6 Discussion; Appendix A (Computing Structural Virality / índice de Wiener, Lema 1, Teorema 2, Algoritmo 1); Appendix B (Alternative Measures); Appendix C (Tree Construction Method); Appendix D (Off-Channel Diffusion); References.
- **NOTA DE INTEGRIDADE (anti-fabricação):** as páginas 8 e 12 do PDF extraído são páginas-figura (Figura 4 — distribuição de virality por domínio; Figura 7 — resultados das simulações A/B/C) cujo texto embutido NÃO renderizou no extrator. Não fabriquei conteúdo delas: usei apenas o que o texto corrido referencia explicitamente sobre essas figuras (Fig.4 citada na p.9 — petições mais virais; Fig.7 citada nas pp.11–13 — taxa de popularidade ~1/1000, virality média ~5, correlação na faixa observada). Onde a figura era a única fonte de um número, não destilei o número.

## 1. TESE CENTRAL
"Viral" tem dois sentidos que a cultura funde: ficar POPULAR (tamanho) e ficar popular POR CONTÁGIO interpessoal multigeracional (estrutura). Os autores criam uma métrica estrutural contínua — **virality estrutural ν(T) = distância média entre todos os pares de nós da árvore de difusão (índice de Wiener)** — e a aplicam a ~1 bilhão de eventos de difusão no Twitter. Achado: eventos grandes exibem DIVERSIDADE estrutural enorme (de broadcast puro a contágio profundo) a qualquer tamanho fixo; a virality estrutural é tipicamente BAIXA e quase NÃO se correlaciona com tamanho; logo a popularidade é governada sobretudo pelo TAMANHO DO MAIOR BROADCAST, não por cadeia viral. Um modelo de contágio simples, de baixa infecciosidade (subcrítico, r≈0.5) em rede scale-free reproduz quase tudo — exceto a diversidade estrutural a tamanho fixo, que fica em aberto.

## 2. COBERTURA (prova de leitura integral)
Varri abstract → §1 motivação/contribuições → §2 definição e desiderata da métrica → §3 dados (Twitter, 4 domínios) e construção de árvore → §4 resultados (diversidade, por-domínio, popularidade×virality) → §5 modelagem (4 modelos SIR/Bass de complexidade crescente) → §6 discussão/limitações → Apêndices A–D (algoritmo de Wiener, métricas alternativas, reconstrução de árvore com validação 95%, controle off-channel via hashtags longas) → referências. Método e resultados revistos linha a linha. Fonte parcial: nenhuma — único faltante é o TEXTO embutido das Figs.4 e 7 (declarado acima); a substância dessas figuras vem das referências em texto, não inventada.

## 3. FRONTEIRA [C]/[V] (+ balizas estatísticas)
Quase tudo é **[C]** empírico forte (N1): n ≈ 1,2 bilhão de adoções; 622M peças únicas; 219.855 cascatas com ≥100 nós; >99% das cascatas morrem em 1 geração; tamanho médio 1,3; taxa de popularidade ~1/1000, "viral hit" ~1/milhão; correlação tamanho×ν: news 0.2, petições 0.04, fotos/vídeos ≈0; ν mediano: fotos/vídeos <3, petições 7–8, news 3→<8; 4 métricas alternativas com corr. de posto ≥0.73; modelo: 25M nós, ~1bi simulações/parâmetro, >100bi totais; melhor ajuste scale-free α≈2.3, r≈0.5; reconstrução de árvore 95% acurácia (retweet oficial 65%, repost creditado 10%, não-creditado 25% @ 79%); controle off-channel: 58.000 cascatas de hashtags longas, resultado igual.
- **[V] (interpretação do autor, não medida):** a EXPLICAÇÃO causal de por que petições/news são mais virais — "escassez de grandes canais de broadcast" — é declarada pelos próprios autores como especulação ("we can only speculate about why"). Marquei na unidade VIR-S08 que o ACHADO é [C] mas a explicação é [V] de menor confiança.
- **[C] CONTROVERSO / em aberto:** nenhum modelo reproduz a diversidade de ν a tamanho fixo (resultado negativo honesto) → VIR-S13.

## 4. NATUREZA (LEI / MOLDE / ESQUELETO) + arquivo-alvo
- **LEIS de difusão/contágio/viralidade** → **VIR** (viralidade_difusao.xml). Núcleo da obra. 13 unidades (principio/modelo_mental).
- **LEIS de método/epistemologia** (desenho de métrica, medir o observável sem modelo, amostragem de cauda, robustez à operacionalização, falsear×provar modelo) → **EPI** (epistemologia_metodo_cientifico.xml). 5 unidades.
- **MÉTODO de validação empírica** (reconstrução de cascata com back-test; controle natural contra confound) → **EXP** (experimentacao_validacao.xml). 2 unidades.
- **MOLDE/GAB:** nenhum — a obra não entrega receita de output para os nós 3DHAN; o algoritmo de Wiener e a reconstrução de árvore são metodologia de pesquisa (EXP/EPI), não gabarito de conteúdo.
- **ESQUELETO/VOZ (Artefato 2):** nenhum — paper acadêmico, sem beat sheet/arco/few-shot.

## 5. CAÇA À PROFUNDIDADE (mecanismo / condições / inversão / tensões / replicação)
- **Métrica ν:** mecanismo = média das distâncias de menor caminho entre pares; broadcast/estrela ≈2 invariante ao tamanho, k-ária cresce com a altura. CONDIÇÃO: precisa da árvore reconstruída (quem-adotou-de-quem); com só agregados a estrutura é não-identificável. Caso patológico (duas estrelas + caminho longo) pontua alto sem ser viral — raro empiricamente.
- **Popularidade × virality:** REVERTE? Buscado ativamente — os autores enfatizam que NÃO há domínio onde tamanho implique alta virality; nem o maior evento (≥10.000) foge disso. Inversão só aparece por DOMÍNIO (petições/news sobem ν) → tensão com disponibilidade de canal.
- **Curva-S / forma / timescale:** mecanismo da inversão = broadcast satura mercado e gera a MESMA sigmoide do contágio; logo forma e velocidade da curva agregada NÃO identificam estrutura (Fig.3: curvas idênticas, estruturas opostas).
- **Modelo:** por que ER falha e scale-free funciona? Em rede homogênea cascata grande TEM de ser profunda → trava correlação tamanho×ν alta; só a heterogeneidade (hubs) quebra isso (contágio fraco "resgatado" ao encontrar hub de altíssimo grau → grande-mas-raso). Tipping point colapsa: em scale-free o limiar epidêmico → 0 (regime subcrítico some). Replicação: o ajuste r≈0.5 é coerente com estimativas subcríticas prévias (Leskovec SIS r≈0.14 em blogs; chain letters, Golub & Jackson 2010); LIMITE: diversidade de ν a tamanho fixo NÃO replica.
- **Epistemologia:** replicar dados não prova mecanismo (equifinalidade) — só permite ELIMINAR (ER eliminado); robustez a 4 métricas (≥0.73) blinda contra artefato de definição; amostragem de cauda exige base ordens de grandeza maior (1M de eventos prévios só viam cascatas pequenas).

## 6. EXTRAÇÃO MÁXIMA (sem deduplicar contra o Cérebro vivo)
Não vejo o Cérebro; uso ids provisórios por-obra (VIR-S01+, EPI-S01+, EXP-S01+), conforme o protocolo (renumeração/merge são da INGESTÃO). NOTA: a obra Rogers já neste folder usa VIR-S01..S63 — colisão por-obra é ESPERADA e resolvida na ingestão; mantive S01+ para esta obra para que as <relacao alvo="..."> internas do paper Goel fiquem auto-consistentes.

## 7. MANIFESTO DE COBERTURA (CONTRATO — 20 unidades)

### ALVO: viralidade_difusao.xml (VIR) — 13 unidades
1. VIR-S01 [modelo_mental] — Virality estrutural ν(T) = índice de Wiener (distância média entre pares na árvore).
2. VIR-S02 [modelo_mental] — Popularidade ≠ virality: tamanho e estrutura são ortogonais.
3. VIR-S03 [principio] — Popularidade é governada pelo MAIOR BROADCAST, não pela profundidade viral (ν baixo, corr.≈0).
4. VIR-S04 [principio] — Diversidade estrutural a tamanho fixo; sem tipping point, sem formas canônicas.
5. VIR-S05 [modelo_mental] — "Going viral" funde popularidade/velocidade com contágio; não se infere mecanismo do resultado.
6. VIR-S06 [principio] — Curva-S NÃO é prova de contágio (broadcast gera a mesma sigmoide).
7. VIR-S07 [principio] — Forma e timescale da curva de adoção não predizem a estrutura.
8. VIR-S08 [principio] — Virality mediada pela disponibilidade de canais de broadcast (efeito-domínio). [achado C; explicação V]
9. VIR-S09 [principio] — Difusão é majoritariamente subcrítica: cauda pesada, >99% morre em 1 geração.
10. VIR-S10 [principio] — Contágio de baixa infecciosidade em rede scale-free reproduz a empiria (sem supercrítico).
11. VIR-S11 [principio] — Heterogeneidade da rede (hubs scale-free), não variância de infecciosidade, faz o modelo ajustar; ER falha.
12. VIR-S12 [principio] — Em redes scale-free o limiar epidêmico (tipping point) colapsa a zero.
13. VIR-S13 [principio] — Nenhum mecanismo conhecido reproduz a DIVERSIDADE de ν a tamanho fixo (limite em aberto).

### ALVO: epistemologia_metodo_cientifico.xml (EPI) — 5 unidades
14. EPI-S01 [modelo_mental] — Construir métrica a partir de desiderata explícitos e rejeitar proxies que falham em casos patológicos.
15. EPI-S02 [modelo_mental] — Medir a estrutura observável independentemente do modelo gerador não observado.
16. EPI-S03 [principio] — Amostrar eventos raros de cauda exige base amostral ordens de grandeza maior.
17. EPI-S04 [principio] — Robustez à operacionalização: triangular o achado por métricas alternativas.
18. EPI-S05 [principio] — Modelo que replica os dados pode ser FALSEADO, nunca provado (equifinalidade).

### ALVO: experimentacao_validacao.xml (EXP) — 2 unidades
19. EXP-S01 [heuristica] — Reconstruir influência por exposição-mais-recente e validar contra subconjunto de verdade-base (95%).
20. EXP-S02 [heuristica] — Controle natural imune ao confound (hashtags longas) para testar viés (off-channel + homofilia).

**TOTAL = 20 unidades** (VIR 13 + EPI 5 + EXP 2), em **2 arquivos staging** (parte1 = VIR; parte2 = EPI+EXP).

</scratchpad_phd>
