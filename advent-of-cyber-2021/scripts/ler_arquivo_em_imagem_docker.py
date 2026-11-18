#!/usr/bin/env python3
"""Lê um arquivo das camadas de um docker-archive sem iniciar o contêiner.

Uso: python3 ler_arquivo_em_imagem_docker.py imagem.tar \
         --path root/envconsul/config.hcl
"""

import argparse
import sys
import tarfile
from pathlib import Path


def nome_relativo(nome: str) -> str:
    """Normaliza apenas o nome da entrada; nenhum arquivo é extraído no disco."""
    while nome.startswith("./"):
        nome = nome[2:]
    return nome.lstrip("/")


def ler_ultima_versao(imagem: Path, caminho: str) -> bytes | None:
    """Percorre os layer.tar na ordem do arquivo e conserva a última ocorrência."""
    encontrado = None
    with tarfile.open(imagem, mode="r|*") as exterior:
        for camada in exterior:
            nome_camada = nome_relativo(camada.name)
            if not camada.isfile() or not (
                nome_camada == "layer.tar" or nome_camada.endswith("/layer.tar")
            ):
                continue
            fluxo = exterior.extractfile(camada)
            if fluxo is None:
                continue
            with fluxo, tarfile.open(fileobj=fluxo, mode="r|*") as interior:
                for entrada in interior:
                    if entrada.isfile() and nome_relativo(entrada.name) == caminho:
                        arquivo = interior.extractfile(entrada)
                        if arquivo is not None:
                            encontrado = arquivo.read()
    return encontrado


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("imagem", type=Path, help="arquivo criado por docker save ou skopeo docker-archive")
    parser.add_argument(
        "--path",
        default="root/envconsul/config.hcl",
        help="caminho dentro da imagem (padrão: %(default)s)",
    )
    args = parser.parse_args()
    alvo = nome_relativo(args.path)

    try:
        conteudo = ler_ultima_versao(args.imagem, alvo)
    except (OSError, tarfile.TarError) as erro:
        parser.exit(2, f"Erro ao ler a imagem: {erro}\n")
    if conteudo is None:
        parser.exit(1, f"Arquivo não encontrado nas camadas: {alvo}\n")

    sys.stdout.buffer.write(conteudo)
    if not conteudo.endswith(b"\n"):
        sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
