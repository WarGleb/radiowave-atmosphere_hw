param([string]$Action, [string]$Dz)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$csv = 'worklog.csv'
$seenFile = '.hw_seen'
$repo = 'WarGleb/radiowave-atmosphere_hw'
$msk = [TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, 'UTC', 'Russian Standard Time')
$stamp = $msk.ToString('yyyy-MM-dd HH:mm')

# Proverka osnovnogo repozitoriya s zadaniyami (tolko pri start). Pri oshibke seti molcha propuskaem.
function Check-Tasks([string]$dz) {
    try {
        $h = @{ 'User-Agent' = 'hw-check' }
        $head = Invoke-RestMethod "https://api.github.com/repos/$repo/commits/main" -Headers $h -TimeoutSec 15
        $new = $head.sha
        $date = ([DateTime]$head.commit.committer.date).ToUniversalTime()
        $dateMsk = [TimeZoneInfo]::ConvertTimeBySystemTimeZoneId($date, 'UTC', 'Russian Standard Time').ToString('yyyy-MM-dd HH:mm')
        $old = if (Test-Path $seenFile) { (Get-Content $seenFile -Raw).Trim() } else { '' }
        if (-not $old) {
            Write-Host "Versiya zadaniy: $($new.Substring(0,7)) ot $dateMsk MSK." -ForegroundColor Cyan
        }
        elseif ($old -ne $new) {
            try {
                $cmp = Invoke-RestMethod "https://api.github.com/repos/$repo/compare/$old...$new" -Headers $h -TimeoutSec 15
                $files = @($cmp.files | ForEach-Object { $_.filename })
                $mine = @($files | Where-Object { $_ -match "(^|/)$dz(_|\.)" -or $_ -match "variants_$dz\." })
                $common = @($files | Where-Object { $_ -match '^(README|HOWTO_|student-template/)' })
                if ($mine.Count -gt 0) {
                    Write-Host "VNIMANIE: zadanie $dz izmeneno v osnovnom repozitorii ($dateMsk MSK):" -ForegroundColor Yellow
                    $mine | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
                    Write-Host "Prochitayte zanovo: https://github.com/$repo/blob/main/$dz*.md  (papka: https://github.com/$repo)" -ForegroundColor Yellow
                }
                if ($common.Count -gt 0) {
                    Write-Host "Izmeneny obshchie fayly (shablon, README, HOWTO):" -ForegroundColor Yellow
                    $common | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
                }
                if ($mine.Count -eq 0 -and $common.Count -eq 0) {
                    Write-Host "V osnovnom repozitorii byli izmeneniya, vashego zadaniya oni ne kasayutsya." -ForegroundColor Cyan
                }
            } catch {
                Write-Host "Istoriya osnovnogo repozitoriya izmenena. Prover'te zadanie $dz zanovo: https://github.com/$repo" -ForegroundColor Yellow
            }
        }
        else { Write-Host 'Zadaniya aktualny, izmeneniy net.' -ForegroundColor Green }
        Set-Content $seenFile $new -Encoding ASCII
        return $new.Substring(0, 7)
    } catch {
        Write-Host 'Ne udalos proverit osnovnoy repozitoriy (net seti?). Prodolzhaem.' -ForegroundColor DarkYellow
        return ''
    }
}

if (-not (Test-Path $csv)) { 'dz,start,end,hw' | Set-Content $csv -Encoding ASCII }
$rows = @(Import-Csv $csv)
$open = @($rows | Where-Object { -not $_.end })

if ($Action -eq 'start') {
    if ($open.Count -gt 0) {
        Write-Host "Vy uzhe nachali rabotu v $($open[-1].start) ($($open[-1].dz)). Snachala zapustite stop.bat." -ForegroundColor Yellow
        exit 1
    }
    if (-not $Dz) { $Dz = Read-Host 'Nomer zadaniya (naprimer dz1)' }
    $Dz = $Dz.Trim().ToLower()
    $hw = Check-Tasks $Dz
    Add-Content $csv "$Dz,$stamp,,$hw" -Encoding ASCII
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
