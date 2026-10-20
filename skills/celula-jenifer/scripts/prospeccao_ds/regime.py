"""Regime tributário (Minha Receita, mesma fonte da Inteligência Comercial) para os prospects D&S, em ordem de prioridade.
Só CNPJs de prospects (nunca clientes: o universo já exclui toda raiz que está no HubSpot). Cache compartilhado."""
import json, os, pickle, subprocess, threading, time
from concurrent.futures import ThreadPoolExecutor
S = os.environ.get("PROSPECCAO_DS", os.path.expanduser("~/agentes-partners/departamentos/intel-comercial/prospeccao-ds"))  # dados (fora do repositório); CP = os.path.expanduser("~/agentes-partners/dados-publicos/receita/regime-cache.json")
cache = json.load(open(CP)); M = pickle.load(open(S + "/modelo-completo.pkl", "rb")); trava = threading.Lock()  # universo inteiro (SO_LUCRO_REAL=0)
alvo = [p for p in M["pros"] if (p["capital"] or 0) >= 10000 and p["cnpj"] not in cache]
alvo.sort(key=lambda p: (-p["similaridade"], p["nivel_geo"], -(p["capital"] or 0)))
print(len(alvo), "a consultar", flush=True); feitos = [0]
def um(p):
    r = subprocess.run(["curl", "-sS", "-m", "20", f"https://minhareceita.org/{p['cnpj']}"], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout); rt = sorted(d.get("regime_tributario") or [], key=lambda x: x.get("ano", 0))
        v = f"{rt[-1]['forma_de_tributacao']} ({rt[-1]['ano']})" if rt else "sem registro"
    except Exception: v = None
    with trava:
        if v: cache[p["cnpj"]] = v
        feitos[0] += 1
        if feitos[0] % 500 == 0:
            json.dump(cache, open(CP + ".tmp", "w")); os.replace(CP + ".tmp", CP); print(feitos[0], "consultados", time.strftime("%H:%M"), flush=True)
    time.sleep(0.3)
with ThreadPoolExecutor(3) as ex: list(ex.map(um, alvo))
json.dump(cache, open(CP + ".tmp", "w")); os.replace(CP + ".tmp", CP); print("fim", feitos[0], flush=True)
