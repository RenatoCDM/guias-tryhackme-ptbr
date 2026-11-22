# Dia 1 - Linux CLI: Shells Bells

Este guia acompanha a sala [Linux CLI - Shells Bells](https://tryhackme.com/room/linuxcli-aoc2025-o1fpqkvxti) do Advent of Cyber 2025. Os comandos devem ser executados **na máquina alvo da sala**, na ordem em que aparecem. Se você usa uma máquina Linux própria conectada à VPN, entre na Lab Machine por SSH e execute os comandos nessa sessão. Executá-los somente no Kali local não produz os arquivos nem os eventos observados pela sala.

## Preparação

Inicie **Start Lab Machine** no TryHackMe e copie o IP. A tarefa 1 mostra as credenciais SSH de `mcskidy`. Na sua máquina conectada à VPN, entre no alvo:

```bash
export IP=10.x.x.x  # substitua pelo IP da sua Lab Machine
ssh mcskidy@"$IP"
```

Digite a senha exibida na tarefa 1. Espere a VM terminar de iniciar se o SSH ainda não responder. Depois de entrar, confirme a tarefa introdutória na página da sala.

## Primeiros comandos e o guia escondido

Execute cada linha abaixo em sequência. `README.txt` orienta a procurar o diretório `Guides`; `ls -la` revela arquivos cujo nome começa com ponto:

```bash
echo "Hello World!"
ls
cat README.txt
pwd
cd Guides
ls
ls -la
cat .guide.txt
```

O comando que lista o diretório responde à primeira pergunta. Leia a flag na saída de `.guide.txt` para responder à segunda. O próprio arquivo orienta a investigar os logs e os arquivos relacionados a `egg`.

Resposta 1: `l...`

Resposta 2: `THM{...}`

## Logs e script Eggstrike

Continue na mesma sessão, mantendo a ordem dos exercícios:

```bash
cd /var/log
ls
grep "Failed password" auth.log
find /home/socmas -name '*egg*'
cd /home/socmas/2025
cat eggstrike.sh
```

`grep` é a resposta sobre a filtragem dos logins com falha. O caminho encontrado por `find` aponta para `eggstrike.sh`; leia o script, inclusive seus comentários, para localizar a segunda flag. Observe também o que ele faz com `wishlist.txt` e `eastmas.txt`: o script copia e organiza os pedidos, remove o arquivo original e coloca a lista falsa no lugar.

Resposta 3: `gr...`

Resposta 4: `THM{...}`

## Permissões, root e histórico

Os próximos comandos mostram informações do sistema e demonstram a diferença entre o usuário comum e `root`:

```bash
uptime
ip addr
ps aux
cat /etc/shadow
sudo su
whoami
history
cd /root
cat .bash_history
```

O primeiro `cat /etc/shadow` deve falhar por falta de permissão. O comando de troca para `root` responde à quinta pergunta. Procure a terceira flag no histórico exibido por `cat .bash_history`, sem executar os comandos suspeitos que encontrar ali. As tarefas finais de leitura complementar não exigem texto como resposta: abra a nota solicitada e marque **Check**.

Resposta 5: `sud...`

Resposta 6: `THM{...}`

## Desafio opcional: chave da Side Quest 1

Na nota escondida em `/home/mcskidy/Documents/`, leia a conta de teste e as três pistas. Elas apontam, nesta ordem, para uma variável de ambiente, uma versão antiga no histórico Git e o fim de um arquivo em `Pictures`. Volte do shell de `root` com `exit` e entre na conta informada pela nota. Use a senha indicada nela.

```bash
cat /home/mcskidy/Documents/read-me-please.txt
exit
su - eddi_knapp
printenv | grep PASSFRAG
cat .pam_environment
git -C .secret_git log --oneline --all
git -C .secret_git show <COMMIT_ANTIGO>:secret_note.txt
tail -n 8 Pictures/.easter_egg
```

Junte os três fragmentos exatamente como aparecem, inclusive hífens e diferenças de maiúsculas e minúsculas. Use a combinação para ler a nota cifrada. Ela fornece a lista correta de dez itens e a chave para decifrar a mensagem do site.

```bash
gpg --batch --pinentry-mode loopback \
  --passphrase '<TRES_FRAGMENTOS_JUNTOS>' \
  --decrypt ~/Documents/mcskidy_note.txt.gpg
```

Na pasta `/home/socmas/2025`, substitua `wishlist.txt` **pelas dez linhas exatas da nota**, uma por linha. O arquivo permite escrita à conta usada nesta etapa. Confira a grafia antes de continuar:

```bash
nano /home/socmas/2025/wishlist.txt
# Insira as dez linhas reveladas pela nota, salve e saia do editor.
wc -l /home/socmas/2025/wishlist.txt
```

Em seguida, abra `http://<IP>:8080/` ou consulte a API indicada no código da página. O resultado é uma mensagem cifrada em Base64. Decodifique-a usando os parâmetros do `openssl` mostrados na nota:

```bash
curl -s "http://<IP>:8081/secret" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["text"])' \
  | base64 -d \
  | openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -salt \
      -pass 'pass:<CHAVE_DA_NOTA>'
```

A mensagem decifrada fornece uma flag intermediária. Use-a como senha para abrir o arquivo GPG em `/home/eddi_knapp/.secret/`. Extraia o `tar.gz` e abra a imagem resultante. O texto impresso na imagem é a chave de entrada da [Side Quest 1](../advent-of-cyber-2025-sidequest/side-quest-01-the-great-disappearing-act.md).

```bash
gpg --batch --pinentry-mode loopback \
  --passphrase '<FLAG_INTERMEDIARIA>' \
  --output /tmp/sidequest1.tar.gz \
  --decrypt /home/eddi_knapp/.secret/dir.tar.gz.gpg
tar -tzf /tmp/sidequest1.tar.gz
tar -xzf /tmp/sidequest1.tar.gz -C /tmp
```
