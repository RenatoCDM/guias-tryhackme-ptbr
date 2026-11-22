#!/usr/bin/env python3
"""Baixa os primeiros segmentos de um ticket HLS da Side Quest 1."""

import argparse
from pathlib import Path
from urllib.parse import urljoin

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ip", help="IP da Lab Machine")
    parser.add_argument("token", help="token Bearer recebido no login do portal")
    parser.add_argument("ticket", help="ticket_id de acesso ao fluxo")
    parser.add_argument("output", type=Path, help="arquivo .ts de saída")
    args = parser.parse_args()

    base = f"http://{args.ip}:13401"
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {args.token}"
    manifest_url = f"{base}/v1/streams/{args.ticket}/manifest.m3u8"
    response = session.get(manifest_url, timeout=15)
    response.raise_for_status()
    segments = [
        line.strip()
        for line in response.text.splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if len(segments) < 2:
        raise RuntimeError("O manifesto não contém dois segmentos de vídeo")

    with args.output.open("wb") as output:
        for segment in segments[:2]:
            url = urljoin(base, segment)
            with session.get(url, stream=True, timeout=30) as source:
                source.raise_for_status()
                for block in source.iter_content(65536):
                    output.write(block)
    print(f"Vídeo salvo em {args.output}")


if __name__ == "__main__":
    main()
