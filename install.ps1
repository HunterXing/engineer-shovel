#!/usr/bin/env pwsh
# engineer-shovel — Windows PowerShell installer
# Usage: powershell -c "iex (iwr -useb https://raw.githubusercontent.com/HunterXing/engineer-shovel/main/install.ps1)"

param(
  [ValidateSet("minimal","recommended","full")]
  [string]$Mode = "full",
  [ValidateSet("opencode","claude","all","auto")]
  [string]$Target = "auto",
  [ValidateSet("global","local")]
  [string]$Scope = "global",
  [switch]$DryRun = $false,
  [switch]$WithGraphBuild = $false,
  [switch]$Yes = $false,
  [switch]$Help = $false
)

$REPO_OWNER = "HunterXing"
$REPO_NAME = "engineer-shovel"
$REPO_URL = "https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main"

$CAVEMAN_INSTALLER_URL = "https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.ps1"

$FAILURES = 0

# --- helpers ---
function Info  { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Ok    { Write-Host "✔ $args" -ForegroundColor Green }
function Warn  { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Err   { Write-Host "✘ $args" -ForegroundColor Red }

function Record-Failure { param([string]$msg) Warn $msg; $global:FAILURES++ }

function Run-Or-Dry {
  if ($DryRun) { Info "DRY-RUN: $args" }
  else { & $args | Out-Host }
}

# --- prereqs ---
function Check-Prereqs {
  $missing = @()
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { $missing += "git" }
  if (-not (Get-Command curl -ErrorAction SilentlyContinue) -and
      -not (Get-Command Invoke-WebRequest -ErrorAction SilentlyContinue)) { $missing += "curl or PowerShell" }

  if ($missing.Count -gt 0) {
    Err "Missing: $($missing -join ', ')"
    Info "Install Git for Windows: https://git-scm.com"
    exit 1
  }

  # Auto-install pipx on Windows
  if (-not (Get-Command pipx -ErrorAction SilentlyContinue)) {
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
      Info "Installing pipx..."
      & python3 -m pip install --user pipx 2>&1 | Out-Host
      & python3 -m pipx ensurepath 2>&1 | Out-Null
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
      Info "Installing pipx..."
      & python -m pip install --user pipx 2>&1 | Out-Host
      & python -m pipx ensurepath 2>&1 | Out-Null
    } else {
      Warn "python3 not found; pipx install skipped"
    }
  }
}

function Resolve-Targets {
  if ($Target -eq "auto") {
    if (Get-Command opencode -ErrorAction SilentlyContinue) { return @("opencode") }
    elseif (Get-Command claude -ErrorAction SilentlyContinue) { return @("claude-code") }
    else { Warn "Neither opencode nor claude found; using OpenCode paths"; return @("opencode") }
  }
  switch ($Target) {
    "opencode" { return @("opencode") }
    "claude"   { return @("claude-code") }
    "all"      { return @("opencode", "claude-code") }
  }
}

function Set-TargetPaths {
  param([string]$target)
  $script:ENV = $target
  if ($Scope -eq "local") {
    $script:SKILL_DIR = ".\\.agents\\skills"
    $script:COMMAND_DIR = if ($target -eq "opencode") { ".\.opencode\commands" } else { ".\.claude\commands" }
  } else {
    $script:SKILL_DIR = "$env:USERPROFILE\.agents\skills"
    $script:COMMAND_DIR = if ($target -eq "opencode") { "$env:APPDATA\opencode\commands" } else { "$env:USERPROFILE\.claude\commands" }
  }
}

function Download-File {
  param([string]$url, [string]$targetPath)
  if ($DryRun) { Info "DRY-RUN: download $url -> $targetPath"; return }
  $dir = Split-Path $targetPath -Parent
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  if (Get-Command curl -ErrorAction SilentlyContinue) {
    curl -fsSL --retry 3 $url -o $targetPath 2>$null
  } else {
    Invoke-WebRequest -Uri $url -OutFile $targetPath -UseBasicParsing
  }
}

function Install-Skill {
  param([string]$skillDir)
  $target = Join-Path $skillDir "engineer-shovel"
  $src = if (Test-Path ".\SKILL.md") { ".\SKILL.md" } else { "$REPO_URL/SKILL.md" }
  if ($DryRun) { Info "DRY-RUN: install skill -> $target"; return }
  New-Item -ItemType Directory -Force -Path $target | Out-Null
  if (Test-Path ".\SKILL.md") {
    Copy-Item ".\SKILL.md" (Join-Path $target "SKILL.md")
  } else {
    Download-File "$REPO_URL/SKILL.md" (Join-Path $target "SKILL.md")
  }
  Ok "Installed skill -> $target\SKILL.md"
}

function Install-Commands {
  param([string]$cmdDir)
  $names = @("branch","feat","fix","plan","refactor","review","quick","research","graph","update","alias")
  if ($DryRun) { Info "DRY-RUN: install commands -> $cmdDir"; return }
  New-Item -ItemType Directory -Force -Path $cmdDir | Out-Null
  $count = 0
  foreach ($name in $names) {
    $localPath = ".\commands\tool-${name}.md"
    $target = Join-Path $cmdDir "tool-${name}.md"
    $remoteUrl = "$REPO_URL/commands/tool-${name}.md"
    if (Test-Path $localPath) {
      Copy-Item $localPath $target
    } else {
      Download-File $remoteUrl $target
    }
    $count++
  }
  Ok "Installed $count commands -> $cmdDir"
}

# ---------- superpowers ----------
function Gen-SuperpowersCommands {
  if ($DryRun) { Info "DRY-RUN: generate superpowers command wrappers"; return }

  $cmdDir = if ($Scope -eq "local") { ".\.opencode\commands" } else { "$env:APPDATA\opencode\commands" }
  New-Item -ItemType Directory -Force -Path $cmdDir | Out-Null

  $skills = @(
    @("brainstorm", "brainstorming", "Structured ideation for design decisions and creative problem-solving"),
    @("parallel-agents", "dispatching-parallel-agents", "Orchestrate parallel subagents for independent work streams"),
    @("execute-plan", "executing-plans", "Execute structured plans with verification checkpoints"),
    @("finish-branch", "finishing-a-development-branch", "Complete and verify a development branch before merge"),
    @("receive-review", "receiving-code-review", "Process and respond to code review feedback systematically"),
    @("request-review", "requesting-code-review", "Prepare and submit code changes for review"),
    @("subagent-dev", "subagent-driven-development", "Decompose complex tasks via specialized subagents"),
    @("debug", "systematic-debugging", "Scientific method debugging pipeline with root cause tracing"),
    @("tdd", "test-driven-development", "Test-driven development: red-green-refactor workflow"),
    @("git-worktrees", "using-git-worktrees", "Manage parallel development with git worktrees"),
    @("superpowers", "using-superpowers", "List, discover, and manage available superpowers skills"),
    @("verify", "verification-before-completion", "Structured verification checklist before task sign-off"),
    @("write-plan", "writing-plans", "Create structured planning documentation and execution roadmaps"),
    @("write-skill", "writing-skills", "Create and maintain reusable skill files")
  )
  $count = 0
  foreach ($entry in $skills) {
    $cmdName = $entry[0]; $skillName = $entry[1]; $desc = $entry[2]
    $target = Join-Path $cmdDir "superpowers:$cmdName.md"
    if (Test-Path $target) { continue }
@"
---
description: $desc
---

# /superpowers:$cmdName

Load the **$skillName** skill from superpowers:

```
skill(name="$skillName")
```

Follow its instructions exactly.
"@ | Set-Content $target -Encoding UTF8
    $count++
  }
  if ($count -gt 0) { Ok "Created $count superpowers command wrappers -> $cmdDir" }
}

function Install-Superpowers-OpenCode {
  if ($DryRun) { Info "DRY-RUN: opencode plugin "superpowers@github:obra/superpowers" -g"; Info "DRY-RUN: generate superpowers command wrappers"; return }

  if (Get-Command opencode -ErrorAction SilentlyContinue) {
    Info "Installing superpowers via opencode plugin..."
    $result = & opencode plugin "superpowers@github:obra/superpowers" -g 2>&1
    if ($LASTEXITCODE -eq 0) { Ok "Superpowers installed for OpenCode"; Gen-SuperpowersCommands; return }
    Warn "opencode plugin "superpowers@github:obra/superpowers" failed; using legacy config method"
  }

  $configDir = if ($Scope -eq "local") { ".\.opencode" } else { "$env:APPDATA\opencode" }
  $configFile = Join-Path $configDir "opencode.json"
  New-Item -ItemType Directory -Force -Path $configDir | Out-Null

  $config = @{}
  if (Test-Path $configFile) {
    $config = Get-Content $configFile | ConvertFrom-Json -AsHashtable
  }
  if (-not $config.ContainsKey("plugin")) { $config["plugin"] = @() }
  $entry = "superpowers@git+https://github.com/obra/superpowers.git"
  if ($config["plugin"] -notcontains $entry) {
    $config["plugin"] += @($entry)
    $config | ConvertTo-Json -Depth 10 | Set-Content $configFile
  }
  Ok "Superpowers configured (legacy method)"
  Gen-SuperpowersCommands
}

function Install-Superpowers-Claude {
  if ($DryRun) { Info "DRY-RUN: claude plugin install superpowers"; return }
  if (Get-Command claude -ErrorAction SilentlyContinue) {
    & claude plugin install superpowers@claude-plugins-official 2>&1 | Out-Host
    if ($LASTEXITCODE -eq 0) { Ok "Superpowers installed for Claude Code" }
    else { Record-Failure "Claude superpowers install failed" }
  } else {
    Record-Failure "claude CLI not found; install superpowers manually"
  }
}

function Install-Superpowers {
  param([string[]]$targets)
  foreach ($t in $targets) {
    switch ($t) {
      "opencode"   { Install-Superpowers-OpenCode }
      "claude-code" { Install-Superpowers-Claude }
    }
  }
}

# ---------- code-review-graph ----------
function Add-CRG-MCP {
  param([string]$configFile)
  $configDir = Split-Path $configFile -Parent
  New-Item -ItemType Directory -Force -Path $configDir | Out-Null

  $config = @{}
  if (Test-Path $configFile) {
    $config = Get-Content $configFile | ConvertFrom-Json -AsHashtable
  }
  if (-not $config.ContainsKey('$schema')) { $config['$schema'] = 'https://opencode.ai/config.json' }
  if (-not $config.ContainsKey("mcp")) { $config["mcp"] = @{} }

  $config["mcp"]["code-review-graph"] = @{
    type    = "local"
    command = @("uvx", "code-review-graph", "serve")
    enabled = $true
  }
  $config | ConvertTo-Json -Depth 10 | Set-Content $configFile
  if ($LASTEXITCODE -eq 0) { Ok "Added code-review-graph MCP to $configFile" }
  else { Record-Failure "Failed to write MCP config to $configFile" }
}

function Install-CodeReviewGraph {
  if ($DryRun) {
    Info "DRY-RUN: pip install code-review-graph"
    foreach ($t in $script:TARGETS) {
      if ($t -eq "opencode") { Info "DRY-RUN: add MCP to opencode config" }
    }
    return
  }

  $haveCrg = (Get-Command code-review-graph -ErrorAction SilentlyContinue) -or
             (Get-Command uvx -ErrorAction SilentlyContinue)
  if (-not $haveCrg) {
    Info "Installing code-review-graph from PyPI..."
    if (Get-Command pip -ErrorAction SilentlyContinue) {
      pip install code-review-graph 2>&1 | Out-Host
    } elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
      pip3 install code-review-graph 2>&1 | Out-Host
    } else {
      Record-Failure "Python/pip not found. Install: pip install code-review-graph"
      return
    }
  }

  foreach ($t in $script:TARGETS) {
    switch ($t) {
      "opencode" {
        $cfgFile = if ($Scope -eq "local") { ".\.opencode\opencode.json" } else { "$env:APPDATA\opencode\opencode.json" }
        Info "Configuring code-review-graph MCP for OpenCode..."
        Add-CRG-MCP $cfgFile
        if (Test-Path ".opencode.json") {
          Remove-Item ".opencode.json" -ErrorAction SilentlyContinue
          Info "Removed old-format .opencode.json"
        }
      }
      "claude-code" {
        if (Get-Command code-review-graph -ErrorAction SilentlyContinue) {
          & code-review-graph install --platform claude-code 2>&1 | Out-Host
        } else {
          Record-Failure "code-review-graph binary needed for Claude Code config"
        }
      }
    }
  }

  if ($WithGraphBuild -and (Get-Command code-review-graph -ErrorAction SilentlyContinue) -and (Test-Path ".git")) {
    Info "Building code-review-graph..."
    & code-review-graph build 2>&1 | Out-Host
  }
}

# ---------- Caveman ----------
function Install-Caveman {
  param([string[]]$targets)
  if ($DryRun) { Info "DRY-RUN: caveman install for $($targets -join ', ')"; return }

  foreach ($t in $targets) {
    $flag = if ($t -eq "opencode") { "--only opencode" } else { "--only claude" }
    if ($Mode -eq "recommended") { $flag += " --minimal" }
    Info "Installing Caveman for $t..."
    try {
      $result = powershell -c "iex (iwr -useb $CAVEMAN_INSTALLER_URL) $flag" 2>&1
      Write-Host $result
      Ok "Caveman installed for $t"
    } catch {
      Record-Failure "Caveman install failed for $t"
    }
  }
}

# ---------- RTK ----------
function Install-RTK {
  if ($DryRun) { Info "DRY-RUN: install rtk (prebuilt binary)"; return }
  if (Get-Command rtk -ErrorAction SilentlyContinue) { Ok "RTK already installed"; return }

  # Try prebuilt binary for Windows
  $arch = switch ([Environment]::ProcessorArchitecture) { "AMD64" { "x86_64" }; "ARM64" { "aarch64" }; default { $null } }
  if ($arch) {
    $rtkUrl = "https://github.com/rtk-ai/rtk/releases/latest/download/rtk-${arch}-pc-windows-msvc.zip"
    $tmpDir = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
    New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
    $zipPath = Join-Path $tmpDir "rtk.zip"
    Info "Downloading RTK from $rtkUrl ..."
    try {
      if (Get-Command curl -ErrorAction SilentlyContinue) {
        curl -fsSL --retry 3 $rtkUrl -o $zipPath 2>$null
      } else {
        Invoke-WebRequest -Uri $rtkUrl -OutFile $zipPath -UseBasicParsing
      }
      Expand-Archive -Path $zipPath -DestinationPath $tmpDir -Force
      $rtkBin = Get-ChildItem -Path $tmpDir -Recurse -Filter "rtk.exe" | Select-Object -First 1
      if ($rtkBin) {
        $targetDir = if ($env:USERPROFILE) { "$env:USERPROFILE\.local\bin" } else { "$env:LOCALAPPDATA\rtk" }
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
        Copy-Item $rtkBin.FullName "$targetDir\rtk.exe" -Force
        # Add to PATH for current session
        $env:Path = "$targetDir;$env:Path"
        if (Get-Command rtk -ErrorAction SilentlyContinue) {
          Ok "RTK installed to $targetDir\rtk.exe"
          Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
          # RTK init on Windows not fully supported; skip
          return
        }
      }
    } catch {
      Warn "RTK download failed: $_"
    }
    Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
  }

  Warn "RTK auto-install failed. Manual: download from https://github.com/rtk-ai/rtk/releases"
  Record-Failure "RTK install failed"
}

# ---------- OpenSpec ----------
function Install-OpenSpec {
  if ($DryRun) { Info "DRY-RUN: npm install -g @fission-ai/openspec@latest"; return }
  if (Get-Command openspec -ErrorAction SilentlyContinue) { Ok "OpenSpec already installed"; return }
  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Record-Failure "npm not found; install Node.js then: npm install -g @fission-ai/openspec@latest"
    return
  }
  Info "Installing OpenSpec..."
  & npm install -g @fission-ai/openspec@latest 2>&1 | Out-Host
  if ($LASTEXITCODE -eq 0) { Ok "OpenSpec installed" }
  else { Record-Failure "OpenSpec install failed" }
}

# ---------- GSD ----------
function Install-GSD {
  param([string[]]$targets)
  if ($DryRun) { Info "DRY-RUN: npx -y get-shit-done-cc@latest $([string]::Join(' ', $targets))"; return }
  $gsdTarget = if ($targets.Count -eq 2) { "--all" } elseif ($targets[0] -eq "opencode") { "--opencode" } else { "--claude" }
  $gsdScope = if ($Scope -eq "local") { "--local" } else { "--global" }
  Info "Installing GSD..."
  & npx -y get-shit-done-cc@latest $gsdTarget $gsdScope 2>&1 | Out-Host
  if ($LASTEXITCODE -eq 0) { Ok "GSD installed" }
  else { Record-Failure "GSD install failed" }
}

# ---------- ECC ----------
function Link-ECCCommands {
  if ($DryRun) { Info "DRY-RUN: link ECC commands"; return }
  $cmdDir = if ($Scope -eq "local") { ".\.opencode\commands" } else { "$env:APPDATA\opencode\commands" }
  # Find ECC commands directory
  $npmRoot = npm root -g 2>$null
  $eccCmdDir = if ($npmRoot) { Join-Path $npmRoot "ecc-universal\commands" } else { $null }
  if (-not $eccCmdDir -or -not (Test-Path $eccCmdDir)) {
    # Try common locations
    $candidates = @(
      "$env:ProgramFiles\nodejs\node_modules\npm\node_modules\ecc-universal\commands",
      "$env:LOCALAPPDATA\npm\node_modules\ecc-universal\commands",
      "$env:APPDATA\npm\node_modules\ecc-universal\commands"
    )
    foreach ($c in $candidates) { if (Test-Path $c) { $eccCmdDir = $c; break } }
  }
  if (-not $eccCmdDir -or -not (Test-Path $eccCmdDir)) { Info "ECC commands not found; skipping symlinks"; return }
  New-Item -ItemType Directory -Force -Path $cmdDir | Out-Null
  $count = 0
  Get-ChildItem "$eccCmdDir\*.md" | ForEach-Object {
    $target = Join-Path $cmdDir $_.Name
    if (-not (Test-Path $target)) {
      New-Item -ItemType SymbolicLink -Path $target -Target $_.FullName -Force | Out-Null
      $count++
    }
  }
  if ($count -gt 0) { Ok "Linked $count ECC commands -> $cmdDir" }
}

function Install-ECC {
  if ($Scope -eq "local") { Info "ECC does not support local scope. Skipping."; return }
  if ($DryRun) { Info "DRY-RUN: ecc installer"; return }
  Info "ECC install requires Linux/macOS; skipping on Windows"
  Record-Failure "ECC is not supported on Windows; install manually in WSL"
  Link-ECCCommands
}

# ---------- claude-mem ----------
function Install-ClaudeMem {
  param([string[]]$targets)
  if ($DryRun) { Info "DRY-RUN: npx claude-mem install"; return }

  # Auto-install Bun if missing
  if (-not (Get-Command bun -ErrorAction SilentlyContinue)) {
    Info "Installing Bun (required by claude-mem)..."
    try {
      $bunScript = Invoke-WebRequest -Uri "https://bun.sh/install" -UseBasicParsing
      & powershell -c $bunScript.Content 2>&1 | Out-Host
      $env:Path = "$env:USERPROFILE\.bun\bin;$env:Path"
    } catch {
      Record-Failure "Bun install failed. claude-mem requires Bun. Manual: https://bun.sh"
      return
    }
  }

  if (-not (Get-Command bun -ErrorAction SilentlyContinue)) {
    Record-Failure "Bun not found after install; add ~\.bun\bin to PATH"
    return
  }

  foreach ($t in $targets) {
    $flag = if ($t -eq "opencode") { "--ide opencode" } else { "--ide claude" }
    & npx -y claude-mem install $flag 2>&1 | Out-Host
    if ($LASTEXITCODE -eq 0) { Ok "claude-mem installed for $t" }
    else { Record-Failure "claude-mem install failed for $t" }
  }
}

# ---------- verify ----------
function Verify-Install {
  if ($DryRun) { Ok "Dry-run completed"; return }
  $missing = 0
  if (-not (Test-Path (Join-Path $SKILL_DIR "engineer-shovel\SKILL.md"))) { $missing = 1 }
  $names = @("branch","feat","fix","plan","refactor","review","quick","research","graph","update","alias")
  foreach ($name in $names) {
    if (-not (Test-Path (Join-Path $COMMAND_DIR "tool-${name}.md"))) { $missing = 1 }
  }
  if ($missing -eq 0 -and $FAILURES -eq 0) { Ok "Verification passed" }
  elseif ($missing -eq 0) { Warn "Engineer Shovel files OK, $FAILURES setup warning(s)" }
  else { Err "Verification failed"; exit 1 }
}

# ---------- main ----------
function Main {
  if ($Help) {
    @"
Usage: install.ps1 [-Mode minimal|recommended|full] [-Target opencode|claude|all|auto] [-Scope global|local] [-DryRun] [-WithGraphBuild] [-Yes]

One-click install:
  powershell -c "iex (iwr -useb <url>/install.ps1)" -- -Yes

Modes:
  --minimal      Skill + commands only
  --recommended  Skill, commands, Caveman, RTK, code-review-graph, superpowers, OpenSpec
  --full         Recommended + ECC + GSD (default)
  --dry-run      Preview without installing
  --with-graph-build  Build initial code-review-graph index
  --yes          Non-interactive: full install for OpenCode global (no prompts)
"@ | Out-Host
    return
  }

  # --yes flag: non-interactive full install for OpenCode
  if ($Yes) {
    $script:Mode = "full"
    $script:Target = "opencode"
    $script:Scope = "global"
  }

  Check-Prereqs
  $script:TARGETS = Resolve-Targets
  Info "OS: Windows | target: $($script:TARGETS -join ', ') | scope: $Scope | mode: $Mode"

  # Install components by mode
  switch ($Mode) {
    "minimal" { # no extras
    }
    "recommended" {
      Install-Superpowers $script:TARGETS
      Install-CodeReviewGraph
      Install-Caveman $script:TARGETS
      Install-RTK
      Install-OpenSpec
      Install-ClaudeMem $script:TARGETS
    }
    "full" {
      Install-ECC
      Install-GSD $script:TARGETS
      Install-Superpowers $script:TARGETS
      Install-CodeReviewGraph
      Install-Caveman $script:TARGETS
      Install-RTK
      Install-OpenSpec
      Install-ClaudeMem $script:TARGETS
    }
  }

  # Core install for each target
  foreach ($t in $script:TARGETS) {
    Set-TargetPaths $t
    New-Item -ItemType Directory -Force -Path $SKILL_DIR, $COMMAND_DIR | Out-Null
    Install-Skill $SKILL_DIR
    Install-Commands $COMMAND_DIR
    Verify-Install
  }

  Info "Installed: $($script:TARGETS -join ', ') | scope: $Scope | mode: $Mode"
  Info "Next: restart opencode session, then use skill(name=\"engineer-shovel\") or /tool-* commands."
  Info "Upgrade later with: /tool-update --check or /tool-update --full"
}

Main
