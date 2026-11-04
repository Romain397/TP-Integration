param([switch]$WaitForDocker)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Push-Location $projectRoot
try {
    if ($WaitForDocker) {
        $ready = $false
        for ($attempt = 0; $attempt -lt 30; $attempt++) {
            docker info --format '{{.ServerVersion}}' 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { $ready = $true; break }
            Start-Sleep -Seconds 2
        }
        if (-not $ready) { throw 'Docker ne répond pas après 60 secondes. Démarrer Docker Desktop puis relancer.' }
    }
    docker info --format '{{.ServerVersion}}'
    if ($LASTEXITCODE -ne 0) { throw 'Le moteur Docker est indisponible.' }

    node scripts/prepare-baseline.js
    if ($LASTEXITCODE -ne 0) { throw 'Préparation baseline impossible.' }
    npm ci --ignore-scripts --prefix .artifacts/baseline
    if ($LASTEXITCODE -ne 0) { throw 'Installation baseline impossible.' }
    docker build -t devsecops-tp:naif .artifacts/baseline
    if ($LASTEXITCODE -ne 0) { throw 'Build naïf impossible.' }
    docker build -t devsecops-tp:optim .
    if ($LASTEXITCODE -ne 0) { throw 'Build optimisé impossible.' }

    $reports = Join-Path $projectRoot 'reports'
    $cache = Join-Path $projectRoot '.artifacts/trivy-cache'
    New-Item -ItemType Directory -Path $reports, $cache -Force | Out-Null
    $scanner = 'aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969'
    $rows = @()
    foreach ($tag in @('naif', 'optim')) {
        $imageName = "devsecops-tp:$tag"
        $info = (docker image inspect $imageName | ConvertFrom-Json)[0]
        if ($LASTEXITCODE -ne 0) { throw "Inspection impossible : $imageName" }
        docker history --no-trunc --human=false --format '{{json .}}' $imageName |
            Set-Content -Encoding utf8 (Join-Path $reports "history-$tag.jsonl")
        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock `
            -v "${reports}:/reports" -v "${cache}:/root/.cache/trivy" $scanner image `
            --quiet --scanners vuln --severity HIGH,CRITICAL --format json `
            --output "/reports/trivy-$tag.json" $imageName
        if ($LASTEXITCODE -ne 0) { throw "Scan impossible : $imageName" }
        $scan = Get-Content (Join-Path $reports "trivy-$tag.json") -Raw | ConvertFrom-Json
        $vulnerabilities = @($scan.Results | ForEach-Object { $_.Vulnerabilities } | Where-Object { $null -ne $_ })
        $rows += [pscustomobject]@{
            image = $imageName
            sizeBytes = $info.Size
            sizeMiB = [math]::Round($info.Size / 1MB, 2)
            layers = $info.RootFS.Layers.Count
            high = @($vulnerabilities | Where-Object Severity -eq HIGH).Count
            critical = @($vulnerabilities | Where-Object Severity -eq CRITICAL).Count
            fixableHighCritical = @($vulnerabilities | Where-Object { $_.FixedVersion }).Count
            user = $info.Config.User
        }
    }
    $containerName = 'tp3-smoke-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
    docker run -d --name $containerName -p 127.0.0.1::3000 devsecops-tp:optim
    if ($LASTEXITCODE -ne 0) { throw "Démarrage de l'image optimisée impossible." }
    try {
        $binding = docker port $containerName 3000/tcp
        $health = $null
        for ($attempt = 0; $attempt -lt 20; $attempt++) {
            try { $health = Invoke-RestMethod "http://$binding/health"; break }
            catch { Start-Sleep -Seconds 1 }
        }
        if ($health.status -ne 'ok') { throw 'Le test /health a échoué.' }
        if ($rows[1].user -ne 'node') { throw "L'image ne fonctionne pas avec USER node." }
        $result = [pscustomobject]@{
            measuredAt = (Get-Date).ToUniversalTime().ToString('o')
            platform = 'linux/amd64'
            trivy = $scanner
            smokeTest = 'GET /health -> 200 {"status":"ok"}; USER node'
            images = $rows
        }
        $result | ConvertTo-Json -Depth 6 | Set-Content -Encoding utf8 (Join-Path $reports 'images.json')
        $rows | Format-Table
        if ($rows[1].fixableHighCritical -gt 0) {
            throw "Le scan bloque : l'image optimisée contient des failles HIGH/CRITICAL corrigeables."
        }
    }
    finally { docker rm -f $containerName | Out-Null }
}
finally { Pop-Location }
