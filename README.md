# Guias de resolução do TryHackMe em português do Brasil

![Coruja cibernética sobre uma nuvem de dados](assets/cyber-owl-social-preview.jpg)

Este repositório ajuda pessoas no Brasil a resolver as tarefas das salas do TryHackMe em português do Brasil. Comandos, mensagens, avisos e saídas dos sistemas permanecem em inglês, como aparecem nos laboratórios.

## Guias

- [Série Advent of Cyber](series/advent-of-cyber/README.md) - guias dos desafios de dezembro do TryHackMe, de 2019 a 2025, incluindo as Side Quests e a sala extra 25 Days of Cyber Security.

## Como usar

Abra a página da série, escolha o ano e, na edição de 2025, selecione o dia ou a Side Quest. Substitua `<IP>` pelo endereço da máquina do seu laboratório. Os guias mostram os procedimentos e máscaras de resposta com dicas entre parênteses, sem revelar os valores completos. Execute os procedimentos apenas em ambientes autorizados.

## Máquina local conectada à VPN

Você pode usar a **AttackBox do TryHackMe** ou uma máquina Linux própria conectada à VPN como máquina de ataque. Recomendamos a máquina própria quando a atividade envolve muitos comandos, ferramentas instaladas ou arquivos que você quer manter: o histórico e o trabalho ficam disponíveis entre sessões e não dependem do tempo de duração da AttackBox. A AttackBox comum também resolve os exercícios, mas, se expirar, arquivos e configurações salvos nela podem ser perdidos. O plano MAX oferece uma [AttackBox persistente](https://help.tryhackme.com/en/articles/6721845-the-attackbox-explained), que retoma arquivos e ferramentas. No plano gratuito, o tempo diário da AttackBox é limitado. Em qualquer opção, inicie a máquina **alvo** quando a tarefa pedir e execute nela os comandos que a sala precisa observar.

Se escolher a máquina própria:

1. Baixe o perfil `.ovpn` da sua região na [página Access do TryHackMe](https://tryhackme.com/access). Conecte uma VM Linux com OpenVPN ou importe o perfil no cliente OpenVPN do Windows. Salas de rede privada podem fornecer um perfil próprio; use o perfil indicado pela sala.
2. Inicie a **Lab Machine** da tarefa e copie o IP exibido nela. Abra um terminal na máquina Linux, confira a rota e teste as portas pertinentes ao exercício (22, 80 e 443 são apenas exemplos):

```bash
export IP=10.x.x.x  # troque pelo IP da Lab Machine
ip route get "$IP"
nmap -Pn -sT -p22,80,443 "$IP"
```

3. Execute cada comando no ambiente indicado pelo guia. Quando a sala precisar observar comandos na máquina alvo, acesse essa máquina e execute-os nela. Para sites internos, use um navegador na máquina que alcança a VPN. Termine a Lab Machine ao concluir a tarefa.

No nosso ambiente, usamos Kali Linux em WSL2 com a VPN conectada no Windows e confirmamos o acesso aos alvos dos exercícios que exigiam rede interna. Essa rota depende da configuração de rede do Windows e do WSL; se não funcionar, use uma VM Linux com OpenVPN diretamente ou a AttackBox do TryHackMe. O [guia oficial de conexão](https://help.tryhackme.com/en/articles/6611809-getting-started-with-openvpn) e as [orientações sobre máquina própria](https://help.tryhackme.com/en/articles/8991559-q-a-common-questions-after-connecting-to-the-vpn) ajudam na configuração. Usar sua VPN não libera salas que exigem assinatura.

Este repositório não é afiliado ao TryHackMe.

## Comunidade e contribuições

Sugestões e correções são bem-vindas por meio dos [relatos](https://github.com/RenatoCDM/guias-tryhackme-ptbr/issues). Leia [Como contribuir](CONTRIBUTING.md) e o [Código de conduta](CODE_OF_CONDUCT.md) antes de participar. Somente o proprietário publica alterações na ramificação `main`; abrir um relato ou uma proposta de alteração não concede acesso de escrita ao repositório.

Para relatar uma falha em um script, consulte a [Política de segurança](SECURITY.md). Barreiras de leitura podem ser relatadas conforme a [Declaração de acessibilidade](ACCESSIBILITY.md).

## Licenças

Os textos originais dos guias e da documentação estão sob [Creative Commons Attribution 4.0 International](LICENSE) (CC BY 4.0): é permitida a reutilização e adaptação com crédito e indicação de mudanças. Os scripts originais nas pastas `scripts/` estão sob a [licença MIT](LICENSE-SCRIPTS).

Essas licenças não abrangem marcas, logotipos, capturas de tela, arquivos ou outros materiais de terceiros, incluindo conteúdos do TryHackMe. Cada titular conserva os direitos sobre seus próprios materiais.
