<#
.SYNOPSIS
Encaminha uma porta TCP da interface VPN do Windows para um serviço no WSL2.

.EXAMPLE
.\vpn-wsl-relay.ps1 -VpnAddress 192.168.151.58 -WslAddress 172.20.229.149 -Port 4445

Encerre com Ctrl+C ao terminar o laboratório. Use somente endereços da VPN
e da instância WSL local. O IP do WSL pode mudar após reiniciar o subsistema.
#>
param(
    [Parameter(Mandatory = $true)][string]$VpnAddress,
    [Parameter(Mandatory = $true)][string]$WslAddress,
    [Parameter(Mandatory = $true)][ValidateRange(1, 65535)][int]$Port
)

$ErrorActionPreference = 'Stop'
$listenIp = [Net.IPAddress]::Parse($VpnAddress)
$targetIp = [Net.IPAddress]::Parse($WslAddress)
$listener = [Net.Sockets.TcpListener]::new($listenIp, $Port)
$listener.Start()
Write-Host "Encaminhando $VpnAddress`:$Port para $WslAddress`:$Port"

try {
    while ($true) {
        $incoming = $listener.AcceptTcpClient()
        $outgoing = $null
        try {
            $outgoing = [Net.Sockets.TcpClient]::new($targetIp.ToString(), $Port)
            $fromLab = $incoming.GetStream()
            $toWsl = $outgoing.GetStream()
            $upload = $fromLab.CopyToAsync($toWsl)
            $download = $toWsl.CopyToAsync($fromLab)
            [Threading.Tasks.Task]::WhenAny($upload, $download).GetAwaiter().GetResult() | Out-Null
        }
        finally {
            if ($outgoing) { $outgoing.Dispose() }
            $incoming.Dispose()
        }
    }
}
finally {
    $listener.Stop()
}
