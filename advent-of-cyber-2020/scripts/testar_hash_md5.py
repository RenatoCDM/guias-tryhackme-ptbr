#!/usr/bin/env python3
"""Testa localmente um hash MD5 contra uma lista de palavras."""

import argparse
import gzip
import hashlib
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hash", help="Hash MD5 encontrado no banco do laboratório")
    parser.add_argument("wordlist", type=Path, help="Lista local, em texto ou .gz")
    args = parser.parse_args()

    if len(args.hash) != 32 or any(c not in "0123456789abcdefABCDEF" for c in args.hash):
        parser.error("O hash MD5 deve conter 32 caracteres hexadecimais")

    opener = gzip.open if args.wordlist.suffix == ".gz" else open
    with opener(args.wordlist, "rb") as words:
        for number, raw in enumerate(words, 1):
            candidate = raw.rstrip(b"\r\n")
            if hashlib.md5(candidate).hexdigest() == args.hash.lower():
                print(f"Correspondência na linha {number}: {candidate.decode('utf-8', errors='replace')}")
                return
    print("Nenhuma correspondência na lista informada.")


if __name__ == "__main__":
    main()
