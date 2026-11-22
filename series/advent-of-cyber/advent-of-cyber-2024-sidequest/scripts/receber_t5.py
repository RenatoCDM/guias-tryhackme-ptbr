#!/usr/bin/env python3
"""Recebe callbacks e arquivos enviados pelos contêineres do laboratório T5."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--escuta", default="0.0.0.0")
    parser.add_argument("--porta", type=int, default=8001)
    parser.add_argument("--saida", type=Path, default=Path("recebido.bin"))
    args = parser.parse_args()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            url = urlparse(self.path)
            print(url.path, parse_qs(url.query), flush=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def do_POST(self) -> None:
            tamanho = int(self.headers.get("Content-Length", "0"))
            args.saida.write_bytes(self.rfile.read(tamanho))
            print(f"Recebidos {tamanho} bytes em {args.saida}", flush=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

    ThreadingHTTPServer((args.escuta, args.porta), Handler).serve_forever()


if __name__ == "__main__":
    main()
