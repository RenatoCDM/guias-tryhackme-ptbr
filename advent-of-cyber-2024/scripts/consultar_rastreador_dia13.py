"""Registra eventos Socket.IO do rastreador de carros do dia 13."""

import argparse
import time

import socketio


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("url", help="URL base da Lab Machine")
parser.add_argument("--usuario", required=True, help="userId observado no rastreador")
args = parser.parse_args()

client = socketio.Client(logger=False, engineio_logger=False)


@client.on("*")
def log_event(event, *payload):
    print(event, repr(payload), flush=True)


client.connect(args.url.rstrip("/"), wait_timeout=10)
try:
    client.emit("track", {"userId": args.usuario})
    time.sleep(4)
    client.emit("send_msg", {"txt": "Teste de integridade do rastreador", "sender": args.usuario})
    time.sleep(4)
finally:
    client.disconnect()
