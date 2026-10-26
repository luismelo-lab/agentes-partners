"""Testes da etapa 2 (validação do token e permissões). Rodam sem Azure: as chaves são geradas aqui.

    cd central/api && python3 -m unittest -v
"""
import json, time, unittest, uuid

try:
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from jwt.algorithms import RSAAlgorithm
except ImportError:  # CI sem as dependências: o módulo aparece como pulado, com o motivo (não some em silêncio)
    raise unittest.SkipTest("PyJWT[crypto] ausente: rode pip install -r central/api/requirements.txt")

from central_api import permissoes as P
from central_api import rotas
from central_api.token import Chaves, Config, TokenInvalido, validar

TENANT, API = str(uuid.uuid4()), str(uuid.uuid4())  # valores de teste, nunca reais
CFG = Config(TENANT, API)


def par_de_chaves(kid):
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = json.loads(RSAAlgorithm.to_jwk(k.public_key())); pub.update(kid=kid, use="sig", alg="RS256")
    return k, pub


CHAVE, JWK = par_de_chaves("k1")
OUTRA, _ = par_de_chaves("k1")  # mesmo kid, chave diferente (assinatura falsa)
buscas = []


def buscar(url):
    buscas.append(url)
    return {"keys": [JWK]}


def token(chave=CHAVE, kid="k1", alg="RS256", **mudar):
    agora = int(time.time())
    c = {"iss": f"https://login.microsoftonline.com/{TENANT}/v2.0", "aud": API, "tid": TENANT, "oid": str(uuid.uuid4()),
         "name": "Teste", "preferred_username": "teste@example.com", "scp": "Central.Acesso", "roles": ["Partners.Masters"],
         "iat": agora, "nbf": agora, "exp": agora + 3600}
    c.update(mudar)
    c = {k: v for k, v in c.items() if v is not None}
    return jwt.encode(c, chave, algorithm=alg, headers={"kid": kid})


def cab(t): return {"Authorization": f"Bearer {t}"}


class Token(unittest.TestCase):
    def setUp(self): self.ch = Chaves(CFG.jwks_url, buscar)

    def ok(self, t): return validar(t, CFG, self.ch)

    def falha(self, t):
        with self.assertRaises(TokenInvalido): self.ok(t)

    def test_valido(self):
        i = self.ok(token())
        self.assertEqual(i["tipo"], "usuario"); self.assertEqual(i["papeis"], ["Partners.Masters"])

    def test_aud_com_prefixo_api(self): self.ok(token(aud=f"api://{API}"))
    def test_assinatura_falsa(self): self.falha(token(chave=OUTRA))
    def test_kid_desconhecido(self): self.falha(token(kid="k9"))
    def test_alg_none_recusado(self): self.falha(jwt.encode({"a": 1}, None, algorithm="none"))
    def test_aud_errado(self): self.falha(token(aud=str(uuid.uuid4())))
    def test_iss_errado(self): self.falha(token(iss="https://login.microsoftonline.com/outro/v2.0"))
    def test_tid_errado(self): self.falha(token(tid=str(uuid.uuid4())))
    def test_expirado(self): self.falha(token(exp=int(time.time()) - 3600, iat=int(time.time()) - 7200, nbf=int(time.time()) - 7200))
    def test_ainda_nao_vale(self): self.falha(token(nbf=int(time.time()) + 3600))
    def test_sem_exp(self): self.falha(token(exp=None))
    def test_sem_escopo_e_sem_papel_de_agente(self): self.falha(token(scp=None))
    def test_escopo_errado(self): self.falha(token(scp="User.Read"))
    def test_sem_oid(self): self.falha(token(oid=None))
    def test_malformado(self): self.falha("isto.nao.e-um-token")

    def test_agente(self):
        i = self.ok(token(scp=None, roles=["Agentes.Processar"]))
        self.assertEqual(i["tipo"], "agente")

    def test_cache_de_chaves(self):
        n = len(buscas); self.ok(token()); self.ok(token())
        self.assertEqual(len(buscas) - n, 1)


class Permissoes(unittest.TestCase):
    def ident(self, *papeis, tipo="usuario"): return {"tipo": tipo, "oid": "x", "papeis": list(papeis)}

    def test_email_corporativo_sem_papel_nao_entra(self):
        with self.assertRaises(P.SemPermissao): P.exigir(self.ident(), "ver_painel")

    def test_cada_papel(self):
        self.assertTrue(P.exigir(self.ident(P.TECNICA), "decidir_recorrencia"))
        with self.assertRaises(P.SemPermissao): P.exigir(self.ident(P.BDR), "decidir_recorrencia")
        with self.assertRaises(P.SemPermissao): P.exigir(self.ident(P.MASTERS), "decidir_conselho")
        with self.assertRaises(P.SemPermissao): P.exigir(self.ident(P.LEITURA), "aprovar_chamado")

    def test_dono_do_registro(self):
        self.assertTrue(P.exigir(self.ident(P.MASTERS), "aprovar_chamado", {"pessoa": "daniela"}))
        with self.assertRaises(P.SemPermissao): P.exigir(self.ident(P.MASTERS), "aprovar_chamado", {"pessoa": "jenifer"})
        self.assertTrue(P.exigir(self.ident(P.GESTOR), "aprovar_chamado", {"pessoa": "jenifer"}))

    def test_agente_nao_usa_acao_de_usuario(self):
        with self.assertRaises(P.SemPermissao): P.exigir(self.ident(P.AGENTE, tipo="agente"), "aprovar_chamado")
        self.assertTrue(P.exigir(self.ident(P.AGENTE, tipo="agente"), "processar_pendencias"))

    def test_usuario_nao_usa_acao_de_agente(self):
        with self.assertRaises(P.SemPermissao): P.exigir(self.ident(P.GESTOR), "processar_pendencias")


class Rotas(unittest.TestCase):
    DADOS = {"atualizado": "19/10/2026", "resumo": {"pedidos": 3}, "whatsapp": {"daniela": [1], "jenifer": [2]}}

    def setUp(self): rotas.contexto(CFG, Chaves(CFG.jwks_url, buscar))

    def test_eu(self):
        s, b = rotas.eu(cab(token(roles=["Partners.Tecnica"])))
        self.assertEqual(s, 200); self.assertEqual(b["pessoa"], "geovana"); self.assertIn("decidir_recorrencia", b["pode"])

    def test_sem_token_401(self): self.assertEqual(rotas.eu({})[0], 401)
    def test_sem_papel_403(self): self.assertEqual(rotas.eu(cab(token(roles=[])))[0], 403)

    def test_painel_filtra_pela_pessoa(self):
        s, b = rotas.painel(cab(token(roles=["Partners.BDR"])), lambda: self.DADOS)
        self.assertEqual(s, 200); self.assertEqual(b["whatsapp"], [2])

    def test_painel_gestor_ve_tudo(self):
        s, b = rotas.painel(cab(token(roles=["Partners.Gestor"])), lambda: self.DADOS)
        self.assertEqual(b["whatsapp"], self.DADOS["whatsapp"])

    def test_painel_leitura_so_agregado(self):
        s, b = rotas.painel(cab(token(roles=["Partners.Leitura"])), lambda: self.DADOS)
        self.assertEqual(set(b), {"atualizado", "resumo"})


if __name__ == "__main__":
    unittest.main()
