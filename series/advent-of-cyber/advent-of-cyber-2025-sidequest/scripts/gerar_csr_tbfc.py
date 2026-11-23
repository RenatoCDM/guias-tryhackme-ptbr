#!/usr/bin/env python3
"""Gera CSR e chave privada para testar a inscrição no modelo TBFCWEBSERVER.

Uso: python3 gerar_csr_tbfc.py --sid S-1-5-21-...-500 --saida tbfc-admin
Requer: certipy-ad e cryptography no ambiente Python.
"""

import argparse
from pathlib import Path

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from certipy.lib.certificate import create_csr


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sid', required=True, help='SID do Administrator de tbfc.loc')
    parser.add_argument('--saida', default='tbfc-admin', help='Prefixo dos arquivos de saída')
    args = parser.parse_args()

    csr, key = create_csr(
        username='TBFC-SQLSERVER1$',
        alt_dns=None,
        alt_upn='Administrator@tbfc.loc',
        alt_sid=args.sid,
        subject=None,
        key_size=2048,
        application_policies=None,
        smime=None,
    )
    prefix = Path(args.saida)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix('.req').write_bytes(csr.public_bytes(Encoding.PEM))
    private_key = prefix.with_suffix('.key')
    private_key.write_bytes(
        key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    )
    private_key.chmod(0o600)
    print(f'CSR: {prefix.with_suffix(".req")}')
    print(f'Chave privada: {private_key}')


if __name__ == '__main__':
    main()
