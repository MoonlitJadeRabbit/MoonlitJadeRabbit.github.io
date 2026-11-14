function Get-RepoRoot {
    $dir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
    while ($dir) {
        if (Test-Path (Join-Path $dir ".git")) {
            return (Resolve-Path $dir).Path
        }
        $parent = Split-Path $dir -Parent
        if (-not $parent -or $parent -eq $dir) {
            break
        }
        $dir = $parent
    }
    return (Get-Location).Path
}

function Write-SyncLog {
    param(
        [string]$Tag,
        [string]$Message
    )

    $logFile = Join-Path $PSScriptRoot "git-sync.log"
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')] [$Tag] $Message"
    Add-Content -Path $logFile -Value $line -Encoding utf8
}

function Invoke-Git {
    param(
        [string]$RepoRoot,
        [string[]]$GitArgs
    )

    $safeDir = "safe.directory=$RepoRoot"
    $allArgs = @("-c", $safeDir) + $GitArgs
    $output = & git @allArgs 2>&1
    return @{
        ExitCode = $LASTEXITCODE
        Output   = ($output | Out-String).Trim()
    }
}

function Test-Throttled {
    param(
        [string]$MarkerFile,
        [int]$Seconds
    )

    if (-not (Test-Path $MarkerFile)) {
        return $false
    }

    $last = (Get-Item $MarkerFile).LastWriteTimeUtc
    return ((Get-Date).ToUniversalTime() - $last).TotalSeconds -lt $Seconds
}

function Set-ThrottleMarker {
    param([string]$MarkerFile)

    New-Item -ItemType File -Path $MarkerFile -Force | Out-Null
    (Get-Item $MarkerFile).LastWriteTimeUtc = (Get-Date).ToUniversalTime()
}
