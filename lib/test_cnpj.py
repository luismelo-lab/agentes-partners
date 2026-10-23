"""Testes do lib/cnpj.py.  Rode:  python3 -m unittest ~/agentes-partners/lib/test_cnpj.py  (ou python3 lib/test_cnpj.py)

Exemplos alfanuméricos da Receita: 12.ABC.345/01DE-35 (nota técnica do Serpro sobre o cálculo do DV) e
00.000.000/E08G-12 (primeiro CNPJ alfanumérico, filial do Banco do Brasil, notícia da Receita de 31/07/2026).
CNPJ numérico gerado na hora (o scanner do repositório bloqueia CNPJ numérico válido no código).
"""
import os, random, re, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cnpj import (cnpj_valido, cnpjs_no_texto, completar_cnpj, dv_cnpj, e_alfanumerico, formatar_cnpj,  # noqa: E402
                  normalizar_cnpj, raiz_cnpj)

SERPRO = "12ABC34501DE35"
PRIMEIRO = "00000000E08G12"


def _antigo_valido(c):
    """Validação numérica usada até 22/10/2026 (lib/partners_dados.py), para conferir que nada mudou."""
    c = re.sub(r"\D", "", str(c or "")); c = c.zfill(14) if 8 < len(c) < 14 else c
    if len(c) != 14 or len(set(c)) == 1: return False
    def dv(base, pesos): s = sum(int(x) * p for x, p in zip(base, pesos)) % 11; return "0" if s < 2 else str(11 - s)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    return c[12] == dv(c[:12], p1) and c[13] == dv(c[:13], [6] + p1)


def _numerico():
    base = "".join(random.choice("0123456789") for _ in range(12))
    return base + dv_cnpj(base)


class Alfanumerico(unittest.TestCase):
    def test_dv_exemplos_receita(self):
        self.assertEqual(dv_cnpj("12ABC34501DE"), "35")
        self.assertEqual(dv_cnpj("00000000E08G"), "12")

    def test_normalizar_preserva_letras(self):
        self.assertEqual(normalizar_cnpj("12.ABC.345/01DE-35"), SERPRO)
        self.assertEqual(normalizar_cnpj(" 12.abc.345/01de-35 "), SERPRO)
        self.assertEqual(normalizar_cnpj("00.000.000/E08G-12"), PRIMEIRO)

    def test_raiz(self):
        self.assertEqual(raiz_cnpj("12.ABC.345/01DE-35"), "12ABC345")
        self.assertEqual(raiz_cnpj("00.000.000/E08G-12"), "00000000")

    def test_valido(self):
        self.assertTrue(cnpj_valido("12.ABC.345/01DE-35"))
        self.assertTrue(cnpj_valido(PRIMEIRO))
        self.assertFalse(cnpj_valido("12.ABC.345/01DE-36"))
        self.assertFalse(cnpj_valido("12ABC34501DEX5"))  # DV com letra
        self.assertTrue(e_alfanumerico(SERPRO))

    def test_formatar(self):
        self.assertEqual(formatar_cnpj(SERPRO), "12.ABC.345/01DE-35")

    def test_texto(self):
        t = "cliente 12.ABC.345/01DE-35, filial 00.000.000/E08G-12, código ABCDEFGHIJKL99 e repetido 12ABC34501DE35"
        self.assertEqual(cnpjs_no_texto(t), [SERPRO, PRIMEIRO])


class Numerico(unittest.TestCase):
    def test_mesmo_resultado_de_antes(self):
        random.seed(2229)
        for _ in range(2000):
            c = _numerico()
            f = formatar_cnpj(c)
            self.assertEqual(normalizar_cnpj(f), re.sub(r"\D", "", f))
            self.assertTrue(cnpj_valido(f)); self.assertEqual(cnpj_valido(f), _antigo_valido(f))
            errado = c[:13] + str((int(c[13]) + 1) % 10)
            self.assertFalse(cnpj_valido(errado)); self.assertEqual(cnpj_valido(errado), _antigo_valido(errado))
            self.assertEqual(raiz_cnpj(f), c[:8])

    def test_zeros_perdidos(self):
        random.seed(7)
        c = "00" + _numerico()[2:]
        c = c[:12] + dv_cnpj(c[:12])
        sem_zeros = c.lstrip("0")
        self.assertEqual(completar_cnpj(sem_zeros), c)
        self.assertEqual(raiz_cnpj(sem_zeros), c[:8])
        self.assertTrue(cnpj_valido(sem_zeros))

    def test_texto_com_rotulo_cai_na_regra_antiga(self):
        self.assertEqual(normalizar_cnpj("CNPJ: 12.345.678/0001-9"), "1234567800019")
        self.assertEqual(normalizar_cnpj(None), ""); self.assertEqual(raiz_cnpj(""), "")
        self.assertFalse(cnpj_valido("11111111111111")); self.assertFalse(cnpj_valido(""))

    def test_texto_numerico_igual_ao_padrao_antigo(self):
        random.seed(11)
        c = _numerico()
        self.assertEqual(cnpjs_no_texto(f"CNPJ{formatar_cnpj(c)}x"), [c])


if __name__ == "__main__":
    unittest.main()
