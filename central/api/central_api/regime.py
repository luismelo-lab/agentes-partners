"""Consulta de regime tributário (Lucro Real) para o parceiro, só por APIs gratuitas.

Fontes, nesta ordem (as duas trazem o mesmo dado: a BrasilAPI usa a base do Minha Receita, então a segunda
é reserva de disponibilidade, não segunda opinião):
  1. Minha Receita  https://minhareceita.org/<cnpj>
  2. BrasilAPI      https://brasilapi.com.br/api/cnpj/v1/<cnpj>
O regime vem da ECF (campo regime_tributario, por ano) e a opção pelo Simples, da Receita. O regime da ECF é o do
ano-base: não é "o regime de hoje".

ATENÇÃO: cada consulta envia o CNPJ a um serviço de terceiros. Só liga com CENTRAL_API_EXTERNA=1 (a demo liga por
padrão, local). No piloto, depende do ok do Jurídico e da TI. Sem contrato nem SLA nas duas fontes.

Faixas: negocio_ativo | confirmado_real | provavel_real | nao_real | sem_dado | indisponivel | invalido.
A 1ª checagem é a base Save Company (negocio_ativo.py): empresa com negócio ativo não segue para as APIs. Negócio ativo,
índice ausente e tetos devolvem a MESMA mensagem neutra (faixa indisponivel); o motivo real só vai para o log e a trilha.
"""
import json, logging, math, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from .caminhos import dados as _dados, preparar_lib  # noqa: E402  (L5: caminhos por variável)
preparar_lib()
from cnpj import cnpj_valido, completar_cnpj  # noqa: E402
from . import negocio_ativo  # noqa: E402

log = logging.getLogger("central_api.regime")

BASE = os.path.expanduser(os.environ.get("CENTRAL_RECEITA") or str(_dados() / "dados-publicos/receita"))  # só a trilha de auditoria
LIMITE_LOTE = 20
LIMITE_DIA = int(os.environ.get("CENTRAL_LIMITE_DIA", "200"))
LIMITE_ATIVO = int(os.environ.get("CENTRAL_LIMITE_ATIVO", "10"))  # acertos "negócio ativo" por usuário por dia (anti-enumeração da base)
MSG_NEUTRA = negocio_ativo.MSG_NEUTRA
MAX_BYTES = 2_000_000     # resposta maior que isto é descartada (as APIs devolvem poucos KB)
MEMORIA_MAX = 2000
TETO_PRESUMIDO = 78_000_000  # Lei 9.718/1998, art. 13 e art. 14, I
TTL = 24 * 3600
TIMEOUT = 10
FONTES = [("Minha Receita", "https://minhareceita.org/%s"), ("BrasilAPI", "https://brasilapi.com.br/api/cnpj/v1/%s")]

_memoria = {}
_uso = {}
_ativos = {}
_lock = threading.Lock()  # a demo atende em várias threads: cache e contadores mudam sob esta trava


def _http(url):
    """(status, json|None). Status 0 = falha de rede ou tempo esgotado. Usa o curl, como o receita_cnpj.py: o Python
    da python.org no Mac não traz os certificados raiz e recusaria o HTTPS (a verificação não é desligada)."""
    try:
        r = subprocess.run(["curl", "-sS", "-m", str(TIMEOUT), "--proto", "=https", "--max-filesize", str(MAX_BYTES), "-A", "SaveCo-Central-Partners/1.0", "-H", "Accept: application/json",
                            "-w", "\n%{http_code}", url], capture_output=True, text=True, timeout=TIMEOUT + 5)
        if len(r.stdout) > MAX_BYTES + 16:
            return 0, None
        corpo, _, codigo = r.stdout.rpartition("\n")
        st = int(codigo or 0)
        return (st, json.loads(corpo)) if st == 200 else (st, None)
    except (subprocess.SubprocessError, ValueError, OSError):
        return 0, None


def _buscar(cnpj):
    """(dados|None, nome da fonte, motivo). Motivo: 'nao_encontrado' (alguma fonte disse 404) ou 'indisponivel'."""
    with _lock:
        visto = _memoria.get(cnpj)
    if visto and time.time() - visto[0] < TTL:
        return visto[1], visto[2], None
    nao_achou = False
    for nome, modelo in FONTES:
        st, dados = _http(modelo % cnpj)
        if st == 200 and isinstance(dados, dict):
            with _lock:
                if len(_memoria) >= MEMORIA_MAX:  # teto de memória: sai a entrada mais antiga
                    del _memoria[min(_memoria, key=lambda k: _memoria[k][0])]
                _memoria[cnpj] = (time.time(), dados, nome)
            return dados, nome, None
        nao_achou = nao_achou or st == 404
    return None, None, "nao_encontrado" if nao_achou else "indisponivel"


def _txt(v):
    return v if isinstance(v, str) else (str(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None)


def _ano(v):
    try:
        a = int(v)
    except (TypeError, ValueError):
        return None
    return a if 1990 <= a <= 2100 else None


def _flag(v):
    return v is True or (isinstance(v, str) and v.strip().lower() in ("true", "1", "sim"))


def _sanear(d):
    """Resposta da API com tipos garantidos (texto, número, lista): campo nulo ou de tipo estranho não derruba a consulta."""
    reg = []
    for x in d.get("regime_tributario") if isinstance(d.get("regime_tributario"), list) else []:
        if isinstance(x, dict) and _ano(x.get("ano")) and _txt(x.get("forma_de_tributacao")) and _txt(x.get("forma_de_tributacao")).strip():
            reg.append({"ano": _ano(x["ano"]), "forma_de_tributacao": _txt(x["forma_de_tributacao"]).strip()})
    sec = [{"codigo": _txt(x.get("codigo")), "descricao": _txt(x.get("descricao"))} for x in (d.get("cnaes_secundarios") if isinstance(d.get("cnaes_secundarios"), list) else []) if isinstance(x, dict)]
    cap = d.get("capital_social")
    try:
        cap = float(cap)
        cap = cap if math.isfinite(cap) else None
    except (TypeError, ValueError):
        cap = None
    out = {k: _txt(d.get(k)) for k in ("razao_social", "nome_fantasia", "cnae_fiscal", "cnae_fiscal_descricao", "data_inicio_atividade", "municipio", "uf",
                                         "porte", "natureza_juridica", "descricao_situacao_cadastral")}
    out.update(capital_social=cap, identificador_matriz_filial=_txt(d.get("identificador_matriz_filial")), cnaes_secundarios=sec, regime_tributario=reg,
               opcao_pelo_simples=_flag(d.get("opcao_pelo_simples")), opcao_pelo_mei=_flag(d.get("opcao_pelo_mei")))
    return out


def _regime(dados):
    """(formas no ano mais recente, ano). Vazio quando a ECF não trouxe nada."""
    lista = [x for x in (dados.get("regime_tributario") or []) if x.get("forma_de_tributacao")]
    if not lista:
        return set(), None
    ano = max(x.get("ano") or 0 for x in lista)
    return {x["forma_de_tributacao"].strip().upper() for x in lista if (x.get("ano") or 0) == ano}, ano or None


def _perfil(d):
    """Retrato da empresa para os agentes, só dado cadastral da pessoa jurídica: sem sócios (QSA), telefone, e-mail nem endereço."""
    sec = [{"codigo": x.get("codigo"), "descricao": x.get("descricao")} for x in (d.get("cnaes_secundarios") or [])[:12]]
    ecf = sorted(({"ano": x.get("ano"), "forma": x.get("forma_de_tributacao")} for x in (d.get("regime_tributario") or [])), key=lambda x: x["ano"] or 0)
    return {"razao": d.get("razao_social"), "fantasia": d.get("nome_fantasia") or None,
            "cnae": {"codigo": d.get("cnae_fiscal"), "descricao": d.get("cnae_fiscal_descricao")}, "cnaes_secundarios": sec,
            "capital_social": d.get("capital_social"), "inicio_atividade": d.get("data_inicio_atividade"), "municipio": d.get("municipio"),
            "uf": d.get("uf"), "porte": (d.get("porte") or "").title() or None, "natureza_juridica": d.get("natureza_juridica"),
            "matriz": str(d.get("identificador_matriz_filial")) == "1", "ecf": ecf}


def neutra(cnpj, motivo):
    """Resposta única para negócio ativo, índice ausente e tetos: o parceiro não distingue um do outro. O motivo real
    fica em `_motivo` (só para o log e a trilha; `publico` o retira antes de qualquer resposta)."""
    log.info("consulta neutra: motivo=%s", motivo)
    return {"cnpj": cnpj, "faixa": "indisponivel", "titulo": MSG_NEUTRA, "detalhe": "", "fonte": None, "ano_base": None, "empresa": None, "_motivo": motivo}


def publico(r):
    """O resultado sem campos internos (chaves que começam com _)."""
    return {k: v for k, v in r.items() if not str(k).startswith("_")}


# Fonte local de teste (modo local do PRM, dados fictícios): função cnpj -> resposta no formato do Minha Receita, ou None.
# Fica None em produção; o servidor local do PRM a liga só com fixtures (central_api/prm/fixtures).
FONTE_LOCAL = None


def consultar(entrada, faturamento=None, protegido=None):
    """`protegido`: função cnpj -> True/False/None da regra única de cliente protegido (PRM, U1/L14). Sem ela,
    vale a 1ª checagem do índice (negocio_ativo.tem_negocio_ativo), como antes."""
    cnpj = completar_cnpj(str(entrada or ""))
    saida = {"cnpj": cnpj, "faixa": "invalido", "titulo": "CNPJ inválido", "fonte": None, "ano_base": None, "empresa": None}
    if not cnpj_valido(cnpj):
        saida["detalhe"] = "Confira os 14 caracteres e os dois dígitos finais."
        return saida
    ativo = (protegido or negocio_ativo.tem_negocio_ativo)(cnpj)  # 1ª checagem: cliente Save nunca é enviado a serviço externo
    if ativo is None:
        return neutra(cnpj, "indice_ausente")
    if ativo:
        return neutra(cnpj, ativo if isinstance(ativo, str) else "negocio_ativo")
    local = FONTE_LOCAL(cnpj) if FONTE_LOCAL else None
    if local is not None:
        dados, fonte, motivo = local, "Base de teste (fictícia)", None
    elif os.environ.get("CENTRAL_API_EXTERNA", "1") != "1":
        saida.update(faixa="indisponivel", titulo="Consulta externa desligada", detalhe="A consulta a APIs externas está desligada neste ambiente.")
        return saida
    else:
        dados, fonte, motivo = _buscar(cnpj)
    if dados is not None:
        dados = _sanear(dados)
    if dados is None:
        if motivo == "nao_encontrado":
            saida.update(faixa="sem_dado", titulo="CNPJ não localizado", fonte=" e ".join(n for n, _ in FONTES),
                         detalhe="As fontes não têm este CNPJ. Confira o número; a base pode demorar semanas para incluir empresas novas.")
        else:
            saida.update(faixa="indisponivel", titulo="Consulta indisponível agora", detalhe="As fontes não responderam. Tente de novo em alguns minutos.")
        return saida
    saida["empresa"] = {"razao": dados.get("razao_social"), "porte": (dados.get("porte") or "").title() or None, "uf": dados.get("uf"),
                        "situacao": (dados.get("descricao_situacao_cadastral") or "").title() or None,
                        "matriz": str(dados.get("identificador_matriz_filial")) == "1"}
    saida["perfil"] = _perfil(dados)
    formas, ano = _regime(dados)
    simples, mei = bool(dados.get("opcao_pelo_simples")), bool(dados.get("opcao_pelo_mei"))
    saida["simples"] = simples or mei
    fonte_txt = "%s (ECF e opção pelo Simples), consultado em %s" % (fonte, date.today().isoformat())
    antigo = " A ECF mais recente é de %s: o regime pode ter mudado." % ano if ano and ano < date.today().year - 2 else ""
    reais = {f for f in formas if "REAL" in f}
    if simples or mei:
        saida.update(faixa="nao_real", titulo="Não é Lucro Real: " + ("MEI" if mei else "Simples Nacional"), fonte=fonte_txt,
                     detalhe="A empresa consta como optante pelo Simples. A recuperação de PIS/COFINS não cumulativo não se aplica.")
    elif reais and len(formas) == 1:
        saida.update(faixa="confirmado_real", titulo="Lucro Real confirmado", ano_base=ano, fonte=fonte_txt,
                     detalhe="Regime declarado na ECF do ano-base %s. Não garante que seja o mesmo hoje.%s" % (ano, antigo))
    elif reais:
        saida.update(faixa="provavel_real", titulo="Provável Lucro Real: regime misto no ano", ano_base=ano, fonte=fonte_txt,
                     detalhe="A ECF do ano-base %s traz mais de um regime (%s). Confirme com o cliente." % (ano, ", ".join(sorted(f.title() for f in formas))))
    elif formas:
        saida.update(faixa="nao_real", titulo="Não é Lucro Real: " + ", ".join(sorted(f.title() for f in formas)), ano_base=ano, fonte=fonte_txt,
                     detalhe="Regime declarado na ECF do ano-base %s.%s" % (ano, antigo))
    elif isinstance(faturamento, (int, float)) and math.isfinite(faturamento) and faturamento > TETO_PRESUMIDO:
        saida.update(faixa="provavel_real", titulo="Provável Lucro Real", fonte="Faturamento informado por você",
                     detalhe="Receita bruta acima de R$ 78 milhões obriga ao Lucro Real (Lei 9.718/1998, art. 14, I), salvo exceções. Falta a confirmação pela ECF.")
    else:
        saida.update(faixa="sem_dado", titulo="Sem dado de regime", fonte=fonte_txt,
                     detalhe="A empresa existe, mas não tem ECF publicada e não é do Simples. Peça a ECF ao cliente.")
    return saida


def consultar_lote(entradas, faturamento=None):
    """Consulta em paralelo (4 de cada vez, para não pressionar as APIs gratuitas), na ordem recebida."""
    with ThreadPoolExecutor(max_workers=4) as ex:
        return list(ex.map(lambda c: consultar(c, faturamento), entradas))


def registrar_uso(usuario, qtd):
    """Teto diário por usuário (contagem em memória na demo, sob trava). Devolve (permitido, usadas, limite)."""
    hoje = date.today().isoformat()
    with _lock:
        for k in [k for k in _uso if k[1] != hoje]:  # dias passados saem da memória
            del _uso[k]
        chave = (usuario, hoje)
        usado = _uso.get(chave, 0)
        if usado + qtd > LIMITE_DIA:
            return False, usado, LIMITE_DIA
        _uso[chave] = usado + qtd
        return True, usado + qtd, LIMITE_DIA


def limitar_ativos(usuario, resultados):
    """Anti-enumeração: conta os acertos 'negocio_ativo' do usuário no dia. A resposta já é neutra desde o primeiro acerto;
    passado CENTRAL_LIMITE_ATIVO o motivo interno vira 'negocio_ativo_acima_do_teto' e sai um alerta no log (possível
    varredura da carteira). Devolve a mesma lista."""
    hoje = date.today().isoformat()
    with _lock:
        for k in [k for k in _ativos if k[1] != hoje]:
            del _ativos[k]
        for r in resultados:
            if r.get("_motivo") == "negocio_ativo":
                _ativos[(usuario, hoje)] = _ativos.get((usuario, hoje), 0) + 1
                if _ativos[(usuario, hoje)] > LIMITE_ATIVO:
                    r["_motivo"] = "negocio_ativo_acima_do_teto"
                    log.warning("acertos de negócio ativo acima do teto (%d/dia): possível varredura da carteira", LIMITE_ATIVO)
    return resultados


def auditar(usuario, resultados, arquivo=None):
    """Quem consultou, o quê e quando (inclui os acertos de negócio ativo). Fica em dados-publicos (fora do git), 600."""
    arq = arquivo or os.path.join(BASE, "consultas-regime.jsonl")
    os.makedirs(os.path.dirname(arq) or ".", exist_ok=True)
    linhas = "".join(json.dumps({"quando": time.strftime("%Y-%m-%dT%H:%M:%S"), "usuario": usuario, "cnpj": r["cnpj"], "faixa": r["faixa"], **({"motivo": r["_motivo"]} if r.get("_motivo") else {})}, ensure_ascii=False) + "\n" for r in resultados)
    fd = os.open(arq, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as f:
        f.write(linhas)  # uma escrita só: linhas de consultas simultâneas não se misturam
    os.chmod(arq, 0o600)
