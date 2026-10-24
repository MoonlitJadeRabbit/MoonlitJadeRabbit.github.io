# Pull latest from GitHub when a chat starts or you send a message.
# Fails open: errors are logged and the chat continues.

$ErrorActionPreference = "SilentlyContinue"
. "$PSScriptRoot\git-sync-common.ps1"

$repoRoot = Get-RepoRoot
Set-Location $repoRoot

$throttleFile = Join-Path $PSScriptRoot ".last-pull"
if (Test-Throttled -MarkerFile $throttleFile -Seconds 60) {
    exit 0
}

$branchResult = Invoke-Git -RepoRoot $repoRoot -GitArgs @("rev-parse", "--abbrev-ref", "HEAD")
if ($branchResult.ExitCode -ne 0) {
    Write-SyncLog "pull" "Not a git repo; skipped."
    exit 0
}

$branch = ($branchResult.Output -split "`n")[0].Trim()
if (-not $branch) {
    exit 0
}

Write-SyncLog "pull" "Fetching origin ($branch) in $repoRoot"

$fetch = Invoke-Git -RepoRoot $repoRoot -GitArgs @("fetch", "origin")
if ($fetch.ExitCode -ne 0) {
    Write-SyncLog "pull" "fetch failed: $($fetch.Output)"
    exit 0
}

$pull = Invoke-Git -RepoRoot $repoRoot -GitArgs @("pull", "--rebase", "origin", $branch)
if ($pull.ExitCode -ne 0) {
    Write-SyncLog "pull" "pull --rebase failed (merge conflict or offline): $($pull.Output)"
    exit 0
}

Set-ThrottleMarker -MarkerFile $throttleFile
Write-SyncLog "pull" "OK: $($pull.Output)"
exit 0
