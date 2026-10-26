"""Validação do token de acesso emitido pelo Microsoft Entra ID (OAuth 2.0 / OpenID Connect, tokens v2).

Regras (docs/sso-entra/diagnostico-e-plano.md §4):
- assinatura RS256 pelas chaves públicas do locatário (JWKS), com cache e nova busca quando aparece um `kid` desconhecido;
- `iss` = https://login.microsoftonline.com/<TENANT_ID>/v2.0, `tid` = <TENANT_ID>, `aud` = <API_CLIENT_ID> (ou api://<API_CLIENT_ID>);
- `exp`, `nbf` e `iat` obrigatórios (tolerância de 60 s de relógio);
- usuário (token delegado): `scp` contém o escopo da Central e há `oid`;
- rotina (token de aplicativo, client credentials): sem `scp`, `roles` contém `Agentes.Processar`.
Nada aqui confia em e-mail: identidade é o `oid`, permissão é o `roles`.

Configuração por variáveis de ambiente (nunca no código): CENTRAL_TENANT_ID, CENTRAL_API_CLIENT_ID,
CENTRAL_SCOPE (padrão Central.Acesso).
"""
import json, os, threading, time, urllib.request

try:
    import jwt
    from jwt import PyJWK
except ImportError:  # sem PyJWT (ex.: CI só com a biblioteca padrão): nenhum token é aceito (falha fechada)
    jwt = PyJWK = None

LEEWAY = 60
JWKS_TTL = 3600
PAPEL_AGENTE = "Agentes.Processar"


class TokenInvalido(Exception):
    """401: token ausente, malformado, expirado ou de outro emissor/público."""


class Config:
    def __init__(self, tenant_id=None, api_client_id=None, scope=None):
        self.tenant_id = tenant_id or os.environ.get("CENTRAL_TENANT_ID", "")
        self.api_client_id = api_client_id or os.environ.get("CENTRAL_API_CLIENT_ID", "")
        self.scope = scope or os.environ.get("CENTRAL_SCOPE", "Central.Acesso")
        if not (self.tenant_id and self.api_client_id):
            raise RuntimeError("Defina CENTRAL_TENANT_ID e CENTRAL_API_CLIENT_ID (local.settings.json ou configuração do Azure).")

    @property
    def emissor(self): return f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"

    @property
    def jwks_url(self): return f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys"

    @property
    def publicos(self): return [self.api_client_id, f"api://{self.api_client_id}"]


class Chaves:
    """Cache das chaves públicas do Entra. `buscar` é injetável para os testes."""

    def __init__(self, url, buscar=None):
        self.url, self._buscar = url, buscar or self._http
        self._chaves, self._quando, self._trava = {}, 0.0, threading.Lock()

    @staticmethod
    def _http(url):
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())

    def _atualizar(self):
        dados = self._buscar(self.url)
        if PyJWK is None:
            raise TokenInvalido("PyJWT ausente")
        self._chaves = {k["kid"]: PyJWK(k, algorithm="RS256").key for k in dados.get("keys", []) if k.get("kid") and k.get("kty") == "RSA"}
        self._quando = time.time()

    def chave(self, kid):
        with self._trava:
            if not self._chaves or time.time() - self._quando > JWKS_TTL:
                self._atualizar()
            if kid not in self._chaves:  # rotação de chave: busca de novo uma vez
                self._atualizar()
            if kid not in self._chaves:
                raise TokenInvalido("chave de assinatura desconhecida")
            return self._chaves[kid]


def extrair_bearer(cabecalhos):
    v = cabecalhos.get("Authorization") or cabecalhos.get("authorization") or ""
    if not v.startswith("Bearer ") or len(v) < 20:
        raise TokenInvalido("sem token Bearer")
    return v[7:].strip()


def validar(token, cfg, chaves):
    """Devolve a identidade validada: {tipo, oid, nome, usuario, papeis, escopos}. Levanta TokenInvalido."""
    if jwt is None:
        raise TokenInvalido("PyJWT ausente")
    try:
        cab = jwt.get_unverified_header(token)
    except jwt.PyJWTError as e:
        raise TokenInvalido("token malformado") from e
    if cab.get("alg") != "RS256" or not cab.get("kid"):
        raise TokenInvalido("algoritmo ou chave não aceitos")
    try:
        c = jwt.decode(token, chaves.chave(cab["kid"]), algorithms=["RS256"], audience=cfg.publicos, issuer=cfg.emissor,
                       leeway=LEEWAY, options={"require": ["exp", "nbf", "iat", "iss", "aud", "tid"]})
    except jwt.ExpiredSignatureError as e:
        raise TokenInvalido("token expirado") from e
    except jwt.PyJWTError as e:
        raise TokenInvalido(f"token recusado: {type(e).__name__}") from e
    if c.get("tid") != cfg.tenant_id:
        raise TokenInvalido("locatário diferente")
    if not c.get("oid"):
        raise TokenInvalido("token sem oid")
    papeis = set(c.get("roles") or [])
    escopos = set(str(c.get("scp") or "").split())
    if escopos:
        if cfg.scope not in escopos:
            raise TokenInvalido("escopo da Central ausente")
        tipo = "usuario"
    else:
        if PAPEL_AGENTE not in papeis:
            raise TokenInvalido("token de aplicativo sem o papel Agentes.Processar")
        tipo = "agente"
    return {"tipo": tipo, "oid": c["oid"], "nome": c.get("name"), "usuario": c.get("preferred_username"),
            "papeis": sorted(papeis), "escopos": sorted(escopos)}
