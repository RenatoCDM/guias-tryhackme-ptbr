"""Envia um único e-mail da campanha fictícia do dia 2 ao SMTP do laboratório."""

import argparse
import smtplib
from email.message import EmailMessage


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--smtp-host', required=True, help='IP da Lab Machine')
parser.add_argument('--landing-url', required=True, help='URL HTTP da página de treino')
args = parser.parse_args()

msg = EmailMessage()
msg['From'] = 'Flying Deer <updates@flyingdeer.thm>'
msg['To'] = 'factory@wareville.thm'
msg['Subject'] = 'Shipping Schedule Changes'
msg.set_content(
    'Dear factory team,\n\n'
    f'Please confirm the updated shipping schedule at {args.landing_url} '
    'before dispatch.\n\nBest regards,\nFlying Deer\n'
)

with smtplib.SMTP(args.smtp_host, 25, timeout=20) as smtp:
    smtp.send_message(msg)

print('Mensagem enviada ao SMTP fictício do laboratório.')
