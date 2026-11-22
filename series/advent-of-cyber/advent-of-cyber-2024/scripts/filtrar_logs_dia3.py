"""Mostra requisições interessantes do índice Frosty Pines no laboratório."""

import argparse
import json
import urllib.parse
import urllib.request


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("host", help="IP ou hostname da Lab Machine")
parser.add_argument("--inicio", default="2024-10-03T10:30:00Z")
parser.add_argument("--fim", default="2024-10-03T11:00:00Z")
args = parser.parse_args()

params = urllib.parse.urlencode({"path": "frostypines-resorts/_search", "method": "GET"})
query = {
    "size": 500,
    "_source": ["@timestamp", "request", "clientip", "verb", "response"],
    "query": {"range": {"@timestamp": {"gte": args.inicio, "lte": args.fim}}},
    "sort": [{"@timestamp": "asc"}],
}
url = f"http://{args.host}:5601/api/console/proxy?{params}"
request = urllib.request.Request(
    url,
    data=json.dumps(query).encode(),
    headers={"kbn-xsrf": "true", "Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=20) as response:
    hits = json.load(response)["hits"]["hits"]

for hit in hits:
    item = hit["_source"]
    path = item.get("request", "")
    if path.startswith("/phpmyadmin") or path.endswith((".css", ".js", ".png", ".jpg", ".svg")):
        continue
    if item.get("verb") == "POST" or "?" in path or "upload" in path.lower():
        print(item.get("@timestamp"), item.get("clientip"), item.get("verb"), path, item.get("response"))
