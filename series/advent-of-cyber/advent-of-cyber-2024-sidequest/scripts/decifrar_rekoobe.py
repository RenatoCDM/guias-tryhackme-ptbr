"""Inspect TinySHell packet encryption in the AoC24 SQ1 capture."""
import argparse
import hashlib
import hmac
import subprocess

from Crypto.Cipher import AES


class Direction:
    def __init__(self, secret: bytes, iv: bytes):
        material = hashlib.sha1(secret + iv).digest()
        self.aes = AES.new(material[:16], AES.MODE_ECB)
        self.ipad = bytes((material[i] ^ 0x36) if i < 20 else 0x36 for i in range(64))
        self.opad = bytes((material[i] ^ 0x5C) if i < 20 else 0x5C for i in range(64))
        self.last = iv[:16]
        self.counter = 0

    def decrypt(self, packet: bytes):
        if len(packet) < 36 or (len(packet) - 20) % 16:
            return None
        cipher, tag = packet[:-20], packet[-20:]
        for count in range(max(0, self.counter - 2), self.counter + 10):
            num = count.to_bytes(4, "big")
            digest = hashlib.sha1(self.opad + hashlib.sha1(self.ipad + cipher + num).digest()).digest()
            if not hmac.compare_digest(tag, digest):
                continue
            prev = self.last
            plain = bytearray()
            for pos in range(0, len(cipher), 16):
                block = cipher[pos : pos + 16]
                plain.extend(a ^ b for a, b in zip(self.aes.decrypt(block), prev))
                prev = block
            self.last = prev
            self.counter = count + 1
            size = int.from_bytes(plain[:2], "big")
            return bytes(plain[2 : 2 + size])
        return None


parser = argparse.ArgumentParser()
parser.add_argument("capture", help="Arquivo PCAP do laboratório")
parser.add_argument("secret", help="Chave de comunicação obtida do binário ff")
args = parser.parse_args()
capture = args.capture
rows = subprocess.check_output(
    [
        "tshark", "-r", capture, "-Y", "tcp.port == 9001", "-T", "fields",
        "-e", "frame.number", "-e", "ip.src", "-e", "tcp.srcport",
        "-e", "tcp.dstport", "-e", "tcp.payload",
    ], text=True
).splitlines()
records = []
for row in rows:
    cols = row.split("\t")
    if len(cols) != 5 or not cols[4]:
        continue
    records.append((int(cols[0]), cols[1], int(cols[2]), int(cols[3]), bytes.fromhex(cols[4])))

first = next(item for item in records if len(item[4]) == 40 and item[3] == 9001)
client_ip = first[1]
secret = args.secret.encode()
client = Direction(secret, first[4][:20])
server = Direction(secret, first[4][20:])
print("IV frame:", first[0], "client:", client_ip)
for frame, src, sport, dport, payload in records:
    if frame <= first[0]:
        continue
    context = client if src == client_ip else server
    decoded = context.decrypt(payload)
    if decoded:
        text = decoded.decode("utf-8", errors="replace")
        if any(c.isprintable() and c.isalpha() for c in text):
            print(frame, "C->S" if src == client_ip else "S->C", repr(text[:300]))
