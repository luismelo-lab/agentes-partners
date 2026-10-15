# Ativação das integrações (Office, GLPI e leitura de arquivos do HubSpot)
Quando a TI liberar, siga a ordem. Cada passo testa antes de ligar: se o teste falhar, nada muda.

## 1. Cole os acessos no `~/agentes-partners/.env` (só você ou a TI)
Uma por linha, no formato `NOME=valor`. Os agentes nunca leem nem mostram esse arquivo: só o código usa.
| Integração | O que a TI entrega | Linhas no .env |
|---|---|---|
| Office (Microsoft Graph) | Registro do aplicativo no Entra ID com Mail.ReadWrite e Mail.Send restritos à caixa da área | `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`, `AGENTES_CAIXA` (e-mail da caixa) |
| GLPI | Cliente OAuth, fluxo "authorization code", redirect `http://127.0.0.1:8765/glpi`, escopos api e user | `GLPI_CLIENT_ID`, `GLPI_CLIENT_SECRET` |
| HubSpot | Escopo **files** (leitura) no aplicativo privado dos agentes | nada: o token atual ganha o escopo |

## 2. Verifique (só leitura, nada é enviado nem aberto)
```bash
~/agentes-partners/bin/partners integracoes verificar
```

## 3. Ligue, uma por vez
**Office:** envia um e-mail de teste só para você. Se chegar, liga o e-mail e tira a pausa:
```bash
~/agentes-partners/bin/partners integracoes ligar email
```

**GLPI:** antes, cada pessoa autoriza uma vez. Ela entra no GLPI com a própria senha e clica em Autorizar; a senha não passa pelos agentes.
```bash
python3 ~/agentes-partners/lib/glpi.py autorizar luis
```
Depois rode o mesmo comando para daniela, geovana e jenifer, e então:
```bash
~/agentes-partners/bin/partners integracoes ligar glpi
```
O chamado continua só abrindo depois de "Aprovar e abrir no GLPI" no painel.

**Pareceres do HubSpot:** lê em segundo plano os cerca de 2.241 pareceres que estavam esperando:
```bash
~/agentes-partners/bin/partners integracoes ligar pareceres
```

## 4. Confira no dia seguinte
```bash
~/agentes-partners/bin/partners teste
```
Mostra a qualidade das entregas dos últimos 7 dias (meta: 100% de conformidade).
