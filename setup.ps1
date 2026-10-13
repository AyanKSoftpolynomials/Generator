<#
.SYNOPSIS
  One-time setup of the LMS Video Generator on a Windows PC (safe to re-run).

.DESCRIPTION
  1. Finds Python 3.12 (3.11 / 3.13 also work; 3.14 does not) - installs 3.12 with winget if none is found
  2. Creates the virtual environment .venv (an existing .venv is kept, never deleted)
  3. Installs the pinned Python packages from requirements.txt
  4. Runs scripts/setup.py: FFmpeg (installed with winget if missing), CUDA PyTorch if an NVIDIA GPU exists
  5. Checks Node.js (installed with winget if missing) and installs the web UI packages (frontend/node_modules)
  6. Creates the working folders (cache, output, local)
  7. Runs the health check (scripts/health_check.py)

  It never deletes or overwrites your files, settings.json, voices, lessons or local/ (YouTube login).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\setup.ps1
  powershell -ExecutionPolicy Bypass -File .\setup.ps1 -Full            # also downloads + tests the speech models (~2.3 GB)
  powershell -ExecutionPolicy Bypass -File .\setup.ps1 -SkipFrontend    # CLI only, no web UI
  powershell -ExecutionPolicy Bypass -File .\setup.ps1 -NoInstallTools  # never run winget; only report what is missing
#>
param(
    [switch]$Full,
    [switch]$SkipFrontend,
    [switch]$NoInstallTools
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$Root = $PSScriptRoot
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"

function Step($text) { Write-Host ""; Write-Host "==> $text" -ForegroundColor Cyan }
function Ok($text)   { Write-Host "    OK   $text" -ForegroundColor Green }
function Warn($text) { Write-Host "    WARN $text" -ForegroundColor Yellow }
function Fail($text) { Write-Host "    FAIL $text" -ForegroundColor Red; exit 1 }

function Refresh-Path {
    # winget installs change PATH for NEW terminals; pick the change up in this one too.
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

function Have($command) { return [bool](Get-Command $command -ErrorAction SilentlyContinue) }

function Winget-Install($id, $what) {
    if ($NoInstallTools) { Fail "$what is missing. Install it (winget install --id $id), open a new terminal and re-run setup.ps1." }
    if (-not (Have "winget")) { Fail "$what is missing and winget is not available. Install $what manually, then re-run setup.ps1." }
    Write-Host "    Installing $what with winget ($id)..."
    & winget install --id $id -e --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity
    if ($LASTEXITCODE -ne 0) {
        # some packages (e.g. Node.js) only offer a machine-wide installer
        & winget install --id $id -e --accept-package-agreements --accept-source-agreements --disable-interactivity
    }
    Refresh-Path
}

function Python-Version($exe, [string[]]$prefix) {
    $old = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    try {
        $out = & $exe @prefix -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $out) { return ($out | Select-Object -First 1).Trim() }
    } catch { }
    finally { $ErrorActionPreference = $old }
    return $null
}

function Find-Python {
    $candidates = @(
        @("py", @("-V:3.12")), @("py", @("-3.12")),
        @("py", @("-V:3.13")), @("py", @("-3.13")),
        @("py", @("-V:3.11")), @("py", @("-3.11")),
        @("python", @())
    )
    foreach ($c in $candidates) {
        if (-not (Have $c[0])) { continue }
        $v = Python-Version $c[0] $c[1]
        if ($v -in @("3.11", "3.12", "3.13")) { return @{ Exe = $c[0]; Args = $c[1]; Version = $v } }
    }
    return $null
}

Write-Host "LMS VIDEO GENERATOR SETUP" -ForegroundColor Cyan
Write-Host "Project: $Root"

# ------------------------------------------------------------------ 1-2. Python + .venv
Step "Python virtual environment (.venv)"
if (Test-Path $VenvPython) {
    $v = Python-Version $VenvPython @()
    if ($v -notin @("3.11", "3.12", "3.13")) {
        Fail ".venv uses Python $v (needs 3.11-3.13; 3.14 has no Manim OpenGL wheels). Rename or delete the .venv folder yourself, then re-run setup.ps1."
    }
    Ok "existing .venv kept (Python $v)"
} else {
    $py = Find-Python
    if (-not $py) {
        Winget-Install "Python.Python.3.12" "Python 3.12"
        $py = Find-Python
        if (-not $py) { Fail "Python 3.12 was installed but is not visible yet. Open a NEW terminal and re-run setup.ps1." }
    }
    Write-Host "    Creating .venv with Python $($py.Version)..."
    & $py.Exe @($py.Args) -m venv .venv
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython)) { Fail "could not create .venv" }
    Ok "created .venv (Python $($py.Version))"
}

# ------------------------------------------------------------------ 3-4. Python packages, FFmpeg, GPU
Step "Python packages (requirements.txt; the first install downloads ~1-2 GB and takes several minutes)"
& $VenvPython -m pip install --upgrade pip --disable-pip-version-check -q
& $VenvPython -m pip install -r requirements.txt --disable-pip-version-check
if ($LASTEXITCODE -ne 0) { Fail "pip install failed (see the error above). Fix it and re-run setup.ps1." }
Ok "packages installed"

Step "FFmpeg, LaTeX and GPU (scripts/setup.py)"
$setupArgs = @("scripts\setup.py")
if ($NoInstallTools) { $setupArgs += "--check" }
& $VenvPython @setupArgs
Refresh-Path
if ($LASTEXITCODE -ne 0) { Warn "scripts/setup.py reported problems (FIX lines above). LaTeX is only needed for MathTex/Tex lessons." }

# ------------------------------------------------------------------ 5. Web UI
if ($SkipFrontend) {
    Step "Web UI skipped (-SkipFrontend): the command line generator works without it"
} else {
    Step "Node.js and web UI packages"
    if (-not (Have "node")) { Winget-Install "OpenJS.NodeJS.LTS" "Node.js LTS" }
    if (-not (Have "node")) { Fail "Node.js was installed but is not visible yet. Open a NEW terminal and re-run setup.ps1." }
    $nodeVersion = (& node --version).Trim()
    $major = [int]($nodeVersion.TrimStart("v").Split(".")[0])
    if ($major -lt 20) { Fail "Node.js $nodeVersion is too old (Next.js 16 needs 20.9+). Update: winget upgrade --id OpenJS.NodeJS.LTS" }
    Ok "Node.js $nodeVersion"
    & npm --prefix frontend install --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { Fail "npm install failed (see the error above)." }
    Ok "frontend packages installed (frontend/node_modules)"
}

# ------------------------------------------------------------------ 6. Folders
Step "Working folders"
foreach ($dir in @("cache", "output", "local", "lessons", "assets\voices")) {
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null; Ok "created $dir\" } else { Ok "$dir\ exists" }
}
if (-not (Test-Path "settings.json")) { Warn "settings.json not found: built-in defaults are used (src/config/settings.py)" }

# ------------------------------------------------------------------ 7. Health check
Step "Health check"
$checkArgs = @("scripts\health_check.py")
if ($Full) { $checkArgs += "--full" }
& $VenvPython @checkArgs
$healthy = ($LASTEXITCODE -eq 0)

Write-Host ""
if ($healthy) {
    Write-Host "Setup finished." -ForegroundColor Green
    Write-Host "  Web UI:        npm run dev        then open http://127.0.0.1:3000"
    Write-Host "  Command line:  .\.venv\Scripts\python.exe generate.py lessons\team_test"
} else {
    Write-Host "Setup finished, but the health check found problems (FAIL lines above)." -ForegroundColor Yellow
    exit 1
}
