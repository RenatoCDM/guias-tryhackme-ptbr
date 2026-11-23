# Dia 2 - Phishing: Merry Clickmas

Este guia acompanha a sala [Phishing - Merry Clickmas](https://tryhackme.com/room/phishing-aoc2025-h2tkye9fzU). Faça o teste somente no ambiente fictício da sala. Você pode usar a AttackBox ou uma máquina própria conectada à VPN do TryHackMe. A máquina própria preserva arquivos e histórico entre sessões; veja as [opções de conexão](../../../README.md#máquina-local-conectada-à-vpn).

## Preparar a página de treinamento

Inicie a Lab Machine e anote o IP do Roundcube. Baixe o pacote oferecido na tarefa e extraia `server.py` e `index.html` na mesma pasta. Leia o início de `server.py` para confirmar a porta HTTP e onde ele grava as credenciais recebidas. No terminal da máquina de ataque:

```bash
mkdir -p ~/aoc2025/dia02
cd ~/aoc2025/dia02
unzip "$HOME/Downloads/arquivo-da-sala.zip"  # use o nome do ZIP baixado
ls -la
python3 server.py
```

Mantenha esse terminal aberto. Em outro terminal, teste `curl -I http://<IP_DA_MAQUINA_DE_ATAQUE>:8000/`. A página precisa ser alcançável pela VM alvo. Se você usa WSL ou outra VM local, confira o encaminhamento da porta 8000 entre sua interface VPN e o processo Python antes de enviar a mensagem.

## Enviar o e-mail e observar a captura

Abra o Social-Engineer Toolkit (`setoolkit`) e siga a sequência da sala para um envio de e-mail: **Social-Engineering Attacks → Mass Mailer Attack → E-Mail Attack Single Email Address**. Use o destinatário fictício `factory@wareville.thm`, o SMTP da Lab Machine na porta 25 e, no corpo, o endereço HTTP da sua página na porta 8000. O remetente e o assunto podem seguir o exemplo mostrado na tarefa.

```bash
sudo setoolkit
```

Volte ao terminal de `server.py`. Aguarde o acesso à página e o envio do formulário. Leia o arquivo de captura indicado pelo script; ele mostra a conta usada e a senha fornecida ao portal de treinamento. Submeta a senha à primeira pergunta.

Se o SET não conseguir completar o envio no seu ambiente, o [script de e-mail do laboratório](scripts/dia02-email-laboratorio.py) envia uma única mensagem ao SMTP fictício da sala. Ele não substitui o estudo do fluxo no SET. Execute com o IP da sua VM e um endereço que ela consiga alcançar:

```bash
python3 scripts/dia02-email-laboratorio.py \
  --smtp-host 10.x.x.x \
  --landing-url http://10.y.y.y:8000/
```

Resposta 1: `un...` (senha)

## Confirmar a reutilização no Roundcube

Abra `http://<IP_DA_LAB_MACHINE>/` na máquina conectada à VPN. Entre no Roundcube com a conta `factory` e a senha capturada. Procure a mensagem de Marta sobre a remessa e leia a quantidade de brinquedos prevista para entrega. Insira o número, sem separadores, no segundo campo. Marque a tarefa final que não pede texto.

Resposta 2: `#######` (número inteiro)
