"""Extract one TCP direction from a local PCAP using TShark's reassembly."""
import argparse
import subprocess
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("pcap", type=Path)
parser.add_argument("stream", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()

result = subprocess.run(
    ["tshark", "-r", str(args.pcap), "-q", "-z", f"follow,tcp,raw,{args.stream}"],
    capture_output=True,
    text=True,
    check=True,
)
lines = result.stdout.splitlines()
node = 0
data = bytearray()
for line in lines:
    if line.startswith("Node 0:"):
        node = 0
    elif line.startswith("Node 1:"):
        node = 1
    elif line.startswith("=" * 20) or line.startswith("Follow:") or line.startswith("Filter:"):
        continue
    elif line.startswith("\t"):
        # TShark indents traffic in the reverse direction.
        continue
    else:
        try:
            data.extend(bytes.fromhex(line.strip()))
        except ValueError:
            pass
args.output.write_bytes(data)
print(f"{len(data)} bytes -> {args.output}")
