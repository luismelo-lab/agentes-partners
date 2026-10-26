"""Fuso, carimbo e dias úteis (02 §0.2): carimbo gravado em UTC com milissegundos, exibido em America/Sao_Paulo.

Dia útil: segunda a sexta, menos os feriados nacionais (calculados, inclusive Páscoa, Sexta-Feira Santa, Carnaval e
Corpus Christi) e os extras de `calendario.feriados_extras`. Prazo em d.u. vence às 23h59 do último dia útil; prazo em
dias corridos vence às 23h59 do último dia. Horas úteis contam só o expediente (`calendario.expediente`) dos dias úteis.
"""
from datetime import date, datetime, time, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    FUSO = ZoneInfo("America/Sao_Paulo")
except Exception:  # noqa: BLE001  sem base de fusos: Brasília não tem horário de verão desde 2019
    FUSO = timezone(timedelta(hours=-3))

UTC = timezone.utc


def iso(dt):
    """Carimbo UTC com milissegundos: 2026-10-26T18:04:05.123Z."""
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (dt.microsecond // 1000)


def ler(s):
    if s is None or s == "":
        return None
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=FUSO)
    if isinstance(s, date):
        return datetime.combine(s, time(0, 0), FUSO)
    t = str(s).strip().replace("Z", "+00:00")
    if len(t) == 10:
        return datetime.combine(date.fromisoformat(t), time(0, 0), FUSO)
    dt = datetime.fromisoformat(t)
    return dt if dt.tzinfo else dt.replace(tzinfo=FUSO)


def local(dt):
    return ler(dt).astimezone(FUSO)


def fmt(dt):
    """dd/mm/aaaa hh:mm no fuso de Brasília."""
    return local(dt).strftime("%d/%m/%Y %H:%M") if dt else ""


def fmt_data(d):
    if not d:
        return ""
    if isinstance(d, str):
        d = date.fromisoformat(d) if len(d) == 10 else ler(d)
    if isinstance(d, datetime):
        d = local(d).date()
    return d.strftime("%d/%m/%Y")


def dia(dt):
    """Data local (date) de um carimbo ou texto."""
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt
    return local(dt).date()


def _pascoa(ano):
    a = ano % 19; b, c = divmod(ano, 100); d, e = divmod(b, 4); f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i, k = divmod(c, 4); l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; mes = (h + l - 7 * m + 114) // 31; dia_ = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia_)


_CACHE = {}


def feriados(ano, carnaval=True, extras=()):
    chave = (ano, carnaval, tuple(extras))
    if chave not in _CACHE:
        p = _pascoa(ano)
        fs = {date(ano, 1, 1), date(ano, 4, 21), date(ano, 5, 1), date(ano, 9, 7), date(ano, 10, 12), date(ano, 11, 2),
              date(ano, 11, 15), date(ano, 11, 20), date(ano, 12, 25), p - timedelta(days=2), p + timedelta(days=60)}
        if carnaval:
            fs |= {p - timedelta(days=48), p - timedelta(days=47)}
        fs |= {date.fromisoformat(x) for x in extras if str(x).startswith(str(ano))}
        _CACHE[chave] = fs
    return _CACHE[chave]


class Calendario:
    def __init__(self, param):
        self.p = param

    def util(self, d):
        d = dia(d)
        return d.weekday() < 5 and d not in feriados(d.year, self.p("calendario.carnaval_feriado"), self.p("calendario.feriados_extras"))

    def proximo_util(self, d):
        d = dia(d)
        while not self.util(d):
            d += timedelta(days=1)
        return d

    def somar_du(self, inicio, n):
        """Data (local) do n-ésimo dia útil depois de `inicio` (0 = o próprio dia, se útil; senão o próximo útil)."""
        d = self.proximo_util(inicio)
        while n > 0:
            d += timedelta(days=1)
            if self.util(d):
                n -= 1
        return d

    def prazo_du(self, inicio, n):
        """Carimbo do fim do prazo: 23h59 do n-ésimo dia útil."""
        return datetime.combine(self.somar_du(inicio, n), time(23, 59, 59), FUSO)

    def prazo_corridos(self, inicio, n):
        return datetime.combine(dia(inicio) + timedelta(days=n), time(23, 59, 59), FUSO)

    def du_entre(self, a, b):
        """Dias úteis completos entre as datas de a (exclusive) e b (inclusive)."""
        da, db = dia(a), dia(b)
        n, d = 0, da
        while d < db:
            d += timedelta(days=1)
            if self.util(d):
                n += 1
        return n

    def horas_uteis_entre(self, a, b):
        ini, fim = self.p("calendario.expediente")
        a, b = local(a), local(b)
        if b <= a:
            return 0.0
        total, d = 0.0, a.date()
        while d <= b.date():
            if self.util(d):
                j0 = datetime.combine(d, time(ini), FUSO); j1 = datetime.combine(d, time(fim), FUSO)
                x0, x1 = max(a, j0), min(b, j1)
                if x1 > x0:
                    total += (x1 - x0).total_seconds() / 3600
            d += timedelta(days=1)
        return round(total, 4)

    def somar_horas_uteis(self, a, horas):
        """Primeiro instante em que se completam `horas` úteis a partir de `a`."""
        ini, fim = self.p("calendario.expediente")
        t, falta = local(a), float(horas)
        while True:
            if self.util(t):
                j0 = datetime.combine(t.date(), time(ini), FUSO); j1 = datetime.combine(t.date(), time(fim), FUSO)
                x = max(t, j0)
                if x < j1:
                    disp = (j1 - x).total_seconds() / 3600
                    if disp >= falta:
                        return x + timedelta(hours=falta)
                    falta -= disp
            t = datetime.combine(t.date() + timedelta(days=1), time(0, 0), FUSO)

    def janela_envio(self, dt):
        """Próximo instante permitido para envio automático (07h–20h de dia útil, 02 §13)."""
        h0, h1 = self.p("notificacao.janela_envio")
        t = local(dt)
        if self.util(t) and h0 <= t.hour < h1:
            return t
        d = t.date() if (t.hour < h0 and self.util(t)) else self.somar_du(t.date() + timedelta(days=1), 0)
        return datetime.combine(d, time(h0, 0), FUSO)
