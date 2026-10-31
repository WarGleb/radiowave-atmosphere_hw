param([string]$Action, [string]$Dz)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
$csv = 'worklog.csv'
$msk = [TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, 'UTC', 'Russian Standard Time')
$stamp = $msk.ToString('yyyy-MM-dd HH:mm')
if (-not (Test-Path $csv)) { 'dz,start,end' | Set-Content $csv -Encoding ASCII }
$rows = @(Import-Csv $csv)
$open = @($rows | Where-Object { -not $_.end })

if ($Action -eq 'start') {
    if ($open.Count -gt 0) {
        Write-Host "Vy uzhe nachali rabotu v $($open[-1].start) ($($open[-1].dz)). Snachala zapustite stop.bat." -ForegroundColor Yellow
        exit 1
    }
    if (-not $Dz) { $Dz = Read-Host 'Nomer zadaniya (naprimer dz1)' }
    Add-Content $csv "$Dz,$stamp," -Encoding ASCII
    $msg = "start $Dz $stamp MSK"
}
elseif ($Action -eq 'stop') {
    if ($open.Count -eq 0) {
        Write-Host 'Net nachatoy raboty. Snachala zapustite start.bat.' -ForegroundColor Yellow
        exit 1
    }
    $open[-1].end = $stamp
    $rows | Export-Csv $csv -NoTypeInformation -Encoding ASCII
    $msg = "stop $($open[-1].dz) $stamp MSK"
}
else { Write-Host 'Usage: worklog.ps1 start|stop [dz]'; exit 1 }

git add $csv
git commit -m $msg | Out-Null
git push
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Ne udalos otpravit na GitHub. Zapis sohranena lokalno; otpravte pozzhe komandoy: git push' -ForegroundColor Yellow
} else { Write-Host "Gotovo: $msg" -ForegroundColor Green }
