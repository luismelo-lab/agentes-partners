"""PRM Save v2 sobre a Central (docs/prm/v2/). Fase 1 em modo local (JSON em registro/prm/), Fase 2 na Azure (SQL).

As regras vivem aqui, uma vez só; as rotas HTTP (rotas.py) e as duas faces do site (web/prm.html) só as chamam.
  app.py           contêiner: repositório, parâmetros, relógio, trilha
  repositorio.py   dois adaptadores com a mesma interface: RepoJSON (Fase 1) e RepoSQL (Fase 2; testado com sqlite)
  identidade.py    autorização em 3 camadas: token → papel + escopo do escritório → dono da linha (404 fora do escopo)
  checagem.py      serviço único da raiz do CNPJ (U1) e regra única de cliente protegido (L14)
  registro.py, negocios.py, extrato.py, demandas.py, nivel.py   máquinas de estado dos módulos
  decisao.py       ação única `decidir` com trilha (U4)
  notificacoes.py  avisos no formato de lib/caixa.py (U3)
  auditoria.py     auditor único de todo texto que sai (U5)
"""
