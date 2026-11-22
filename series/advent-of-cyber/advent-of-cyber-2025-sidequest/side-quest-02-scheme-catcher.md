# Side Quest 2 - Scheme Catcher

Este guia acompanha a sala [Scheme Catcher](https://tryhackme.com/room/sq2-aoc2025-JxiOKUSD9R), do Advent of Cyber 2025. A missão combina descoberta de uma chave, engenharia reversa e exploração de memória. Use uma máquina Linux conectada à VPN do TryHackMe. Inicie a Lab Machine e substitua o IP abaixo pelo da sua instância.

```bash
export IP=10.x.x.x
mkdir -p scheme-catcher && cd scheme-catcher
nmap -Pn -sT -n -sV -p- --open "$IP"
```

## 1. Abrir a missão e descobrir o primeiro estágio

O acesso à Side Quest vem do desafio opcional do dia 9. Na VM daquele dia, localize o banco KeePass `Passwords.kdbx`, extraia seu hash e teste uma lista de palavras:

```bash
keepass2john Passwords.kdbx > keepass.hash
john --wordlist=/usr/share/wordlists/rockyou.txt keepass.hash
keepassxc-cli ls Passwords.kdbx
keepassxc-cli show -s Passwords.kdbx Key
```

O registro `Key` contém uma imagem anexada. Exporte-a pelo `keepassxc-cli attachment-export` e leia a chave de acesso. Na Side Quest, abra o serviço da porta `21337` e forneça a chave para remover a barreira inicial.

Depois, enumere os arquivos publicados pelo serviço HTTP. O pacote de atualização `4.2.0.zip` fica em `/dev/`. Baixe e inspecione o conteúdo antes de executá-lo:

```bash
curl -fsS "http://$IP/dev/4.2.0.zip" -o 4.2.0.zip
unzip -l 4.2.0.zip
unzip 4.2.0.zip
file latest/beacon.bin
strings -a latest/beacon.bin | less
```

O binário contém uma seção de código que se decifra em tempo de execução. Com `readelf -S`, `objdump -d` e `gdb`, identifique a rotina que aplica XOR aos bytes da seção `.easter` e examine o resultado após a decifração. No fluxo de mensagens do executável aparece a primeira flag.

Resposta: `THM{...}`

## 2. Seguir a trilha deixada pelo beacon

As strings e as rotinas do `beacon.bin` indicam um caminho Web pouco evidente. Consulte esse caminho na aplicação do laboratório; ele contém `foothold.txt` e o arquivo ZIP do segundo estágio. Não use um scanner de diretórios como única fonte: o próprio binário fornece a pista.

```bash
curl -fsS "http://$IP/<CAMINHO_IDENTIFICADO>/foothold.txt"
curl -fsS "http://$IP/<CAMINHO_IDENTIFICADO>/stage2.zip" -o stage2.zip
unzip -l stage2.zip
unzip stage2.zip
file server libc.so.6 ld-linux-x86-64.so.2
checksec --file=server
```

O `foothold.txt` entrega a segunda flag. O ZIP inclui o serviço vulnerável e as versões de `libc` e do carregador usadas pelo alvo, fundamentais para reproduzir os offsets da exploração.

Resposta: `THM{...}`

## 3. Analisar a falha de heap

O serviço do segundo estágio responde na porta `9004`. Faça alguns testes manuais com `nc` para mapear o menu e compare as opções com o desassemblado do `server`.

```bash
nc "$IP" 9004
objdump -d -M intel server | less
readelf -Ws libc.so.6 | grep -E '_IO_2_1_stdout_| exit@@'
```

As operações **create**, **update** e **delete** manipulam uma tabela de objetos no heap. Após liberar um objeto, a opção de atualização ainda aceita um índice que referencia sua antiga região: essa é a condição de *use after free*. A exploração precisa, nesta ordem:

1. Preparar as classes de tamanho do alocador e liberar um bloco suficientemente grande para produzir um vazamento de ponteiros.
2. Reutilizar a entrada antiga com `update` para observar os endereços do heap e da `libc`.
3. Calcular a base da `libc` com os símbolos da versão fornecida, sem usar offsets de outra distribuição.
4. Construir uma estrutura `_IO_FILE` falsa e redirecionar o ponteiro de `stdout` para ela. Essa técnica é conhecida como *FSOP*.
5. Acionar a saída do processo e repetir somente quando a tentativa falhar por causa dos bits aleatórios dos endereços. O espaço de busca observado no laboratório foi de 16 candidatos para o heap e 16 para a `libc`.

Ao obter uma sessão no contêiner, confirme o usuário e leia `user.txt` para a terceira flag:

```bash
id
cat user.txt
```

Resposta: `THM{...}`

## 4. Alcançar o host a partir do contêiner

Enumere os dispositivos e montagens. O contêiner concede privilégios suficientes para montar o sistema de arquivos do host, visível no laboratório como `/dev/nvme0n1p1`:

```bash
lsblk
mount | head
mkdir -p /mnt/host
mount /dev/nvme0n1p1 /mnt/host
cat /mnt/host/root/root.txt
```

O último arquivo contém a quarta flag. Envie as quatro respostas aos respectivos campos da sala, com alguns segundos entre submissões, e confira o progresso de 100%.

Resposta: `THM{...}`
