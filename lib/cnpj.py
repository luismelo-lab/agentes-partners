"""CNPJ numérico e alfanumérico: fonte única de normalização, raiz e dígito verificador.

Regra (IN RFB nº 2.229, de 15/10/2024; emissão desde 31/07/2026; consultado em 22/10/2026 em
gov.br/receitafederal › CNPJ Alfanumérico e na nota técnica do Serpro sobre o cálculo do DV):
  - 14 posições: raiz (1–8) e ordem do estabelecimento (9–12) podem ter letras A–Z e números;
    os 2 dígitos verificadores (13–14) continuam numéricos.
  - DV: módulo 11 com os pesos de sempre, valor de cada caractere = código ASCII − 48
    (0–9 valem 0–9; A = 17 … Z = 42). Para CNPJ só com números o resultado é o mesmo de antes.
  - CNPJs já emitidos não mudam; novas inscrições ainda podem sair só com números.

Use:  sys.path.insert(0, os.path.expanduser("~/agentes-partners/lib")); from cnpj import normalizar_cnpj, raiz_cnpj, cnpj_valido
"""
import re

_NAO_ALFANUM = re.compile(r"[^0-9A-Z]")
_FORMATO = re.compile(r"[0-9A-Z]{12}[0-9]{2}")
_P1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_P2 = [6] + _P1
# CNPJ dentro de texto (WhatsApp, e-mail, planilha): o numérico com o padrão de antes; o alfanumérico
# em maiúsculas, isolado de outras letras e números, com pelo menos uma letra.
CNPJ_TEXTO_NUM = re.compile(r"(?<!\d)(\d{2}\.?\d{3}\.?\d{3}\s?/?\s?\d{4}\s?-?\s?\d{2})(?!\d)")
CNPJ_TEXTO_ALFA = re.compile(r"(?<![0-9A-Za-z])([0-9A-Z]{2}\.?[0-9A-Z]{3}\.?[0-9A-Z]{3}\s?/?\s?[0-9A-Z]{4}\s?-?\s?\d{2})(?![0-9A-Za-z])")


def normalizar_cnpj(s):
    """Maiúsculas, sem pontuação nem espaços, letras preservadas. '' quando vazio.
    Para CNPJ numérico devolve o mesmo que re.sub(r'\\D', '', s). Texto com letras que não cabe num
    CNPJ alfanumérico (ex.: 'CNPJ 12.345…') cai na regra antiga (só os dígitos)."""
    t = _NAO_ALFANUM.sub("", str(s or "").upper())
    if t.isdigit() or not t: return t
    if len(t) <= 14 and t[-2:].isdigit(): return t
    return re.sub(r"\D", "", t)


def completar_cnpj(s):
    """normalizar_cnpj + zeros à esquerda (o HubSpot e o Excel perdem os zeros iniciais do CNPJ numérico)."""
    c = normalizar_cnpj(s)
    return c.zfill(14) if c else ""


def raiz_cnpj(s):
    """8 primeiras posições (identificam a empresa; matriz e filiais têm a mesma raiz). '' sem CNPJ."""
    c = completar_cnpj(s)
    return c[:8] if len(c) >= 8 else ""


def _valor(ch):
    return ord(ch) - 48


def dv_cnpj(base12):
    """Os 2 dígitos verificadores das 12 primeiras posições (numéricas ou alfanuméricas)."""
    b = _NAO_ALFANUM.sub("", str(base12 or "").upper())
    def dv(cs, pesos):
        r = sum(_valor(x) * p for x, p in zip(cs, pesos)) % 11
        return "0" if r < 2 else str(11 - r)
    d1 = dv(b, _P1)
    return d1 + dv(b + d1, _P2)


def cnpj_valido(s):
    """True se tem 14 posições no formato da Receita e o DV confere. Completa zeros à esquerda (8 < tamanho < 14)."""
    c = normalizar_cnpj(s)
    if 8 < len(c) < 14: c = c.zfill(14)
    if not _FORMATO.fullmatch(c) or len(set(c)) == 1: return False
    return c[12:] == dv_cnpj(c[:12])


def e_alfanumerico(s):
    return any(ch.isalpha() for ch in normalizar_cnpj(s))


def formatar_cnpj(s):
    """XX.XXX.XXX/XXXX-XX (também com letras). Fora de 14 posições devolve o valor normalizado."""
    c = completar_cnpj(s)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


def cnpjs_no_texto(texto, validar=True):
    """CNPJs encontrados num texto, normalizados e sem repetição (com validar=True, só os de DV válido)."""
    t = texto or ""
    achados = [(m.start(), m.group(1)) for m in CNPJ_TEXTO_NUM.finditer(t)]
    achados += [(m.start(), m.group(1)) for m in CNPJ_TEXTO_ALFA.finditer(t) if re.search(r"[A-Z]", m.group(1))]
    out = []
    for _, m in sorted(achados):
        c = normalizar_cnpj(m)
        if (not validar or cnpj_valido(c)) and c not in out: out.append(c)
    return out
