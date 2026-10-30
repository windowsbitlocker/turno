param([string]$PythonCommand = 'python')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Run-TurnoPython {
    param([string[]]$PythonArguments)
    & $PythonCommand @PythonArguments
    if ($LASTEXITCODE -ne 0) { throw 'The Windows build failed.' }
}

Run-TurnoPython @('-m', 'PyInstaller', '--version')
Run-TurnoPython @('tools/make_windows_icon.py')
Run-TurnoPython @('-m', 'PyInstaller', '--noconfirm', 'Turno.spec')

$debateReport = Join-Path $PSScriptRoot 'build\windows-smoke\report.json'
$debateExe = Join-Path $PSScriptRoot 'dist\Turno.exe'
$debateSmoke = Start-Process -FilePath $debateExe -ArgumentList @('--self-test-report', ('"' + $debateReport + '"')) -WindowStyle Hidden -PassThru
if (-not $debateSmoke.WaitForExit(45000)) {
    $debateSmoke.Kill()
    throw 'The packaged application smoke check timed out.'
}
if ($debateSmoke.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $debateReport)) {
    throw 'The packaged application smoke check failed.'
}
$debateCheck = Get-Content -LiteralPath $debateReport -Raw | ConvertFrom-Json
if (-not $debateCheck.ok -or -not $debateCheck.frozen) { throw 'The bundled application check did not pass.' }
Run-TurnoPython @('tools/package_windows.py')
Write-Output 'Windows portable release built and verified.'
