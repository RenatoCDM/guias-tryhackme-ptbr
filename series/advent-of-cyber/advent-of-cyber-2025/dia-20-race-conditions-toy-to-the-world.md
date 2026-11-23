# Dia 20 - Race Conditions: Toy to The World

Este guia acompanha [Race Conditions - Toy to The World](https://tryhackme.com/room/race-conditions-aoc2025-d7f0g3h6j9). Inicie a Lab Machine, anote o IP e conecte a Kali pela VPN do TryHackMe. A AttackBox da plataforma também serve para estes passos. Uma Kali local conserva o histórico e os arquivos caso o tempo da AttackBox se esgote.

## Confirmar o fluxo normal da loja

Abra `http://<IP_DA_LAB_MACHINE>/` e entre com `attacker` / `attacker@123`, as credenciais de teste da sala. Na página da loja, anote o estoque inicial do **SleighToy Limited Edition** e do **Bunny Plush (Blue)**. Acrescente um SleighToy ao carrinho, abra o checkout e clique em **Confirm & Pay**. A requisição usada é `POST /process_checkout`; a resposta JSON deve conter `status: confirmed`, `stock_before` e `stock_after`.

Resposta 1 da tarefa 1: clique em **Check** após confirmar a conexão com a máquina.

## Reproduzir a condição de corrida

A aplicação verifica a disponibilidade e atualiza o estoque em etapas separadas. Com várias requisições usando o mesmo carrinho e cookie de sessão, checkouts simultâneos podem passar pela verificação antes que os demais abatam o estoque. A própria sala demonstra isso com o Burp Repeater e **Send group in parallel (last-byte sync)**.

O [script de checkout paralelo](scripts/dia20-checkout-paralelo.py), criado para este laboratório, reproduz o fluxo pela Kali usando Python e `requests`. Ele faz um pedido normal, adiciona outra unidade ao carrinho e sincroniza até 16 requisições `POST /process_checkout` por uma barreira de threads. Instale `requests` em um ambiente virtual se ele não estiver disponível:

```bash
python3 -m venv .venv
.venv/bin/pip install requests
.venv/bin/python scripts/dia20-checkout-paralelo.py --ip 10.x.x.x --produto sled-101
```

Volte à loja após o teste. O estoque pode ter um valor surpreendente por causa de atualizações concorrentes; observe os pedidos e procure a mensagem **Flag Found** no HTML da loja. Se ela ainda não aparecer, repita o teste com outra leva de requisições enquanto houver estoque. O script mostra os indicadores encontrados na página ao final.

Resposta 1 da tarefa 2: `THM{WIN...}` (flag exibida após explorar o SleighToy)

## Repetir com o segundo produto

Execute o mesmo fluxo para o código `plush-001`. O script inicia uma nova sessão laboratorial e repete o pedido normal antes das requisições simultâneas:

```bash
.venv/bin/python scripts/dia20-checkout-paralelo.py --ip 10.x.x.x --produto plush-001
```

Confira a segunda mensagem **Flag Found** na loja e marque a pergunta final sem resposta. A correção para a vulnerabilidade, discutida na sala, combina uma transação atômica no banco, nova verificação de estoque antes da confirmação e tratamento idempotente do checkout.

Resposta 2 da tarefa 2: `THM{WIN...}` (flag exibida após explorar o Bunny Plush)
