#!/usr/bin/env python3
"""Testa as senhas recomendadas depois de passá-las pelo enc do laboratório."""
import subprocess
import sys
import pyzipper


if len(sys.argv) != 4:
    raise SystemExit(f"Uso: {sys.argv[0]} <enc> <lista> <arquivo.zip>")

binary, wordlist, archive = sys.argv[1:]
with pyzipper.AESZipFile(archive) as zipped:
    target = min(
        (item for item in zipped.infolist() if not item.is_dir()),
        key=lambda item: item.file_size,
    )
    with open(wordlist, encoding="utf-8", errors="replace") as words:
        for number, line in enumerate(words, 1):
            original = line.strip()
            result = subprocess.run(
                [binary, original], capture_output=True, text=True, check=True
            )
            candidate = result.stdout.strip().encode()
            try:
                zipped.read(target, pwd=candidate)
            except (RuntimeError, pyzipper.BadZipFile, ValueError):
                continue
            print(f"Linha {number}: {original} -> {candidate.decode()}")
            break
        else:
            raise SystemExit("Nenhuma senha da lista abriu o ZIP")
