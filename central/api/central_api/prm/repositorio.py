"""Camada de repositório do PRM (lacuna L3): a mesma interface para o modo local (JSON, Fase 1) e para o banco (SQL, Fase 2).

Tabelas lógicas → arquivos de registro/prm/ (o mesmo envelope do skills/depto-dados/scripts/prm_local.py) e tabelas SQL.
Três tipos de tabela:
  gerado   o prm_local.py refaz inteiro a cada rodada (espelho do HubSpot, extrato previsto, registro único de demandas):
           a API só LÊ (gravar aqui seria perder o dado na próxima rodada);
  autoria  nasce no PRM e a API grava (registro, conflito, usuário, demanda do portal, notificação, contador...);
  ledger   só inclusão (eventos, decisões, trilha de acesso, movimentos do extrato): nada é alterado nem apagado.

Interface (as duas classes):
  listar(t, **igual) · obter(t, id) · inserir(t, linha) · gravar(t, linha) (upsert) · atualizar(t, id, mudancas)
  seq(serie) → int atômico · contar(chave, delta=1) → int atômico e persistente (tetos, L4) · transacao() (contexto)
"""
import contextlib, copy, fcntl, json, os, threading, time

ESQUEMA = "prm-local/1"
# lógica: (arquivo local, tabela SQL, chave, tipo)
TABELAS = {
    "parceiro": ("prm_parceiro", "prm.parceiro", "parceiro_id", "autoria"),
    "usuario_parceiro": ("prm_usuario_parceiro", "prm.usuario_parceiro", "usuario_id", "autoria"),
    "termo": ("prm_termo", "prm.termo", "termo_id", "autoria"),
    "registro": ("prm_registro_oportunidade", "prm.registro_oportunidade", "registro_id", "autoria"),
    "registro_evento": ("prm_registro_evento", "prm.registro_evento", "evento_id", "ledger"),
    "conflito": ("prm_conflito", "prm.conflito", "conflito_id", "autoria"),
    "negocio": ("hs_negocio", "hs.negocio", "deal_id", "gerado"),
    "pendencia": ("prm_negocio_pendencia", "prm.negocio_pendencia", "pendencia_id", "autoria"),
    "extrato_linha": ("prm_extrato_linha", "prm.extrato_linha", "linha_id", "gerado"),
    "extrato_movimento": ("prm_extrato_movimento", "prm.extrato_movimento", "movimento_id", "ledger"),
    "contestacao": ("prm_contestacao", "prm.contestacao", "contestacao_id", "autoria"),
    "demanda_unica": ("prm_demanda", "prm.demanda", "demanda_id", "gerado"),
    "demanda": ("prm_demanda_portal", "prm.demanda", "demanda_id", "autoria"),
    "demanda_evento": ("prm_demanda_evento", "prm.demanda_evento", "evento_id", "ledger"),
    "notificacao": ("central_caixa_mensagem", "central.caixa_mensagem", "id", "autoria"),
    "decisao": ("prm_decisao", "prm.decisao", "decisao_id", "ledger"),
    "acesso_log": ("seg_acesso_log", "seg.acesso_log", "acesso_id", "ledger"),
    "consulta": ("central_consulta_regime", "central.consulta_regime", "consulta_id", "ledger"),
    "aceite": ("seg_aceite_termo_uso", "seg.aceite_termo_uso", "aceite_id", "ledger"),
    "contador": ("seg_contador", "seg.contador", "chave", "autoria"),
    "sequencia": ("seg_sequencia", "seg.sequencia", "serie", "autoria"),
    "config": ("prm_config", "prm.config", "chave", "autoria"),
    "config_evento": ("prm_config_evento", "prm.config_evento", "evento_id", "ledger"),
    "nivel_apuracao": ("prm_nivel_apuracao", "prm.nivel_apuracao", "apuracao_id", "autoria"),
}


class SoLeitura(Exception):
    """Gravação em tabela gerada (espelho) ou alteração de ledger: erro de programa, nunca do usuário."""


def _chave(t):
    return TABELAS[t][2]


def _tipo(t):
    return TABELAS[t][3]


def _casa(linha, igual):
    return all(linha.get(k) == v for k, v in igual.items())


class _Base:
    def _id_ledger(self, t, linha):
        k = _chave(t)
        if linha.get(k) in (None, ""):
            linha[k] = "%s-%06d" % (t[:3].upper(), self.seq("ledger:" + t))
        return linha

    def inserir(self, t, linha):
        linha = dict(linha)
        if _tipo(t) == "gerado":
            raise SoLeitura("tabela %s é gerada pelo prm_local.py" % t)
        with self.transacao():
            if _tipo(t) == "ledger":
                self._id_ledger(t, linha)
            if self.obter(t, linha[_chave(t)]) is not None:
                raise SoLeitura("chave repetida em %s" % t)
            self._por(t, linha)
        return linha

    def gravar(self, t, linha):
        if _tipo(t) != "autoria":
            raise SoLeitura("upsert só em tabela de autoria (%s)" % t)
        with self.transacao():
            self._por(t, dict(linha))
        return linha

    def atualizar(self, t, ident, mudancas):
        if _tipo(t) != "autoria":
            raise SoLeitura("tabela %s não aceita alteração" % t)
        with self.transacao():
            atual = self.obter(t, ident)
            if atual is None:
                raise KeyError(ident)
            atual.update(mudancas)
            self._por(t, atual)
            return atual


class RepoJSON(_Base):
    """Fase 1: um arquivo por tabela em `pasta` (registro/prm/), permissão 700/600, gravação atômica, trava de arquivo
    (fcntl) para várias threads e processos. `somente_leitura` protege uma pasta real aberta só para ver."""

    def __init__(self, pasta, somente_leitura=False):
        self.pasta = os.path.abspath(os.path.expanduser(pasta))
        self.ro = somente_leitura
        os.makedirs(self.pasta, exist_ok=True)
        try:
            os.chmod(self.pasta, 0o700)
        except OSError:
            pass
        self._rl = threading.RLock()
        self._prof = 0
        self._fh = None
        self._cache = {}

    def _arq(self, t):
        return os.path.join(self.pasta, TABELAS[t][0] + ".json")

    @contextlib.contextmanager
    def transacao(self):
        with self._rl:
            if self._prof == 0:
                self._fh = open(os.path.join(self.pasta, ".trava"), "w")
                fcntl.flock(self._fh, fcntl.LOCK_EX)
            self._prof += 1
            try:
                yield self
            finally:
                self._prof -= 1
                if self._prof == 0:
                    fcntl.flock(self._fh, fcntl.LOCK_UN); self._fh.close(); self._fh = None

    def _linhas(self, t):
        a = self._arq(t)
        try:
            m = os.path.getmtime(a)
        except OSError:
            return []
        c = self._cache.get(t)
        if c and c[0] == m:
            return c[1]
        try:
            with open(a, encoding="utf-8") as f:
                env = json.load(f)
            linhas = env.get("linhas") if isinstance(env, dict) else None
            linhas = [x for x in (linhas or []) if isinstance(x, dict)]
        except (OSError, ValueError):
            linhas = []
        self._cache[t] = (m, linhas)
        return linhas

    def _escrever(self, t, linhas):
        if self.ro:
            raise SoLeitura("repositório aberto só para leitura")
        a = self._arq(t)
        env = {"esquema": ESQUEMA, "tabela": TABELAS[t][1], "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%S"), "fonte": "central_api.prm", "linhas": linhas}
        tmp = "%s.%d.%d.tmp" % (a, os.getpid(), threading.get_ident())
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(env, f, ensure_ascii=False, indent=1, default=str)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, a)
        self._cache[t] = (os.path.getmtime(a), linhas)

    def carregar_gerado(self, t, linhas, fonte="fixtures"):
        """Só para montar a pasta de demonstração (o papel do prm_local.py gerar)."""
        with self.transacao():
            self._escrever(t, [dict(x) for x in linhas])

    def listar(self, t, **igual):
        return [copy.deepcopy(x) for x in self._linhas(t) if _casa(x, igual)]

    def obter(self, t, ident):
        k = _chave(t)
        for x in self._linhas(t):
            if str(x.get(k)) == str(ident):
                return copy.deepcopy(x)
        return None

    def _por(self, t, linha):
        k = _chave(t)
        linhas = [x for x in self._linhas(t)]
        for i, x in enumerate(linhas):
            if str(x.get(k)) == str(linha[k]):
                linhas[i] = linha
                break
        else:
            linhas.append(linha)
        self._escrever(t, linhas)

    def seq(self, serie):
        with self.transacao():
            atual = self.obter("sequencia", serie) or {"serie": serie, "n": 0}
            atual["n"] = int(atual["n"]) + 1
            self._por("sequencia", atual)
            return atual["n"]

    def contar(self, chave, delta=1):
        with self.transacao():
            atual = self.obter("contador", chave) or {"chave": chave, "n": 0}
            atual["n"] = int(atual["n"]) + delta
            atual["em"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            self._por("contador", atual)
            return atual["n"]

    def valor_contador(self, chave):
        x = self.obter("contador", chave)
        return int(x["n"]) if x else 0


# ---------------------------------------------------------------- Fase 2: SQL (DB-API, paramstyle qmark: sqlite3 e pyodbc)
PROMOVIDAS = ("parceiro_id", "usuario_id", "estado", "cnpj_raiz_hmac", "deal_id")


class RepoSQL(_Base):
    """Mesma interface sobre um banco. Cada tabela lógica tem a chave, colunas promovidas (filtro e RLS por
    parceiro_id/usuario_id no Azure SQL) e o documento completo em `dados` (JSON). Na Fase 2 as colunas do schema.sql
    entram como promovidas, sem mudar quem chama. `conectar` devolve uma conexão DB-API nova (pyodbc com token do Entra
    na Azure; sqlite3 nos testes)."""

    def __init__(self, conectar, criar=False):
        self._conectar = conectar
        self._con = conectar()
        self._rl = threading.RLock()
        self._prof = 0
        if criar:
            self.criar_tabelas()

    @staticmethod
    def nome(t):
        return TABELAS[t][1].replace(".", "_")

    def criar_tabelas(self):
        cur = self._con.cursor()
        for t in TABELAS:
            cols = ", ".join("%s TEXT" % c for c in PROMOVIDAS if c != _chave(t))
            cur.execute("CREATE TABLE IF NOT EXISTS %s (chave TEXT PRIMARY KEY, %s, dados TEXT NOT NULL)" % (self.nome(t), cols))
        self._con.commit()

    @contextlib.contextmanager
    def transacao(self):
        with self._rl:
            self._prof += 1
            try:
                yield self
                if self._prof == 1:
                    self._con.commit()
            except BaseException:
                if self._prof == 1:
                    self._con.rollback()
                raise
            finally:
                self._prof -= 1

    def _linha(self, r):
        return json.loads(r[0])

    def listar(self, t, **igual):
        sql_f = {k: v for k, v in igual.items() if k in PROMOVIDAS and k != _chave(t) and v is not None}
        resto = {k: v for k, v in igual.items() if k not in sql_f}
        onde = " AND ".join("%s = ?" % k for k in sql_f)
        cur = self._con.cursor()
        cur.execute("SELECT dados FROM %s%s ORDER BY chave" % (self.nome(t), (" WHERE " + onde) if onde else ""), [str(v) for v in sql_f.values()])
        return [x for x in (self._linha(r) for r in cur.fetchall()) if _casa(x, resto)]

    def obter(self, t, ident):
        cur = self._con.cursor()
        cur.execute("SELECT dados FROM %s WHERE chave = ?" % self.nome(t), [str(ident)])
        r = cur.fetchone()
        return self._linha(r) if r else None

    def _por(self, t, linha):
        cols = [c for c in PROMOVIDAS if c != _chave(t)]
        vals = [None if linha.get(c) is None else str(linha.get(c)) for c in cols]
        dados = json.dumps(linha, ensure_ascii=False, default=str)
        cur = self._con.cursor()
        sets = ", ".join("%s = ?" % c for c in cols + ["dados"])
        cur.execute("UPDATE %s SET %s WHERE chave = ?" % (self.nome(t), sets), vals + [dados, str(linha[_chave(t)])])
        if cur.rowcount == 0:
            cur.execute("INSERT INTO %s (chave, %s, dados) VALUES (?, %s)" % (self.nome(t), ", ".join(cols), ", ".join("?" * (len(cols) + 1))),
                        [str(linha[_chave(t)])] + vals + [dados])
        if self._prof == 0:
            self._con.commit()

    def carregar_gerado(self, t, linhas, fonte="fixtures"):
        with self.transacao():
            self._con.cursor().execute("DELETE FROM %s" % self.nome(t))
            for x in linhas:
                self._por(t, dict(x))

    def _incrementar(self, t, chave, campo, delta):
        """Atualização atômica no banco (UPDATE n = n + ?), com inclusão na 1ª vez."""
        with self.transacao():
            atual = self.obter(t, chave)
            if atual is None:
                atual = {_chave(t): chave, campo: 0}
            atual[campo] = int(atual[campo]) + delta
            atual["em"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            self._por(t, atual)
            return atual[campo]

    def seq(self, serie):
        return self._incrementar("sequencia", serie, "n", 1)

    def contar(self, chave, delta=1):
        return self._incrementar("contador", chave, "n", delta)

    def valor_contador(self, chave):
        x = self.obter("contador", chave)
        return int(x["n"]) if x else 0
