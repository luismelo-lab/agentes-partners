# Briefing · Guia do Parceiro (consulta durante a reunião) · Save Co.

**Pedido do Luis (gerente comercial Masters), 16/10/2026:** um segundo material, para o PARCEIRO (Master ou indicador da Save que acompanha a reunião com o cliente), com o direcionamento técnico de cada tese e de cada produto, TRADUZIDO para linguagem comercial, para ele consultar durante a reunião, e com a **quebra de objeção de cada tese e de cada produto**. Deve seguir as informações que o Luis já passou (fontes abaixo). Layout padrão da Save (preto, ouro, IBM Plex), uma ficha por página (1920×1080), pesquisável.

**Quem lê:** parceiro comercial (conhece o mercado e o cliente, não é tributarista). Em reunião, precisa achar a ficha em 10 segundos e dizer algo certo em 20. Por isso: frases curtas, concretas, sem juridiquês; cada termo técnico traz a tradução ("o que isso quer dizer para o dono da empresa"). Não é material para o cliente: pode ter ticket/remuneração (campo próprio marcado "não mostrar ao cliente") e sinais de quando NÃO oferecer.

**Fontes (leia por inteiro as que são da sua tarefa; as demais só se precisar):**
- Teses T01–T19, P01 Planejamento Tributário, P02 Planejamento Estratégico e visão geral (vias e espécies de pedido): `departamentos/tributario/catalogo-teses-save-completo.md` (fonte oficial, resumos do time técnico).
- Produtos e serviços (institucional, ecossistema, reunião de 13/10 com os produtos financeiros, regras de comunicação): `departamentos/produtos/fontes-produtos-guia-parceiro.md`. Detalhe da reunião: `/Users/luisfernandomelo/Library/CloudStorage/OneDrive-SAVECOMPANY/00 · Entrada/10-13 Reunião_ Gestão de Contas, Produtos Financeiros e Modelo Consultivo-Summary.md` (800 linhas; busque os tópicos).
- Pareceres de revisão (limites e erros já corrigidos; leia o que for da sua frente): `departamentos/tributario/entregas/2026-10-14-brasol-*.md` e `2026-10-15-brasol-revisao-deck-tributario.md`; `departamentos/juridico/entregas/2026-10-14-padrao-apresentacao-diagnostico-compliance.md` e `2026-10-15-brasol-revisao-deck-juridico.md`; `departamentos/tributario/aprendizados.md`, `radar-teses.md`; skill `~/.claude/skills/revisor-diagnostico/SKILL.md` (vetos V1–V15, matriz tese × perfil).
Tudo é pré-análise para validação de técnico/advogado humano. Para qualquer afirmação técnica além do que está nas fontes, pesquise fonte oficial (STF, STJ, Planalto, Receita) e cite; sem fonte: "não localizado". Não invente tema, artigo, valor ou prazo.

**Regras de conteúdo (inegociáveis):**
1. Siga as informações do Luis (catálogo e fontes). Onde elas divergirem das revisões tributária/jurídica de 14 e 15/10 (por exemplo: "insumo no atacado"; Aquisições; Tema 1.231; débito não impede crédito), escreva o que o catálogo diz E o cuidado da revisão na lista `cuidados`.
2. Sem promessa de resultado ou êxito; sem "garantido", "sem risco", "blindagem", "holding" (use "estruturação patrimonial"); crédito/antecipação/fundos são de instituições autorizadas, a Save estrutura e acompanha; ação judicial só por advogado habilitado; estatística de mercado não é dado Save; e-CAC só por procuração, nunca senha ou certificado; estimativa é preliminar.
3. Preço/ticket só no campo `remuneracao_interna`.
4. As respostas às objeções devem ser específicas da tese ou do produto (não genéricas), honestas (admitir o que é risco real e como a Save trata), em frases que o parceiro fale em voz alta, e terminar, quando couber, com uma pergunta ou próximo passo.
5. Português do Brasil, Acordo Ortográfico, sem travessão longo, sem emoji.

**Esquema de cada ficha (objeto JSON; todas as chaves obrigatórias; limites de caracteres são para o texto caber na página):**
```
{
 "id": "T01",
 "grupo": "Tese" ou "Produto",
 "familia": "PIS/COFINS" (rótulo curto, até 24),
 "nome": "até 62 caracteres",
 "selos": ["ADM", "5 anos", ...]  (1 a 3 itens, até 18 cada: via ADM/JUD/MSC/Consultivo, período, regime),
 "em_20_segundos": "como o parceiro explica ao dono, até 230 caracteres, linguagem comercial",
 "o_que_o_cliente_ganha": ["3 itens, até 90 cada"],
 "tecnico_traduzido": [ {"termo": "até 28", "tecnico": "o termo ou a norma, até 90", "comercial": "tradução em linguagem de dono de empresa, até 160"} ] (3 a 5 itens: fundamento, como funciona, base de prova, período, risco),
 "perfil_ideal": ["3 a 4 itens, até 80 cada"],
 "sinais_para_oferecer": ["3 itens, até 80 cada: o que o parceiro vê ou ouve no cliente"],
 "nao_oferecer_quando": ["2 a 3 itens, até 80 cada"],
 "perguntas_de_descoberta": ["3 itens, até 100 cada"],
 "documentos": ["3 a 5 itens, até 60 cada"],
 "objecoes": [ {"o": "a fala do cliente, até 90", "r": "resposta do parceiro, até 240"} ] (4 itens),
 "remuneracao_interna": "até 150 (ticket do catálogo; começa com 'Uso interno:')",
 "cuidados": ["1 a 3 itens, até 120 cada: compliance e limites técnicos"],
 "fonte": "até 130: de onde vem (ex.: catálogo T01; STF Tema 304; IN RFB 2.055/2021)"
}
```
**Entrega:** grave o(s) arquivo(s) JSON indicados na sua tarefa em `/Users/luisfernandomelo/agentes-partners/.claude/worktrees/diagnosticos-presentation-flow-309d5a/departamentos/tributario/guia-parceiro/conteudo/` (uma lista JSON de fichas). Valide com `python3 -c "import json;json.load(open(ARQ))"` e confira os limites de caracteres com um pequeno script (corrija o que passar). Na resposta final, informe só: quantas fichas, os 5 pontos que mais exigem validação humana e os caminhos.
