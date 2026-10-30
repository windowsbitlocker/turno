param(
    [string]$Repository = 'windowsbitlocker/turno',
    [string]$Tag = 'v0.1.0'
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-Location -LiteralPath (Split-Path $PSScriptRoot -Parent)
if ($Repository -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$' -or $Tag -notmatch '^v\d+\.\d+\.\d+$') {
    throw 'Invalid repository or release tag.'
}
$turnoVersion = $Tag.Substring(1)
$turnoAssets = @(
    (Join-Path (Get-Location) "dist\Turno-$Tag-Windows-x64.zip"),
    (Join-Path (Get-Location) "dist\Turno-$Tag-SHA256.txt")
)
foreach ($turnoAsset in $turnoAssets) {
    if (-not (Test-Path -LiteralPath $turnoAsset -PathType Leaf)) { throw "Missing asset: $turnoAsset" }
}
# Git Credential Manager supplies the existing GitHub sign-in. Never print or save it.
$turnoCredential = @{}
$turnoCredentialLines = "protocol=https`nhost=github.com`n`n" | git credential fill
if ($LASTEXITCODE -ne 0) { throw 'GitHub sign-in is required. Sign in through Git first.' }
foreach ($turnoLine in $turnoCredentialLines) {
    $turnoParts = $turnoLine -split '=', 2
    if ($turnoParts.Count -eq 2) { $turnoCredential[$turnoParts[0]] = $turnoParts[1] }
}
if (-not $turnoCredential.password) { throw 'No GitHub credential is available.' }
$turnoHeaders = @{
    Authorization = 'Bearer ' + $turnoCredential.password
    Accept = 'application/vnd.github+json'
    'X-GitHub-Api-Version' = '2022-11-28'
    'User-Agent' = 'Turno-Windows-release'
}
$turnoApi = "https://api.github.com/repos/$Repository"
$turnoExisting = @(Invoke-RestMethod "$turnoApi/releases" -Headers $turnoHeaders)
$turnoRelease = $turnoExisting | Where-Object tag_name -EQ $Tag | Select-Object -First 1
if ($turnoRelease -and -not $turnoRelease.draft) { throw 'This release is already published; no files were changed.' }
$turnoCommit = (git rev-parse HEAD).Trim()
$turnoBody = @"
## Turno $turnoVersion for Windows

Download **Turno-$Tag-Windows-x64.zip**, extract it, and open **Turno.exe**.
No Python installation is needed. Windows 10/11, 64-bit Intel/AMD.

- Operator panel and separate projector display.
- Twenty configurable debate phases and operator-controlled robo/refutation.
- Live resizing of projector text and logos.
- Optional logos are supported by the bundled app.
- Completely offline; no contestant phones or network connection required.

The ZIP includes the MIT license and third-party notices. SHA-256 checksums are attached.

Validation: 15 automated source tests plus a smoke check of the compiled executable,
including the clock, robo deduction, logo loading, and projector size editor.

This initial portable release is unsigned. It was checked on Windows 11; testing on
additional Windows machines remains welcome.
"@
if (-not $turnoRelease) {
    $turnoCreate = @{ tag_name=$Tag; target_commitish=$turnoCommit; name="Turno $Tag - Windows";
                      body=$turnoBody; draft=$true; prerelease=$false } | ConvertTo-Json
    $turnoRelease = Invoke-RestMethod "$turnoApi/releases" -Method Post -Headers $turnoHeaders -ContentType 'application/json' -Body $turnoCreate
}
$turnoUpload = ($turnoRelease.upload_url -split '\{')[0]
if (([uri]$turnoUpload).Host -ne 'uploads.github.com' -or ([uri]$turnoUpload).Scheme -ne 'https') {
    throw 'Unexpected release upload host.'
}
foreach ($turnoAsset in $turnoAssets) {
    $turnoFile = Get-Item -LiteralPath $turnoAsset
    $turnoPresent = @($turnoRelease.assets) | Where-Object name -EQ $turnoFile.Name | Select-Object -First 1
    if ($turnoPresent) {
        $turnoDigest = 'sha256:' + (Get-FileHash -LiteralPath $turnoAsset -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($turnoPresent.size -ne $turnoFile.Length -or $turnoPresent.digest -ne $turnoDigest) {
            throw 'A draft asset with different contents exists. Review it before replacing anything.'
        }
        continue
    }
    $turnoContentType = if ($turnoFile.Extension -eq '.zip') { 'application/zip' } else { 'text/plain' }
    $turnoAssetUrl = $turnoUpload + '?name=' + [uri]::EscapeDataString($turnoFile.Name)
    $turnoUploaded = Invoke-RestMethod $turnoAssetUrl -Method Post -Headers $turnoHeaders -ContentType $turnoContentType -InFile $turnoAsset
    if ($turnoUploaded.state -ne 'uploaded' -or $turnoUploaded.size -ne $turnoFile.Length) {
        throw 'Release asset verification failed; the release remains a draft.'
    }
}
$turnoReady = Invoke-RestMethod "$turnoApi/releases/$($turnoRelease.id)" -Headers $turnoHeaders
foreach ($turnoAsset in $turnoAssets) {
    $turnoName = Split-Path $turnoAsset -Leaf
    if (-not (@($turnoReady.assets) | Where-Object { $_.name -eq $turnoName -and $_.state -eq 'uploaded' })) {
        throw 'An expected asset is missing; the release remains a draft.'
    }
}
$turnoPublish = @{ draft=$false; make_latest='true'; body=$turnoBody } | ConvertTo-Json
$turnoPublished = Invoke-RestMethod "$turnoApi/releases/$($turnoRelease.id)" -Method Patch -Headers $turnoHeaders -ContentType 'application/json' -Body $turnoPublish
Write-Output $turnoPublished.html_url
$turnoPublished.assets | Select-Object name,size,browser_download_url
