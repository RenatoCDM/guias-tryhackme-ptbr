#!/usr/bin/env python3
"""Recupera a senha Hopflix da base SQLite exposta na Side Quest 4.

Uso: python3 recuperar_senha_hopflix.py hopflix.db
"""

import hashlib
import sqlite3
import string
import sys
from pathlib import Path


def hopper_hash(character: str, rounds: int) -> str:
    digest = character
    for _ in range(rounds):
        digest = hashlib.sha1(digest.encode()).hexdigest()
    return digest


def recover(database: Path) -> tuple[str, str]:
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT email, password_hash FROM users LIMIT 1"
        ).fetchone()
    if row is None:
        raise ValueError("A tabela users não contém uma conta")

    email, combined_hash = row
    if len(combined_hash) % 40:
        raise ValueError("O hash não é uma sequência de SHA-1 de 40 caracteres")

    alphabet = string.ascii_letters + string.digits + string.punctuation + " "
    parts = [combined_hash[start : start + 40] for start in range(0, len(combined_hash), 40)]
    # A base e a aplicação podem usar contagens de iterações diferentes.
    for rounds in (1000, 5000):
        by_digest = {hopper_hash(character, rounds): character for character in alphabet}
        if all(part in by_digest for part in parts):
            return email, "".join(by_digest[part] for part in parts)
    raise ValueError("Nenhuma contagem de iterações conhecida decodificou o hash")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python3 recuperar_senha_hopflix.py <arquivo.db>")
    email, password = recover(Path(sys.argv[1]))
    print(f"E-mail: {email}")
    print(f"Senha: {password}")


if __name__ == "__main__":
    main()
