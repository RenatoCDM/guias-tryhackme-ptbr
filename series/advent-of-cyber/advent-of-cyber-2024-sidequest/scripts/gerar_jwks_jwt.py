#!/usr/bin/env python3
"""Gera uma chave RSA, um JWKS público e um JWT para o T5."""

import argparse
import base64
import json
import os
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def b64url_inteiro(numero: int) -> str:
    dados = numero.to_bytes((numero.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pasta", type=Path, help="Diretório onde gravar os três arquivos")
    parser.add_argument("--usuario", default="mcskidy-adm")
    parser.add_argument("--kid", default="sidequest-t5")
    args = parser.parse_args()
    args.pasta.mkdir(parents=True, exist_ok=True)

    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    privada = chave.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    numeros = chave.public_key().public_numbers()
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "kid": args.kid,
                "use": "sig",
                "alg": "RS256",
                "n": b64url_inteiro(numeros.n),
                "e": b64url_inteiro(numeros.e),
            }
        ]
    }

    caminho_chave = args.pasta / "jwt.key"
    caminho_chave.write_bytes(privada)
    os.chmod(caminho_chave, 0o600)
    (args.pasta / "jwks.json").write_text(json.dumps(jwks), encoding="utf-8")
    token = jwt.encode(
        {"username": args.usuario},
        privada,
        algorithm="RS256",
        headers={"kid": args.kid},
    )
    (args.pasta / "token.txt").write_text(token, encoding="utf-8")
    print(f"Arquivos gerados em {args.pasta}")


if __name__ == "__main__":
    main()
