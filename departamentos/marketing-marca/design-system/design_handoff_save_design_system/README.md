# Handoff · Save Design System v0.5

## Overview
Save Co. é uma consultoria brasileira de recuperação tributária, gestão de passivos, planejamento patrimonial, monetização de ativos e certificação digital. Este pacote é o **design system completo** para os produtos digitais da Save Co.

## About the Design Files
Os arquivos HTML neste pacote são **referências de design** — protótipos navegáveis que mostram look-and-feel e comportamento pretendido, **não código de produção para ser copiado diretamente**. A tarefa do dev é **recriar estes designs no codebase alvo** (React, Vue, Swift, etc.) usando os padrões estabelecidos. Se não houver codebase, recomendamos: **Next.js + Tailwind + shadcn/ui + Framer Motion**.

## Fidelity
**High-fidelity (hifi)** — mockups pixel-perfect com cores finais, tipografia, espaçamento e interações documentadas.

## Modos de superfície (3)
| Modo | Quando usar |
|---|---|
| **A · Dark-first** | Produtos analíticos, dashboards de IA, monitoramento contínuo |
| **B · Híbrido** ★ recomendado | Módulos operacionais (casos, clientes, financeiro), formulários longos, tabelas densas |
| **C · Light-only** | Materiais públicos: landing, relatórios PDF, documentos para clientes |

Detalhes em `Save Light Surface.html`.

## Screens / Views

1. **Design System Principal** (`Design System Save.html`) — 23 seções, referência mestra
2. **Lista de casos** (Dashboard Screens · screen 01) — sidebar dark · breadcrumb · KPI grid 4-col · filter bar · tabela densa
3. **Detalhe do caso** (Dashboard Screens · screen 02) — timeline + stepper + IA contextual · grid 1.5fr+1fr
4. **Perfil do cliente** (Dashboard Screens · screen 03) — agregação de casos · profile-head + distribuição
5. **IA conversacional** (Dashboard Screens · screen 04) — analista júnior, não chatbot · stream de mensagens
6. **Mobile** (Mobile and Data Viz) — 3 telas iPhone 14 Pro · bottom nav · hit target ≥ 44×44
7. **Light workspace** (Light Surface) — padrão híbrido: sidebar dark + topbar branca com ⌘K + workspace claro
8. **Components Library** — 30 componentes documentados

## Motion tokens
| Token | Valor | Uso |
|---|---|---|
| --d-hover | 120ms | Botões, links |
| --d-expand | 180ms | Accordion, dropdown |
| --d-modal | 240ms | Modal, drawer |
| --d-page | 300ms | Rota |
| --ease | cubic-bezier(0.4, 0, 0.2, 1) | Curva única |

## Estados obrigatórios
default · hover · focus (halo gold 3px) · active · disabled · loading

## Navegação por teclado (obrigatório)
- Tab/Shift+Tab segue ordem visual · Enter/Space ativa · Esc fecha overlay
- ⌘K / Ctrl+K abre command palette
- Modal precisa de trap-focus

## State management sugerido
- React Query / TanStack Query (data fetching)
- Zustand ou Jotai (state global)
- React Hook Form + Zod (validação)

## Design Tokens

### Dark mode (padrão)
```
--bg-primary:#000000  --bg-secondary:#111111  --bg-card:#171717  --bg-elevated:#1E1E1E
--border:#2A2A2A
--text-primary:#F5F5F5  --text-secondary:#A1A1A1  --text-tertiary:#6B6B6B
--gold:#F3CD60  (única cor cromática)
--success:#44C653  --warning:#E8B34A  --error:#D64545  --info:#3065D6
```

### Light mode (workspace híbrido)
```
--l-bg:#F6F7F9  --l-card:#FFFFFF  --l-border:#E6E8EC
--l-text:#0F1115  --l-text-2:#4A4F58  --l-text-3:#838892
--gold-deep:#B58A1F  (gold AA-safe para texto)
--success:#1E8E3E  --warning:#B5790F  --error:#C5221F  --info:#1A56DB
```

### Pareamento dark ↔ light
| Papel | Dark | Light |
|---|---|---|
| bg-primary | #000000 | #F6F7F9 |
| bg-card | #171717 | #FFFFFF |
| text-primary | #F5F5F5 | #0F1115 |
| text-secondary | #A1A1A1 | #4A4F58 |
| border | #2A2A2A | #E6E8EC |
| gold (texto) | #F3CD60 | #B58A1F |

### Espaçamento (base 4)
4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 / 128

### Raios
4 / 8 / 12 / 16 / 24 · nunca > 24

### Tipografia
- **IBM Plex Sans** (300/400/500/600/700) — display, UI, body
- **IBM Plex Mono** (400/500) — tokens, números, IDs, eyebrows

### Tokens em formato dev
Veja `Save Tokens Apps and A11y.html` para CSS vars, JSON W3C, Tailwind config e TypeScript.

## Acessibilidade (WCAG 2.2 AA)

**Dark mode:**
- text-primary sobre bg-primary: **19.42:1** ✓ AAA
- gold (#F3CD60) sobre bg-primary: **13.83:1** ✓ AAA
- info (#3065D6): use #6E92E8 para texto

**Light mode:**
- text (#0F1115) sobre #F6F7F9: **19.3:1** ✓ AAA
- gold-deep (#B58A1F) sobre branco: **4.5:1** ✓ AA — usar sempre para texto gold em light
- gold puro (#F3CD60) só em fundos/badges em light mode

Foco visível obrigatório · suporte a prefers-reduced-motion.

## Assets

### Logo Save Co.
13 PNGs transparentes (4501×4501) em `/logos/`:
- Mista (lockup): original_white/dark · pb_white/dark · mono_dark_on_gold
- Nominal (wordmark): white · dark
- Símbolo: gold · white · dark · original · outline_gold · outline_white

### Iconografia
SVGs inline nas refs são placeholders. **Recomendamos Lucide React** (`pnpm add lucide-react`).

### Tipografia
```html
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

## Files

| Arquivo | Conteúdo |
|---|---|
| Design System Save.html | Documento mestre (23 seções + 5 extras) |
| Save Components Library.html | 30 componentes UI |
| Save Dashboard Screens.html | 4 telas-canônicas |
| Save Mobile and Data Viz.html | 3 mobile + 6 gráficos |
| Save Tokens Apps and A11y.html | Tokens × 4 formatos + aplicações + WCAG |
| Save Light Surface.html | Modo híbrido + tokens light |
| logos/ | 13 PNGs Save Co. |

## Stack recomendada
**Web**: Next.js · Tailwind · shadcn/ui · Framer Motion · TanStack Query · RHF+Zod
**Mobile**: React Native · NativeWind
**Docs**: Storybook

## Princípios não-negociáveis
1. **Dark-first** é o default. Light só em híbrido ou materiais públicos.
2. **Uma cor cromática** — gold reservado a destaque. Em light: gold-deep (#B58A1F) para texto.
3. **Densidade alta** — Save é B2B operacional. Tabelas, KPIs, listas densas > minimalismo vazio.
4. **IA é executiva** — nunca chatbot, mascote, emoji, "olá! como posso ajudar?".
5. **Cor com função** — nunca cor sozinha como sinal.
6. **44×44 mínimo** mobile · WCAG AA · trap-focus em modais.
7. **Marca central é Save Co.** — não criar sub-produtos fictícios. Domínios reais: recuperação tributária, gestão de passivos, holding, monetização de ativos, certificação digital.

---
Save Co. · Design System v0.5 · Marketing / Design System · 21 mai 2026
