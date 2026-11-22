param(
    [Parameter(Mandatory = $true)][string]$Conta,
    [Parameter(Mandatory = $true)][int]$Evento
)

$xpath = "*[System[(EventID=$Evento)]] and *[EventData[Data[@Name='TargetUserName']='$Conta']]"
$logons = Get-WinEvent -LogName Security -FilterXPath $xpath -MaxEvents 20 -ErrorAction SilentlyContinue
foreach ($entry in $logons) {
    Write-Output ("LOGON {0:dd/MM/yyyy HH:mm:ss} ID={1}" -f $entry.TimeCreated, $entry.Id)
}

$events = Get-WinEvent -LogName 'Windows PowerShell' -MaxEvents 500 -ErrorAction SilentlyContinue
$commands = foreach ($entry in $events) {
    if ($entry.Message -match [regex]::Escape($Conta) -or
        $entry.Message -match 'Set-ADAccountPassword|New-ADUser|net user') {
        $entry.Message -split '\r?\n' |
            Where-Object { $_ -match '^\s*HostApplication=' } |
            ForEach-Object { $_.Trim() }
    }
}
$commands | Sort-Object -Unique | ForEach-Object { Write-Output "PSLOG $_" }
