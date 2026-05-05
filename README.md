# Vídeo Institucional — Anclivepa RJ

Projeto de vídeo institucional para a **Anclivepa RJ — Faculdade**, focado na pós-graduação prática em Medicina Veterinária. Desenvolvido com **Remotion + React + TypeScript**.

---

## Especificações do vídeo

| Item         | Valor              |
| ------------ | ------------------ |
| Resolução    | 1080 × 1920 (9:16) |
| FPS          | 30                 |
| Duração      | ~52 segundos       |
| Codec        | H.264 (MP4)        |

---

## Instalação

```bash
# Instalar dependências
npm install

# Abrir o Remotion Studio (preview no navegador)
npm start

# Renderizar o vídeo final
npm run render

# Renderizar em alta qualidade
npm run render:hq
```

---

## Estrutura do projeto

```
├── src/
│   ├── index.ts              → Ponto de entrada Remotion
│   ├── Root.tsx              → Registro da composição
│   ├── Video.tsx             → Sequência principal (8 cenas)
│   ├── constants.ts          → Cores, durações, dimensões
│   ├── components/
│   │   ├── AnimatedText.tsx  → Texto com animação de entrada
│   │   ├── SceneWrapper.tsx  → Wrapper de cena com fade in/out
│   │   ├── MediaBackground.tsx → Fundo com imagem/vídeo ou gradiente
│   │   ├── Logo.tsx          → Componente do logo
│   │   └── CTABlock.tsx      → Bloco de chamada para ação
│   └── scenes/
│       ├── Scene01Abertura.tsx
│       ├── Scene02Problema.tsx
│       ├── Scene03Cirurgia.tsx
│       ├── Scene04Cardiologia.tsx
│       ├── Scene05Oftalmologia.tsx
│       ├── Scene06Pratica.tsx
│       ├── Scene07Diferencial.tsx
│       └── Scene08CTA.tsx
└── assets/
    ├── logo/         → Logo da Anclivepa RJ
    ├── fotos/        → Fotos das aulas/ambiente
    ├── videos/       → Vídeos de apoio das cenas
    └── audio/        → Trilha sonora e narração
```

---

## Como adicionar os arquivos reais

### Logo

1. Coloque o arquivo em `/assets/logo/logo.png`
2. No componente `src/components/Logo.tsx`, substitua o bloco `<LogoPlaceholder>` por:

```tsx
<Img src={staticFile("logo/logo.png")} style={{ width: size, height: "auto" }} />
```

---

### Fotos de apoio

Coloque os arquivos conforme a tabela abaixo e descomente a linha `imageSrc` no arquivo de cena correspondente:

| Arquivo                 | Cena                            |
| ----------------------- | ------------------------------- |
| `fotos/foto-01.jpg`     | Scene01Abertura — foto abertura |
| `fotos/foto-02.jpg`     | Scene02Problema — aula prática  |
| `fotos/foto-03.jpg`     | Scene04Cardiologia — estetoscópio |
| `fotos/foto-04.jpg`     | Scene05Oftalmologia — exame ocular |
| `fotos/foto-05.jpg`     | Scene06Pratica — alunos praticando |

Exemplo (em `Scene01Abertura.tsx`):

```tsx
<MediaBackground
  gradient={GRADIENTS.s1}
  imageSrc="fotos/foto-01.jpg"   // ← descomente esta linha
/>
```

---

### Vídeos de apoio

| Arquivo                 | Cena                                  |
| ----------------------- | ------------------------------------- |
| `videos/video-01.mp4`   | Scene03Cirurgia — aula de cirurgia    |
| `videos/video-02.mp4`   | Scene06Pratica — prática guiada       |

Exemplo (em `Scene03Cirurgia.tsx`):

```tsx
<MediaBackground
  gradient={GRADIENTS.s3}
  videoSrc="videos/video-01.mp4"   // ← descomente esta linha
/>
```

---

### Trilha sonora

1. Coloque o arquivo em `/assets/audio/trilha.mp3`
2. Em `src/Video.tsx`, descomente a linha:

```tsx
<Audio src={staticFile("audio/trilha.mp3")} volume={0.35} />
```

Ajuste o `volume` conforme necessário (0 = mudo, 1 = volume máximo).

---

## Como editar textos

Todos os textos de cada cena estão nos arquivos `src/scenes/Scene0X*.tsx`. Basta abrir o arquivo da cena e editar as strings dentro dos componentes `<AnimatedText>` e `<CTABlock>`.

Textos do CTA final (telefone, endereço, etc.) estão em `src/components/CTABlock.tsx`.

---

## Como ajustar duração das cenas

Em `src/constants.ts`, altere o valor de `DURATIONS` para cada cena (valores em frames a 30fps):

```ts
export const DURATIONS = {
  s1: 150,  // 5s
  s2: 180,  // 6s
  // ...
};
```

---

## Paleta de cores

| Nome       | Hex       | Uso                        |
| ---------- | --------- | -------------------------- |
| bgDark     | `#0A1628` | Fundo principal            |
| gold       | `#C9A84C` | Destaque, títulos          |
| goldLight  | `#E8C97A` | Hover / detalhes           |
| white      | `#FFFFFF` | Texto principal            |
| offWhite   | `#F0EDE8` | Texto secundário           |
| gray       | `#A0A8B8` | Texto suave / subtítulos   |

Todas as cores estão centralizadas em `src/constants.ts`.

---

## Renderização

```bash
# Renderização padrão
npm run render
# Saída: out/video.mp4

# Renderização em alta qualidade (CRF 12)
npm run render:hq
# Saída: out/video-hq.mp4
```

> O arquivo de saída será salvo na pasta `out/`. Ela é ignorada pelo `.gitignore`.
