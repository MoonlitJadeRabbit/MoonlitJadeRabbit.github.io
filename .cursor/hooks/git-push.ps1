# Push local commits after an agent finishes. Does NOT commit — you commit manually.
# Fails open: errors are logged and the chat continues.

$ErrorActionPreference = "SilentlyContinue"
. "$PSScriptRoot\git-sync-common.ps1"

$repoRoot = Get-RepoRoot
Set-Location $repoRoot

$throttleFile = Join-Path $PSScriptRoot ".last-push"
if (Test-Throttled -MarkerFile $throttleFile -Seconds 120) {
    exit 0
}

$branchResult = Invoke-Git -RepoRoot $repoRoot -GitArgs @("rev-parse", "--abbrev-ref", "HEAD")
if ($branchResult.ExitCode -ne 0) {
    exit 0
}

$branch = ($branchResult.Output -split "`n")[0].Trim()

$dirty = Invoke-Git -RepoRoot $repoRoot -GitArgs @("status", "--porcelain")
if ($dirty.Output) {
    Write-SyncLog "push" "Skipped: uncommitted changes (commit manually, then push or run agent again after commit)."
    exit 0
}

$ahead = Invoke-Git -RepoRoot $repoRoot -GitArgs @("rev-list", "--count", "origin/$branch..HEAD")
if ($ahead.ExitCode -ne 0 -or [int]$ahead.Output -eq 0) {
    Write-SyncLog "push" "Nothing to push."
    exit 0
}

Write-SyncLog "push" "Pulling before push ($branch)..."

$fetch = Invoke-Git -RepoRoot $repoRoot -GitArgs @("fetch", "origin")
if ($fetch.ExitCode -ne 0) {
    Write-SyncLog "push" "fetch failed; skipped push: $($fetch.Output)"
    exit 0
}

$pull = Invoke-Git -RepoRoot $repoRoot -GitArgs @("pull", "--rebase", "origin", $branch)
if ($pull.ExitCode -ne 0) {
    Write-SyncLog "push" "pull --rebase failed; skipped push: $($pull.Output)"
    exit 0
}

$push = Invoke-Git -RepoRoot $repoRoot -GitArgs @("push", "origin", $branch)
if ($push.ExitCode -ne 0) {
    Write-SyncLog "push" "push failed: $($push.Output)"
    exit 0
}

Set-ThrottleMarker -MarkerFile $throttleFile
Write-SyncLog "push" "OK: pushed $branch ($($ahead.Output) commit(s))"
exit 0
