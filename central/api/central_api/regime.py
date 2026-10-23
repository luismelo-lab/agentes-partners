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
A 1ª checagem é a base Save Company (negocio_ativo.py): empresa com negócio ativo não segue para as APIs.
"""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import date

sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib"))
from cnpj import cnpj_valido, normalizar_cnpj  # noqa: E402
from . import negocio_ativo  # noqa: E402

BASE = os.path.expanduser(os.environ.get("CENTRAL_RECEITA", "~/agentes-partners/dados-publicos/receita"))  # só a trilha de auditoria
LIMITE_LOTE = 20
LIMITE_DIA = int(os.environ.get("CENTRAL_LIMITE_DIA", "200"))
TETO_PRESUMIDO = 78_000_000  # Lei 9.718/1998, art. 13 e art. 14, I
TTL = 24 * 3600
TIMEOUT = 10
FONTES = [("Minha Receita", "https://minhareceita.org/%s"), ("BrasilAPI", "https://brasilapi.com.br/api/cnpj/v1/%s")]

_memoria = {}
_uso = {}


def _http(url):
    """(status, json|None). Status 0 = falha de rede ou tempo esgotado. Usa o curl, como o receita_cnpj.py: o Python
    da python.org no Mac não traz os certificados raiz e recusaria o HTTPS (a verificação não é desligada)."""
    try:
        r = subprocess.run(["curl", "-sS", "-m", str(TIMEOUT), "-A", "SaveCo-Central-Partners/1.0", "-H", "Accept: application/json",
                            "-w", "\n%{http_code}", url], capture_output=True, text=True, timeout=TIMEOUT + 5)
        corpo, _, codigo = r.stdout.rpartition("\n")
        st = int(codigo or 0)
        return (st, json.loads(corpo)) if st == 200 else (st, None)
    except (subprocess.SubprocessError, ValueError, OSError):
        return 0, None


def _buscar(cnpj):
    """(dados|None, nome da fonte, motivo). Motivo: 'nao_encontrado' (alguma fonte disse 404) ou 'indisponivel'."""
    visto = _memoria.get(cnpj)
    if visto and time.time() - visto[0] < TTL:
        return visto[1], visto[2], None
    nao_achou = False
    for nome, modelo in FONTES:
        st, dados = _http(modelo % cnpj)
        if st == 200 and isinstance(dados, dict):
            _memoria[cnpj] = (time.time(), dados, nome)
            return dados, nome, None
        nao_achou = nao_achou or st == 404
    return None, None, "nao_encontrado" if nao_achou else "indisponivel"


def _regime(dados):
    """(formas no ano mais recente, ano). Vazio quando a ECF não trouxe nada."""
    lista = [x for x in (dados.get("regime_tributario") or []) if x.get("forma_de_tributacao")]
    if not lista:
        return set(), None
    ano = max(x.get("ano") or 0 for x in lista)
    return {x["forma_de_tributacao"].strip().upper() for x in lista if (x.get("ano") or 0) == ano}, ano or None


def consultar(entrada, faturamento=None):
    cnpj = normalizar_cnpj(str(entrada or ""))
    saida = {"cnpj": cnpj, "faixa": "invalido", "titulo": "CNPJ inválido", "fonte": None, "ano_base": None, "empresa": None}
    if not cnpj_valido(cnpj):
        saida["detalhe"] = "Confira os 14 caracteres e os dois dígitos finais."
        return saida
    ativo = negocio_ativo.tem_negocio_ativo(cnpj)  # 1ª checagem: cliente Save nunca é enviado a serviço externo
    if ativo is None:
        saida.update(faixa="indisponivel", titulo="Consulta indisponível agora", detalhe="Não foi possível conferir a base Save Company. Tente de novo mais tarde.")
        return saida
    if ativo:
        saida.update(faixa="negocio_ativo", titulo="Empresa com negócio ativo na base Save Company", fonte="Base Save Company",
                     detalhe="Esta empresa já tem um negócio em andamento ou concluído com a Save. Não é preciso consultar o regime. Em caso de dúvida, fale com a Área Partners.")
        return saida
    if os.environ.get("CENTRAL_API_EXTERNA", "1") != "1":
        saida.update(faixa="indisponivel", titulo="Consulta externa desligada", detalhe="A consulta a APIs externas está desligada neste ambiente.")
        return saida
    dados, fonte, motivo = _buscar(cnpj)
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
    elif faturamento and faturamento > TETO_PRESUMIDO:
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
    """Teto diário por usuário (contagem em memória na demo). Devolve (permitido, usadas, limite)."""
    chave = (usuario, date.today().isoformat())
    usado = _uso.get(chave, 0)
    if usado + qtd > LIMITE_DIA:
        return False, usado, LIMITE_DIA
    _uso[chave] = usado + qtd
    return True, usado + qtd, LIMITE_DIA


def auditar(usuario, resultados, arquivo=None):
    """Quem consultou, o quê e quando. Fica em dados-publicos (fora do git)."""
    arq = arquivo or os.path.join(BASE, "consultas-regime.jsonl")
    with open(arq, "a") as f:
        for r in resultados:
            f.write(json.dumps({"quando": time.strftime("%Y-%m-%dT%H:%M:%S"), "usuario": usuario, "cnpj": r["cnpj"], "faixa": r["faixa"]}, ensure_ascii=False) + "\n")
    os.chmod(arq, 0o600)
