#!/usr/bin/env bash
# engineer-shovel — cross-platform installer (macOS/Linux/WSL)
# Windows: use install.ps1 instead
#
# Quick start:
#   bash install.sh                    # Interactive: prompts for target/mode/scope
#   bash install.sh --target opencode  # Non-interactive: full install for OpenCode
#   bash install.sh --target all       # Non-interactive: full install for both
#   bash install.sh --minimal          # Non-interactive: skill + commands only

set -euo pipefail

VERSION="1.8.0"
REPO_RAW="https://raw.githubusercontent.com"
REPO_OWNER="HunterXing"
REPO_NAME="engineer-shovel"
REPO_URL="${REPO_RAW}/${REPO_OWNER}/${REPO_NAME}/main"

# --- OS detection ---
detect_os() {
  case "$(uname -s)" in
    Darwin) echo "macos" ;;
    Linux)  echo "linux" ;;
    MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
    *)      echo "unknown" ;;
  esac
}

OS="$(detect_os)"
if [[ "$OS" == "windows" ]]; then
  echo "⚠ Windows detected. This script requires WSL or Git Bash."
  echo "  For native Windows support, use:"
  echo "    powershell -c \"iex (iwr -useb ${REPO_URL}/install.ps1)\""
  echo ""
  echo "  Continuing with limited support (WSL/Git Bash mode)..."
fi

ECC_REPO="https://github.com/affaan-m/everything-claude-code"
RTK_REPO="https://github.com/rtk-ai/rtk"
CODE_REVIEW_GRAPH_REPO="https://github.com/tirth8205/code-review-graph"
GSD_REPO="https://github.com/gsd-build/get-shit-done"
OPENSPEC_REPO="https://github.com/Fission-AI/OpenSpec"
CLAUDE_MEM_REPO="https://github.com/thedotmack/claude-mem"

RTK_SHA="4338f029ec43b69eb959748ec02cd7885200c264"
# ECC follows latest-installer strategy: the pinned SHA is intentionally
# dropped so users benefit from upstream bug fixes without manual bumps.
# Resolved against $ECC_REPO HEAD at install time.

MODE="full"
MODE_SET=0
TARGET="auto"
TARGET_SET=0
SCOPE="global"
SCOPE_SET=0
ENV="opencode"
SKILL_DIR="$HOME/.agents/skills"
COMMAND_DIR="$HOME/.config/opencode/commands"
OPENCODE_CONFIG_DIR="$HOME/.config/opencode"
PLUGIN_CACHE_DIR="$HOME/.claude/plugins/cache"
DRY_RUN=0
WITH_GRAPH_BUILD=0
FAILURES=0
TMP_ROOT=""
TARGETS=()

info() { printf 'ℹ %s\n' "$1"; }
ok() { printf '✔ %s\n' "$1"; }
warn() { printf '⚠ %s\n' "$1"; }
err() { printf '✘ %s\n' "$1" >&2; }

usage() {
  cat <<'USAGE'
Usage: ./install.sh [--minimal|--recommended|--full] [--target opencode|claude|all|auto] [--scope global|local]

One-click install:
  bash install.sh --yes              # Full install for OpenCode, global scope (no prompts)
  curl -fsSL <url>/install.sh | bash -s -- --yes

Modes:
  --minimal      Install only engineer-shovel skill and slash commands.
  --recommended  Skill, commands, Caveman, RTK, code-review-graph,
                 superpowers, and OpenSpec.
  --full         Install recommended components plus ECC and GSD,
                  engineer-shovel skill, and commands.
                  Interactive default.
  --dry-run      Print planned actions without writing files or cloning repos.
  --with-graph-build
                 In full mode, run initial code-review-graph build after install.

Targets:
  --target auto      Auto-detect OpenCode or Claude Code. Default for non-interactive use.
  --target opencode  Install OpenCode skill and slash commands.
  --target claude    Install Claude Code skill and slash commands.
  --target all       Install both OpenCode and Claude Code skill/commands.

Scope:
  --scope global  Install to home directory (~/.agents/skills, ~/.config/opencode/, ~/.claude/).
                  Default for non-interactive use.
  --scope local   Install to project directory (./.agents/skills, ./.opencode/, ./.claude/).
                  ECC skipped (no project-scope support). RTK is system-wide and stays global.

Flags:
  --yes, -y      Non-interactive: full install for OpenCode global (equivalent to
                 --full --target opencode --scope global). Suppresses all prompts.

When run in a terminal without explicit mode/target/scope, the installer prompts interactively
in order: target → mode → scope.

Routine drift checks and post-install repair belong to /tool-update:
  /tool-update --check [--target ...] [--scope global|local]
  /tool-update --full  [--target ...] [--scope global|local]

Model:
  install.sh     = first install and explicit repair hooks
  /tool-update   = router drift + component health + repair guidance
USAGE
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --minimal) MODE="minimal"; MODE_SET=1 ;;
      --recommended) MODE="recommended"; MODE_SET=1 ;;
      --full) MODE="full"; MODE_SET=1 ;;
      --target)
        if [[ $# -lt 2 ]]; then
          err "Missing value for --target"
          usage
          exit 1
        fi
        TARGET="$2"
        TARGET_SET=1
        shift
        ;;
      --target=*) TARGET="${1#--target=}"; TARGET_SET=1 ;;
      --opencode) TARGET="opencode"; TARGET_SET=1 ;;
      --claude|--claude-code) TARGET="claude"; TARGET_SET=1 ;;
      --all) TARGET="all"; TARGET_SET=1 ;;
      --scope)
        if [[ $# -lt 2 ]]; then
          err "Missing value for --scope"
          usage
          exit 1
        fi
        SCOPE="$2"
        SCOPE_SET=1
        shift
        ;;
      --scope=*) SCOPE="${1#--scope=}"; SCOPE_SET=1 ;;
      --global) SCOPE="global"; SCOPE_SET=1 ;;
      --local) SCOPE="local"; SCOPE_SET=1 ;;
      --dry-run) DRY_RUN=1 ;;
      --with-graph-build) WITH_GRAPH_BUILD=1 ;;
      --yes|-y) TARGET="opencode"; TARGET_SET=1; MODE="full"; MODE_SET=1; SCOPE="global"; SCOPE_SET=1 ;;
      -h|--help) usage; exit 0 ;;
      *) err "Unknown option: $1"; usage; exit 1 ;;
    esac
    shift
  done
}

is_interactive() {
  [[ -t 0 && -t 1 ]]
}

prompt_target() {
  local choice
  cat <<'PROMPT'
Select install target:
  1) OpenCode (recommended for ~/.config/opencode users)
  2) Claude Code
  3) Both OpenCode and Claude Code
  4) Auto-detect
PROMPT
  printf 'Target [1]: '
  read -r choice
  case "${choice:-1}" in
    1|opencode|OpenCode) TARGET="opencode" ;;
    2|claude|claude-code|Claude|ClaudeCode) TARGET="claude" ;;
    3|all|both|All|Both) TARGET="all" ;;
    4|auto|Auto) TARGET="auto" ;;
    *) err "Invalid target selection: ${choice}"; exit 1 ;;
  esac
}

prompt_mode() {
  local choice
  cat <<'PROMPT'
Select install mode:
   1) Full: recommended components plus ECC and GSD (default)
  2) Recommended: skill + commands + Caveman + RTK + code-review-graph + superpowers + OpenSpec
  3) Minimal: skill + commands only
PROMPT
  printf 'Mode [1]: '
  read -r choice
  case "${choice:-1}" in
    1|full|Full) MODE="full" ;;
    2|recommended|Recommended) MODE="recommended" ;;
    3|minimal|Minimal) MODE="minimal" ;;
    *) err "Invalid mode selection: ${choice}"; exit 1 ;;
  esac
}

prompt_scope() {
  local choice
  cat <<'PROMPT'
Select install scope:
  1) Global: install to home directory (~/.agents/skills, ~/.claude/, etc.) (default)
  2) Local: install to project directory (./.agents/skills, ./.opencode/, etc.)
PROMPT
  printf 'Scope [1]: '
  read -r choice
  case "${choice:-1}" in
    1|global|Global) SCOPE="global" ;;
    2|local|Local) SCOPE="local" ;;
    *) err "Invalid scope selection: ${choice}"; exit 1 ;;
  esac
}

configure_interactive_choices() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    if [[ "$TARGET_SET" -eq 0 ]]; then
      TARGET="auto"
    fi
    if [[ "$SCOPE_SET" -eq 0 ]]; then
      SCOPE="global"
    fi
    if is_interactive && { [[ "$TARGET_SET" -eq 0 ]] || [[ "$SCOPE_SET" -eq 0 ]] || [[ "$MODE_SET" -eq 0 ]]; }; then
      info "DRY-RUN: using non-interactive defaults (mode=${MODE}, target=${TARGET}, scope=${SCOPE})"
      info "DRY-RUN: pass explicit flags if you want to preview another combination."
    fi
    return
  fi

  if is_interactive; then
    if [[ "$TARGET_SET" -eq 0 ]]; then
      prompt_target
    fi
    if [[ "$MODE_SET" -eq 0 ]]; then
      prompt_mode
    fi
    if [[ "$SCOPE_SET" -eq 0 ]]; then
      prompt_scope
    fi
  fi
}

record_failure() {
  warn "$1"
  FAILURES=$((FAILURES + 1))
}

run_or_print() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: $*"
  else
    "$@"
  fi
}

download_file() {
  local url="$1"
  local target_path="$2"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: download ${url} -> ${target_path}"
    return 0
  fi

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 3 --retry-delay 2 "$url" -o "$target_path"
  elif command -v wget >/dev/null 2>&1; then
    wget -q --retry-connrefused --tries=3 "$url" -O "$target_path"
  else
    err "Neither curl nor wget found"
    return 1
  fi
}

ensure_tmp_root() {
  if [[ -z "$TMP_ROOT" ]]; then
    TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/engineer-shovel.XXXXXX" 2>/dev/null || echo "/tmp/engineer-shovel.$$")"
    mkdir -p "$TMP_ROOT"
  fi
}

cleanup_tmp() {
  if [[ -n "$TMP_ROOT" && -d "$TMP_ROOT" ]]; then
    rm -rf "$TMP_ROOT"
  fi
}

clone_pinned_repo() {
  local repo_url="$1"
  local commit_sha="$2"
  local target_dir="$3"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: clone ${repo_url} at ${commit_sha} -> ${target_dir}"
    return 0
  fi

  local clone_err
  clone_err="$(git clone --no-tags --filter=blob:none "$repo_url" "$target_dir" 2>&1)" || {
    err "Clone failed for ${repo_url}: ${clone_err}"
    return 1
  }
  git -C "$target_dir" checkout --detach "$commit_sha" >/dev/null 2>&1 || {
    err "Checkout failed for ${repo_url} at ${commit_sha}"
    return 1
  }
  local actual_sha
  actual_sha="$(git -C "$target_dir" rev-parse HEAD)"
  if [[ "$actual_sha" != "$commit_sha" ]]; then
    err "Pinned source verification failed for ${repo_url}: expected ${commit_sha}, got ${actual_sha}"
    return 1
  fi
}

check_prereqs() {
  local missing=()
  for cmd in git curl; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      missing+=("$cmd")
    fi
  done

  if [[ ${#missing[@]} -gt 0 ]]; then
    err "Missing required tools: ${missing[*]}"
    case "$OS" in
      macos) info "Install: brew install ${missing[*]}" ;;
      linux) info "Install: apt install ${missing[*]}  (or your distro's equivalent)" ;;
    esac
    exit 1
  fi

  if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    warn "Running as root will install files under HOME=${HOME}. Re-run without sudo if this is not intended."
  fi

  # Ensure pipx is available
  if ! command -v pipx >/dev/null 2>&1; then
    # Add common paths before checking
    export PATH="$HOME/.local/bin:$HOME/Library/Python/3.9/bin:$HOME/Library/Python/3.10/bin:$HOME/Library/Python/3.11/bin:$HOME/Library/Python/3.12/bin:$HOME/Library/Python/3.13/bin:$PATH"
  fi
  if ! command -v pipx >/dev/null 2>&1; then
    if command -v python3 >/dev/null 2>&1; then
      info "Installing pipx via pip..."
      if python3 -m pip install --user pipx 2>&1; then
        python3 -m pipx ensurepath 2>/dev/null || true
        export PATH="$HOME/.local/bin:$PATH"
        if ! command -v pipx >/dev/null 2>&1; then
          warn "pipx installed but not in PATH. Add ~/.local/bin to your PATH."
        fi
      else
        warn "pipx install failed; some features may be unavailable"
      fi
    else
      warn "python3 not found; pipx install skipped"
    fi
  fi
}

node_version_at_least() {
  local min_major="$1"
  local min_minor="$2"
  local min_patch="$3"

  command -v node >/dev/null 2>&1 || return 1
  local raw version major minor patch
  raw="$(node -v 2>/dev/null || true)"
  version="${raw#v}"
  IFS=. read -r major minor patch <<<"$version"
  major="${major:-0}"
  minor="${minor:-0}"
  patch="${patch:-0}"

  [[ "$major" =~ ^[0-9]+$ && "$minor" =~ ^[0-9]+$ && "$patch" =~ ^[0-9]+$ ]] || return 1
  if (( major > min_major )); then return 0; fi
  if (( major < min_major )); then return 1; fi
  if (( minor > min_minor )); then return 0; fi
  if (( minor < min_minor )); then return 1; fi
  (( patch >= min_patch ))
}

resolve_targets() {
  TARGETS=()
  case "$TARGET" in
    opencode) TARGETS=(opencode) ;;
    claude|claude-code) TARGETS=(claude-code) ;;
    all|both) TARGETS=(opencode claude-code) ;;
    auto)
      if command -v opencode >/dev/null 2>&1; then
        TARGETS=(opencode)
      elif command -v claude >/dev/null 2>&1; then
        TARGETS=(claude-code)
      else
        warn "Neither opencode nor claude was found; defaulting to OpenCode target paths."
        TARGETS=(opencode)
      fi
      ;;
    *) err "Unknown target: ${TARGET}"; usage; exit 1 ;;
  esac
}

validate_scope() {
  case "$SCOPE" in
    global|local) ;;
    *) err "Invalid scope: ${SCOPE}. Must be 'global' or 'local'."; usage; exit 1 ;;
  esac
}

set_target_paths() {
  local target="$1"
  case "$target" in
    opencode)
      ENV="opencode"
      if [[ "$SCOPE" == "local" ]]; then
        SKILL_DIR="./.agents/skills"
        COMMAND_DIR="./.opencode/commands"
        OPENCODE_CONFIG_DIR="./.opencode"
      else
        SKILL_DIR="$HOME/.agents/skills"
        COMMAND_DIR="$HOME/.config/opencode/commands"
        OPENCODE_CONFIG_DIR="$HOME/.config/opencode"
      fi
      ;;
    claude-code)
      ENV="claude-code"
      if [[ "$SCOPE" == "local" ]]; then
        SKILL_DIR="./.claude/skills"
        COMMAND_DIR="./.claude/commands"
      else
        SKILL_DIR="$HOME/.claude/skills"
        COMMAND_DIR="$HOME/.claude/commands"
      fi
      ;;
    *) err "Unknown resolved target: ${target}"; exit 1 ;;
  esac
}

prepare_target_dirs() {
  local target="$1"
  set_target_paths "$target"
  run_or_print mkdir -p "$SKILL_DIR" "$COMMAND_DIR"
  ok "Mode: ${MODE}; target: ${ENV}; scope: ${SCOPE}; skill_dir: ${SKILL_DIR}; command_dir: ${COMMAND_DIR}"
}

copy_or_download_file() {
  local local_path="$1"
  local remote_path="$2"
  local target_path="$3"

  if [[ -f "$local_path" ]]; then
    run_or_print cp "$local_path" "$target_path"
  else
    download_file "${REPO_URL}/${remote_path}" "$target_path"
  fi
}

install_skill() {
  local target="$SKILL_DIR/engineer-shovel"
  run_or_print mkdir -p "$target"
  copy_or_download_file "$(dirname "$0")/SKILL.md" "SKILL.md" "$target/SKILL.md"
  ok "Installed skill → ${target}/SKILL.md"
}

install_commands() {
  local src_dir
  src_dir="$(dirname "$0")/commands"
  local names=(branch feat fix plan refactor review quick research graph update alias)
  local count=0

  run_or_print mkdir -p "$COMMAND_DIR"
  for name in "${names[@]}"; do
    local target="$COMMAND_DIR/tool-${name}.md"
    if [[ -d "$src_dir" && -f "$src_dir/tool-${name}.md" ]]; then
      run_or_print cp "$src_dir/tool-${name}.md" "$target"
    else
      download_file "${REPO_URL}/commands/tool-${name}.md" "$target"
    fi
    count=$((count + 1))
  done

  ok "Installed ${count} slash command files → ${COMMAND_DIR}/"
}

# ---------- Caveman: Official installer ----------

# Caveman v1.9.1 is the published tag; install.sh is a Node wrapper that
# forwards flags to bin/install.js. Pin the tag so first-install is
# deterministic; bump via /tool-update or manual edit when upstream changelog
# warrants it.
CAVEMAN_INSTALLER_URL="https://raw.githubusercontent.com/JuliusBrussee/caveman/v1.9.1/install.sh"

_caveman_installed() {
  local target="$1"
  case "$target" in
    opencode)
      # v1.9.1 install drops a plugin dir at ~/.config/opencode/plugins/caveman/
      # plus commands/caveman.md; legacy v1.7 left a SKILL.md at
      # ~/.agents/skills/caveman/SKILL.md. Either is enough evidence.
      [[ -d "$HOME/.config/opencode/plugins/caveman" ]] && return 0
      [[ -f "$HOME/.config/opencode/commands/caveman.md" ]] && return 0
      [[ -d "$HOME/.agents/skills/caveman" ]] && return 0
      [[ -d "$HOME/.agents/skills/JuliusBrussee-caveman" ]] && return 0
      # Try npx skills list as fallback
      local out
      out="$(npx -y skills list 2>/dev/null)" || true
      echo "$out" | grep -qi caveman && return 0
      return 1
      ;;
    claude-code)
      # Check if caveman plugin is installed for Claude Code
      local out
      out="$(claude plugin list 2>/dev/null)" || true
      echo "$out" | grep -qi caveman && return 0
      # Also check if plugin directory exists
      [[ -d "$HOME/.claude/plugins/caveman" ]] && return 0
      return 1
      ;;
    *)
      return 1
      ;;
  esac
}

install_caveman_for_target() {
  local target="$1"

  # Map target to Caveman's --only <agent-id> flag. Use an ARRAY so the
  # two words are forwarded as separate argv entries — otherwise
  # `bash -s -- "--only opencode"` would hand npx a single token
  # "--only opencode" which caveman v1.9.1 install.js then parses as one
  # unknown flag.
  local -a agent_args=()
  case "$target" in
    opencode) agent_args=(--only opencode) ;;
    claude-code) agent_args=(--only claude) ;;
    *) record_failure "Unknown target for Caveman: ${target}"; return 1 ;;
  esac

  local -a upstream_args=("${agent_args[@]}" --force)
  if [[ "$MODE" == "recommended" ]]; then
    upstream_args+=(--minimal)
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: Caveman official installer for ${target}"
    info "  curl -fsSL ${CAVEMAN_INSTALLER_URL} | bash -s -- ${upstream_args[*]}"
    if [[ "$SCOPE" == "local" ]]; then
      warn "DRY-RUN: Caveman does not support project-scoped installation."
      warn "  Will install globally. Agent discovers skills from home directory."
    fi
    return 0
  fi

  # v1.9.1 install layout moves files into ~/.config/opencode/{plugins,
  # commands,skills,agents} and patches AGENTS.md; the legacy ~/.agents/
  # skills/caveman/SKILL.md is no longer created. Detection looks at the
  # v1.9.1 markers (plugin/ + commands/caveman.md).
  if _caveman_installed "$target"; then
    ok "Caveman already installed for ${target}"
    return 0
  fi

  if [[ "$SCOPE" == "local" ]]; then
    warn "Caveman does not support project-scoped installation."
    warn "  Installing globally. Agent discovers skills from home directory."
  fi

  info "Installing Caveman for ${target} via official installer (v1.9.1)..."
  local caveman_output
  if caveman_output="$(curl -fsSL "$CAVEMAN_INSTALLER_URL" | bash -s -- "${upstream_args[@]}" 2>&1)"; then
    printf '%s\n' "$caveman_output"
    ok "Caveman installed for ${target}"
  else
    local rc=$?
    printf '%s\n' "$caveman_output" >&2
    record_failure "Caveman install failed for ${target} (exit ${rc}). Install manually: curl -fsSL ${CAVEMAN_INSTALLER_URL} | bash -s -- ${upstream_args[*]}"
  fi
}

# ---------- Caveman: target dispatcher ----------

_install_caveman_for_targets() {
  local target
  for target in "${TARGETS[@]}"; do
    install_caveman_for_target "$target"
  done
}

install_ecc() {
  if [[ "$SCOPE" == "local" ]]; then
    info "ECC does not support local (project-scoped) installation. Skipping ECC."
    info "Use --scope global or install ECC separately."
    return 0
  fi
  if [[ -d "$PLUGIN_CACHE_DIR/ecc/ecc" || -d "$HOME/.claude/ecc" || -d "${OPENCODE_HOME:-$HOME/.config/opencode}/ecc" ]]; then
    ok "ECC already installed"
    link_ecc_commands
    return 0
  fi

  ensure_tmp_root
  local checkout_dir="$TMP_ROOT/ecc"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: clone ${ECC_REPO} (latest) -> ${checkout_dir}"
    link_ecc_commands
    return 0
  fi
  local ecc_target_flag=""
  local ecc_profile_flag=""
  if [[ ${#TARGETS[@]} -ge 1 ]]; then
    case "${TARGETS[0]}" in
      opencode)
        ecc_target_flag="--target opencode"
        ecc_profile_flag="--profile opencode"
        ;;
      claude-code)
        ecc_target_flag="--target claude"
        ecc_profile_flag=""
        ;;
      *)
        ecc_target_flag=""
        ecc_profile_flag=""
        ;;
    esac
  fi

  # ECC v2 install path: prefer the npm-published `ecc-universal@latest`
  # package which is pre-built and exposes an `ecc-install` bin via
  # scripts/install-apply.js. The git clone path falls back when npm
  # access is unavailable or when an upstream-mainspecifed tag must be
  # installed.
  if command -v npm >/dev/null 2>&1; then
    info "Installing ECC v2 via npm-published ecc-universal@latest (pre-built)..."
    local ecc_npm_output
    if ecc_npm_output="$(npx -y ecc-install ${ecc_target_flag} ${ecc_profile_flag} 2>&1)"; then
      printf '%s\n' "$ecc_npm_output"
      ok "ECC installed via npm"
      link_ecc_commands
      return 0
    fi
    local ecc_npm_rc=$?
    printf '%s\n' "$ecc_npm_output" >&2
    warn "ecc-install failed (exit ${ecc_npm_rc}); falling back to git clone"
  fi

  ensure_tmp_root
  local checkout_dir="$TMP_ROOT/ecc"
  local clone_err
  clone_err="$(git clone --no-tags --filter=blob:none "$ECC_REPO" "$checkout_dir" 2>&1)" || {
    err "Clone failed for ${ECC_REPO}: ${clone_err}"
    record_failure "Could not clone ECC source. Install manually: npm install -g ecc-universal && ecc-install ${ecc_target_flag} ${ecc_profile_flag}"
    return 1
  }
  local actual_sha
  actual_sha="$(git -C "$checkout_dir" rev-parse HEAD)"
  info "ECC checkout: ${actual_sha} (git-clone fallback path)"
  if [[ -f "$checkout_dir/install.sh" ]]; then
    local ecc_output
    local ecc_rc
    if ecc_output="$(timeout 600 bash "$checkout_dir/install.sh" ${ecc_target_flag} ${ecc_profile_flag} 2>&1)"; then
      printf '%s\n' "$ecc_output"
    else
      ecc_rc=$?
      printf '%s\n' "$ecc_output" >&2
      if [[ "$ecc_rc" -eq 124 ]]; then
        record_failure "ECC installer timed out after 600 seconds; retry manually if needed"
      else
        record_failure "ECC installer exited with code ${ecc_rc}; check log or retry: cd <ecc> && npm run build:opencode && bash install.sh ${ecc_target_flag} ${ecc_profile_flag}"
      fi
    fi
  fi
  ok "ECC install attempted"
  link_ecc_commands
}

# ---------- ECC command symlinks ----------

_ecc_cmd_dir() {
  local dir
  dir="$(npm root -g 2>/dev/null)/ecc-universal/commands" && [[ -d "$dir" ]] && { echo "$dir"; return 0; }
  dir="${NODE_PATH%%:*}/ecc-universal/commands" 2>/dev/null && [[ -d "$dir" ]] && { echo "$dir"; return 0; }
  # Check common global install locations
  for prefix in /usr/local/lib/node_modules /usr/lib/node_modules "$HOME/.local/share/vfox/cache/nodejs"/*/lib/node_modules; do
    dir="$prefix/ecc-universal/commands"
    [[ -d "$dir" ]] && { echo "$dir"; return 0; }
  done
  return 1
}

link_ecc_commands() {
  if [[ "$SCOPE" == "local" ]]; then
    info "Skipping ECC command symlinks for local scope"
    return 0
  fi

  local src_dir
  src_dir="$(_ecc_cmd_dir)" || {
    info "ECC commands directory not found; skipping symlinks"
    return 0
  }

  local cmd_dir="$HOME/.config/opencode/commands"
  run_or_print mkdir -p "$cmd_dir"

  local count=0
  for f in "$src_dir"/*.md; do
    local name
    name="$(basename "$f")"
    local target="$cmd_dir/$name"
    if [[ -f "$target" ]]; then
      if [[ ! -L "$target" ]]; then
        warn "Skipping ${name}: regular file exists (manual resolution needed)"
      fi
      continue
    fi
    if [[ "$DRY_RUN" -eq 1 ]]; then
      info "DRY-RUN: ln -s ${f} ${target}"
    else
      ln -sf "$f" "$target"
    fi
    count=$((count + 1))
  done

  if [[ "$count" -gt 0 ]]; then
    ok "Symlinked ${count} ECC commands → ${cmd_dir}/"
  fi
}

# ---------- superpowers command wrappers ----------

_gen_superpowers_commands() {
  local cmd_dir="$HOME/.config/opencode/commands"
  run_or_print mkdir -p "$cmd_dir"

  local count=0

  # Each entry: cmd_name skill_name description
  _gen_sp_cmd() {
    local cmd_name="$1"
    local skill_name="$2"
    local desc="$3"
    local target="$cmd_dir/superpowers:${cmd_name}.md"
    [[ -f "$target" ]] && return
    if [[ "$DRY_RUN" -eq 1 ]]; then
      info "DRY-RUN: create command /superpowers:${cmd_name} → skill(${skill_name})"
    else
      cat > "$target" <<CMDFILE
---
description: ${desc}
---

# /superpowers:${cmd_name}

Load the **${skill_name}** skill from superpowers:

\`\`\`
skill(name="${skill_name}")
\`\`\`

Follow its instructions exactly.
CMDFILE
    fi
    count=$((count + 1))
  }

  _gen_sp_cmd brainstorm brainstorming "Structured ideation for design decisions and creative problem-solving"
  _gen_sp_cmd parallel-agents dispatching-parallel-agents "Orchestrate parallel subagents for independent work streams"
  _gen_sp_cmd execute-plan executing-plans "Execute structured plans with verification checkpoints"
  _gen_sp_cmd finish-branch finishing-a-development-branch "Complete and verify a development branch before merge"
  _gen_sp_cmd receive-review receiving-code-review "Process and respond to code review feedback systematically"
  _gen_sp_cmd request-review requesting-code-review "Prepare and submit code changes for review"
  _gen_sp_cmd subagent-dev subagent-driven-development "Decompose complex tasks via specialized subagents"
  _gen_sp_cmd debug systematic-debugging "Scientific method debugging pipeline with root cause tracing"
  _gen_sp_cmd tdd test-driven-development "Test-driven development: red-green-refactor workflow"
  _gen_sp_cmd git-worktrees using-git-worktrees "Manage parallel development with git worktrees"
  _gen_sp_cmd superpowers using-superpowers "List, discover, and manage available superpowers skills"
  _gen_sp_cmd verify verification-before-completion "Structured verification checklist before task sign-off"
  _gen_sp_cmd write-plan writing-plans "Create structured planning documentation and execution roadmaps"
  _gen_sp_cmd write-skill writing-skills "Create and maintain reusable skill files"

  if [[ "$count" -gt 0 ]]; then
    ok "Created ${count} superpowers command wrappers → ${cmd_dir}/"
  fi
}

_superpowers_skills_dir() {
  # Find superpowers package directory
  local sp
  sp="$(npm root -g 2>/dev/null)/superpowers/skills" && [[ -d "$sp" ]] && { echo "$sp"; return 0; }
  sp="${NODE_PATH%%:*}/superpowers/skills" 2>/dev/null && [[ -d "$sp" ]] && { echo "$sp"; return 0; }
  # Check cache locations
  for prefix in "$HOME/.cache/opencode/packages/superpowers@"*/node_modules/superpowers/skills; do
    [[ -d "$prefix" ]] && { echo "$prefix"; return 0; }
  done
  return 1
}

_gsd_provisioned() {
  local target check_dir
  for target in "${TARGETS[@]}"; do
    case "$target" in
      opencode)
        if [[ "$SCOPE" == "local" ]]; then
          check_dir="./.opencode/commands"
        else
          # v1.50 dropped the trailing 's'; accept both layouts.
          check_dir="$HOME/.config/opencode"
        fi
        ;;
      claude-code)
        if [[ "$SCOPE" == "local" ]]; then
          check_dir="./.claude/commands"
        else
          check_dir="$HOME/.claude/commands"
        fi
        ;;
      *) return 1 ;;
    esac
    # Probe both 'commands/' and 'command/' under check_dir; a hit in either
    # is enough evidence that GSD has been provisioned on this target/scope.
    if [[ "$target" == "opencode" && "$SCOPE" != "local" ]]; then
      ls "$check_dir/commands"/gsd-*.md >/dev/null 2>&1 \
        || ls "$check_dir/command"/gsd-*.md >/dev/null 2>&1 \
        || return 1
    else
      ls "$check_dir"/gsd-*.md >/dev/null 2>&1 || return 1
    fi
  done
  return 0
}

install_gsd() {
  # Resolve GSD target flag from the already-resolved TARGETS array.
  # v1.50+ uses dash-form per-runtime flags: --opencode, --claude, --all, etc.
  if [[ ${#TARGETS[@]} -eq 2 ]]; then
    gsd_target="--all"
  elif [[ ${#TARGETS[@]} -eq 1 ]]; then
    case "${TARGETS[0]}" in
      opencode) gsd_target="--opencode" ;;
      claude-code) gsd_target="--claude" ;;
    esac
  fi

  local gsd_scope=""
  case "$SCOPE" in
    global) gsd_scope="--global" ;;
    local) gsd_scope="--local" ;;
  esac

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: git clone --depth=1 $GSD_REPO → /tmp/gsd; (cd /tmp/gsd && npm install --no-audit --no-fund --loglevel=error); (cd /tmp/gsd/sdk && npm install --no-audit --no-fund --loglevel=error && npm run build); node /tmp/gsd/bin/install.js ${gsd_target} ${gsd_scope}"
    return 0
  fi

  if _gsd_provisioned; then
    ok "GSD already installed for ${TARGET} / ${SCOPE}"
    return 0
  fi

  # GSD upstream main is now 1.50.0-canary.0; the npm package
  # `get-shit-done-cc` is deprecated. Install via git clone so we get the
  # canary build that upstream actually ships. Upstream's bin/install.js
  # requires a pre-built sdk/dist that lives outside the install.js path,
  # so we explicitly run `cd sdk && npm install && npm run build` first.
  info "Installing GSD via git clone + node bin/install.js (latest-installer strategy)..."
  ensure_tmp_root
  local gsd_checkout_dir="$TMP_ROOT/gsd"
  local clone_err
  clone_err="$(git clone --depth=1 --no-tags --filter=blob:none "$GSD_REPO" "$gsd_checkout_dir" 2>&1)" || {
    err "GSD clone failed: ${clone_err}"
    record_failure "Could not clone GSD source. Install manually: git clone https://github.com/gsd-build/get-shit-done && cd get-shit-done/sdk && npm install && npm run build && cd .. && node bin/install.js ${gsd_target} ${gsd_scope}"
    return 1
  }
  local gsd_sha
  gsd_sha="$(git -C "$gsd_checkout_dir" rev-parse HEAD)"
  info "GSD checkout: ${gsd_sha} (latest-installer strategy)"

  if [[ ! -d "$gsd_checkout_dir/node_modules" ]]; then
    info "Running npm install for GSD root (one-time)..."
    if ! (cd "$gsd_checkout_dir" && npm install --no-audit --no-fund --loglevel=error 2>&1); then
      record_failure "GSD root npm install failed; check Node ≥22 and retry"
      return 1
    fi
  fi

  # GSD SDK must be built before bin/install.js can dispatch slash-command
  # definitions; upstream explicitly tells the user to run `cd sdk &&
  # npm install && npm run build`. Mirror that.
  info "Building GSD SDK (sdk/dist)..."
  if [[ -d "$gsd_checkout_dir/sdk" ]]; then
    if ! (cd "$gsd_checkout_dir/sdk" \
        && npm install --no-audit --no-fund --loglevel=error \
        && npm run build 2>&1); then
      record_failure "GSD SDK build failed; retry manually: cd $gsd_checkout_dir/sdk && npm install && npm run build"
      return 1
    fi
  fi

  local gsd_output
  if gsd_output="$(timeout 600 node "$gsd_checkout_dir/bin/install.js" ${gsd_target} ${gsd_scope} 2>&1)"; then
    printf '%s\n' "$gsd_output"
    ok "GSD installed (build ${gsd_sha})"
  else
    local gsd_rc=$?
    printf '%s\n' "$gsd_output" >&2
    if [[ "$gsd_rc" -eq 124 ]]; then
      record_failure "GSD installer timed out after 600 seconds; retry manually if needed"
    else
      record_failure "GSD installer exited with code ${gsd_rc}; run: cd $gsd_checkout_dir/sdk && npm install && npm run build && cd .. && node bin/install.js ${gsd_target} ${gsd_scope}"
    fi
  fi
}

_superpowers_opencode_installed() {
  # Check via opencode plugin command (preferred)
  if command -v opencode >/dev/null 2>&1; then
    local out
    out="$(opencode plugin "superpowers@github:obra/superpowers" 2>&1)" || true
    echo "$out" | grep -qi "installed\|already" && return 0
  fi
  # Fallback: check config file
  local config_file="$HOME/.config/opencode/opencode.json"
  [[ -f "$config_file" ]] && grep -q "superpowers" "$config_file" 2>/dev/null
}

install_superpowers_opencode() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: opencode plugin "superpowers@github:obra/superpowers" -g"
    info "DRY-RUN: generate superpowers command wrappers"
    return 0
  fi

  if _superpowers_opencode_installed; then
    ok "Superpowers already configured for OpenCode"
    _gen_superpowers_commands
    return 0
  fi

  if command -v opencode >/dev/null 2>&1; then
    info "Installing superpowers via opencode plugin..."
    opencode plugin "superpowers@github:obra/superpowers" -g 2>&1 && {
      ok "Superpowers installed for OpenCode"
      _gen_superpowers_commands
      return 0
    }
    warn "opencode plugin "superpowers@github:obra/superpowers" failed; falling back to config edit"
  fi

  # Fallback: manually write plugin entry to opencode.json (legacy)
  local config_dir="$HOME/.config/opencode"
  local config_file="$config_dir/opencode.json"
  mkdir -p "$config_dir"

  if command -v node >/dev/null 2>&1; then
    node -e "
      const fs = require('fs');
      const path = '$config_file';
      let config = {};
      try { config = JSON.parse(fs.readFileSync(path, 'utf8')); } catch(e) {}
      if (!config.plugin) config.plugin = [];
      if (!Array.isArray(config.plugin)) config.plugin = [config.plugin];
      const entry = 'superpowers@git+https://github.com/obra/superpowers.git';
      if (!config.plugin.includes(entry)) {
        config.plugin.push(entry);
        fs.writeFileSync(path, JSON.stringify(config, null, 2) + '\n');
        console.log('Added superpowers to opencode.json');
      } else {
        console.log('superpowers already in opencode.json');
      }
    "
    ok "Superpowers plugin added to opencode.json (legacy)"
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c "
import json, sys
path = sys.argv[1]
with open(path) as f:
    data = json.load(f)
entry = 'superpowers@git+https://github.com/obra/superpowers.git'
if 'plugin' not in data:
    data['plugin'] = []
if isinstance(data['plugin'], str):
    data['plugin'] = [data['plugin']]
if entry not in data['plugin']:
    data['plugin'].insert(0, entry)
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
" "$config_file" || warn "Could not add superpowers. Add manually: opencode plugin "superpowers@github:obra/superpowers" -g"
  else
    warn "No node or python3 found. Install manually: opencode plugin "superpowers@github:obra/superpowers" -g"
  fi
  _gen_superpowers_commands
}

install_superpowers_claude() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: claude plugin marketplace add https://github.com/obra/superpowers"
    info "DRY-RUN: claude plugin install superpowers@superpowers-dev"
    info "DRY-RUN: fallback: claude plugin install superpowers@claude-plugins-official"
    return 0
  fi

  local out
  out="$(claude plugin list 2>/dev/null)" || true
  if echo "$out" | grep -qi superpowers; then
    ok "Superpowers already installed for Claude Code"
    return 0
  fi

  info "Installing superpowers v6 (obra marketplace) for Claude Code..."
  # v6 is published via the obra/superpowers marketplace (declared in
  # .claude-plugin/marketplace.json as version 6.x). claude-plugins-official
  # marketplace only carries the older v5 line, so we register obra's
  # marketplace first; claude-plugins-official remains the fallback for
  # offline / older setups where v5 is the only reachable option.
  if claude plugin marketplace add https://github.com/obra/superpowers --scope user >/dev/null 2>&1 \
    && claude plugin install superpowers@superpowers-dev --scope user 2>&1; then
    ok "Superpowers v6 installed (obra marketplace) for Claude Code"
    return 0
  fi
  warn "obra marketplace install failed; falling back to claude-plugins-official (v5)"

  if claude plugin install superpowers@claude-plugins-official 2>&1; then
    ok "Superpowers (fallback v5) installed for Claude Code"
  else
    local rc=$?
    record_failure "Superpowers Claude install failed (exit ${rc}). Manually: claude plugin marketplace add https://github.com/obra/superpowers && claude plugin install superpowers@superpowers-dev"
  fi
}

install_superpowers() {
  local target
  for target in "${TARGETS[@]}"; do
    case "$target" in
      opencode) install_superpowers_opencode ;;
      claude-code) install_superpowers_claude ;;
    esac
  done
}

install_rtk() {
  if [[ "$SCOPE" == "local" ]]; then
    info "RTK is a system tool — installs globally regardless of scope selection."
    info "Binary will be installed to ~/.local/bin/ or ~/.cargo/bin/."
  fi

  if command -v rtk >/dev/null 2>&1; then
    ok "RTK already installed"
    init_rtk
    return 0
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"
    info "DRY-RUN: rtk init for ${TARGETS[*]}"
    return 0
  fi

  # Use a background subshell with timeout for the official installer
  info "Installing RTK via official installer (may take a minute)..."
  local rtk_installed=0

  # Attempt 1: official installer with 90s timeout
  local tmp_rtk_out
  tmp_rtk_out="$(mktemp "${TMPDIR:-/tmp}/rtk-install.XXXXXX")"
  if timeout 90 bash -c "curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh" > "$tmp_rtk_out" 2>&1; then
    cat "$tmp_rtk_out"
    rm -f "$tmp_rtk_out"
    rtk_installed=1
  else
    local rtk_exit=$?
    rm -f "$tmp_rtk_out"
    info "Official installer timed out (exit ${rtk_exit}). Trying fallback..."
  fi

  # Attempt 2: cargo install (if available)
  if [[ "$rtk_installed" -eq 0 ]] && command -v cargo >/dev/null 2>&1; then
    info "Installing RTK via cargo (pinned commit)..."
    if timeout 300 cargo install --git "$RTK_REPO" --rev "$RTK_SHA" rtk 2>&1; then
      rtk_installed=1
    else
      warn "cargo install failed"
    fi
  fi

  # Attempt 3: download prebuilt binary for common platforms
  if [[ "$rtk_installed" -eq 0 ]]; then
    local arch=""
    case "$(uname -m)" in
      x86_64|amd64) arch="x86_64" ;;
      aarch64|arm64) arch="arm64" ;;
    esac
    local os=""
    case "$OS" in
      macos) os="apple-darwin" ;;
      linux) os="unknown-linux-gnu" ;;
    esac
    if [[ -n "$arch" && -n "$os" ]]; then
      local rtk_url="https://github.com/rtk-ai/rtk/releases/latest/download/rtk-${arch}-${os}.tar.gz"
      info "Downloading RTK prebuilt binary from ${rtk_url}..."
      local tmp_dir
      tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/rtk-dl.XXXXXX")"
      if curl -fsSL --retry 3 "$rtk_url" -o "$tmp_dir/rtk.tar.gz" && tar xzf "$tmp_dir/rtk.tar.gz" -C "$tmp_dir" 2>/dev/null; then
        local rtk_bin
        rtk_bin="$(find "$tmp_dir" -name 'rtk' -type f 2>/dev/null | head -1)"
        if [[ -n "$rtk_bin" ]]; then
          install -d "$HOME/.local/bin" && install "$rtk_bin" "$HOME/.local/bin/rtk"
          export PATH="$HOME/.local/bin:$PATH"
          if command -v rtk >/dev/null 2>&1; then
            info "RTK prebuilt binary installed to ~/.local/bin/rtk"
            rtk_installed=1
          fi
        fi
      fi
      rm -rf "$tmp_dir"
    fi
  fi

  if [[ "$rtk_installed" -eq 1 ]]; then
    init_rtk
  else
    record_failure "RTK install failed. Manual: curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"
  fi
}

init_rtk() {
  local target
  if [[ "$DRY_RUN" -eq 1 ]]; then
    for target in "${TARGETS[@]}"; do
      case "$target" in
        opencode) info "DRY-RUN: rtk init -g --opencode" ;;
        claude-code) info "DRY-RUN: rtk init -g" ;;
      esac
    done
    return 0
  fi
  if ! command -v rtk >/dev/null 2>&1; then
    record_failure "RTK binary unavailable after install"
    return 1
  fi
  for target in "${TARGETS[@]}"; do
    case "$target" in
      opencode)
        rtk init -g --opencode 2>&1 || record_failure "RTK OpenCode init failed; run manually: rtk init -g --opencode"
        ;;
      claude-code)
        rtk init -g 2>&1 || record_failure "RTK Claude init failed; run manually: rtk init -g"
        ;;
    esac
  done
}

# ---------- MCP config writer ----------

_add_crg_mcp_to_config() {
  local config_file="$1"
  local config_dir
  config_dir="$(dirname "$config_file")"
  mkdir -p "$config_dir"

  if command -v node >/dev/null 2>&1; then
    node -e "
      const fs = require('fs');
      const path = '$config_file';
      let config = {};
      try { config = JSON.parse(fs.readFileSync(path, 'utf8')); } catch(e) { config = { '\\\$schema': 'https://opencode.ai/config.json' }; }
      if (!config.mcp) config.mcp = {};
      config.mcp['code-review-graph'] = {
        type: 'local',
        command: ['uvx', 'code-review-graph', 'serve'],
        enabled: true
      };
      fs.writeFileSync(path, JSON.stringify(config, null, 2) + '\n');
      console.log('Added code-review-graph MCP to ' + path);
    " 2>&1
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c "
import json, sys, os
path = sys.argv[1]
config = {}
if os.path.exists(path):
    with open(path) as f:
        config = json.load(f)
if '\$schema' not in config and not os.path.exists(path):
    config['\$schema'] = 'https://opencode.ai/config.json'
if 'mcp' not in config:
    config['mcp'] = {}
config['mcp']['code-review-graph'] = {
    'type': 'local',
    'command': ['uvx', 'code-review-graph', 'serve'],
    'enabled': True
}
with open(path, 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')
print('Added code-review-graph MCP to ' + path)
" "$config_file" 2>&1
  else
    cat >> "$config_file" <<'MCPCFG'

  "mcp": {
    "code-review-graph": {
      "type": "local",
      "command": ["uvx", "code-review-graph", "serve"],
      "enabled": true
    }
  }
MCPCFG
    warn "Could not safely merge MCP config; appended template to ${config_file}. Fix manually."
    return 1
  fi
  return 0
}

install_code_review_graph() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: pipx install code-review-graph || python3 -m pip install --user code-review-graph"
    local target
    for target in "${TARGETS[@]}"; do
      case "$target" in
        opencode)
          info "DRY-RUN: add MCP to opencode config"
          if [[ "$SCOPE" == "local" ]]; then
            info "  config: ./.opencode/opencode.json"
          else
            info "  config: ~/.config/opencode/opencode.json"
          fi
          ;;
        claude-code) info "DRY-RUN: code-review-graph install --platform claude-code" ;;
      esac
    done
    if [[ "$WITH_GRAPH_BUILD" -eq 1 ]]; then
      info "DRY-RUN: code-review-graph build"
    else
      info "DRY-RUN: Skipping code-review-graph build; pass --with-graph-build to run it"
    fi
    return 0
  fi

  if ! command -v code-review-graph >/dev/null 2>&1 && ! command -v uvx >/dev/null 2>&1; then
    info "Installing code-review-graph from PyPI..."
    if command -v pipx >/dev/null 2>&1; then
      pipx install code-review-graph 2>&1 || record_failure "code-review-graph pipx install failed"
    elif command -v python3 >/dev/null 2>&1; then
      python3 -m pip install --user code-review-graph 2>&1 || record_failure "code-review-graph pip install failed"
    else
      record_failure "Python 3 not found. Install code-review-graph manually: pipx install code-review-graph"
    fi
  fi

  # Configure MCP server (OpenCode uses new format; Claude Code uses old format)
  local target
  for target in "${TARGETS[@]}"; do
    case "$target" in
      opencode)
        local opencode_config
        if [[ "$SCOPE" == "local" ]]; then
          opencode_config="./.opencode/opencode.json"
          mkdir -p ./.opencode
        else
          opencode_config="$HOME/.config/opencode/opencode.json"
        fi
        info "Configuring code-review-graph MCP for OpenCode..."
        _add_crg_mcp_to_config "$opencode_config" || record_failure "Failed to configure code-review-graph MCP"
        if command -v code-review-graph >/dev/null 2>&1; then
          info "Removing old-format MCP config if present..."
          rm -f .opencode.json 2>/dev/null || true
        fi
        ;;
      claude-code)
        if command -v code-review-graph >/dev/null 2>&1; then
          info "Configuring code-review-graph for Claude Code..."
          code-review-graph install --platform claude-code 2>&1 || record_failure "code-review-graph install --platform claude-code failed; run manually"
        else
          record_failure "code-review-graph not installed; MCP config for Claude Code requires the binary"
        fi
        ;;
    esac
  done

  if [[ "$WITH_GRAPH_BUILD" -ne 1 ]]; then
    info "Skipping code-review-graph build; pass --with-graph-build to run it."
    return 0
  fi
  if command -v code-review-graph >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    info "Building code-review-graph for current repository..."
    code-review-graph build 2>&1 || record_failure "code-review-graph build failed; run manually: code-review-graph build"
  else
    info "Skipping code-review-graph build (no git worktree or binary not found)"
  fi
}

install_openspec() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: npm install -g @fission-ai/openspec@latest"
    info "DRY-RUN: Not running openspec init; initialize per project with: openspec init"
    return 0
  fi

  if command -v openspec >/dev/null 2>&1; then
    ok "OpenSpec already installed"
    return 0
  fi

  if ! command -v npm >/dev/null 2>&1; then
    record_failure "OpenSpec requires npm. Install manually after Node.js setup: npm install -g @fission-ai/openspec@latest"
    return 1
  fi

  if ! node_version_at_least 20 19 0; then
    record_failure "OpenSpec requires Node.js >=20.19.0. Skipping CLI install; see ${OPENSPEC_REPO}"
    return 1
  fi

  info "Installing OpenSpec CLI via npm..."
  local openspec_output
  if openspec_output="$(npm install -g @fission-ai/openspec@latest 2>&1)"; then
    printf '%s\n' "$openspec_output"
    ok "OpenSpec installed"
    info "OpenSpec is not initialized automatically. Run 'openspec init' inside each project that needs specs."
  else
    local openspec_rc=$?
    printf '%s\n' "$openspec_output" >&2
    record_failure "OpenSpec install failed (exit ${openspec_rc}). Manual: npm install -g @fission-ai/openspec@latest"
  fi
}

_claude_mem_installed() {
  local target="$1"
  case "$target" in
    opencode)
      local config="$HOME/.config/opencode/opencode.json"
      if [[ -f "$config" ]] && grep -qi "claude-mem" "$config" 2>/dev/null; then return 0; fi
      local config2="$HOME/.config/opencode/opencode.jsonc"
      if [[ -f "$config2" ]] && grep -qi "claude-mem" "$config2" 2>/dev/null; then return 0; fi
      return 1
      ;;
    claude-code)
      local out
      out="$(claude plugin list 2>/dev/null)" || true
      echo "$out" | grep -qi claude-mem && return 0
      return 1
      ;;
    *)
      return 1
      ;;
  esac
}

install_claude_mem_for_target() {
  local target="$1"
  local ide_flag=""

  case "$target" in
    opencode) ide_flag="--ide opencode" ;;
    claude-code) ide_flag="--ide claude" ;;
    *) record_failure "Unknown target for claude-mem: ${target}"; return 1 ;;
  esac

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: npx -y claude-mem install ${ide_flag}"
    return 0
  fi

  if _claude_mem_installed "$target"; then
    ok "claude-mem already installed for ${target}"
    return 0
  fi

  # Auto-install Bun if missing
  if ! command -v bun >/dev/null 2>&1; then
    info "Bun not found; installing Bun first..."
    local bun_ok=0
    # Official Bun installer
    if curl -fsSL https://bun.sh/install | bash 2>&1; then
      export PATH="$HOME/.bun/bin:$PATH"
      if command -v bun >/dev/null 2>&1; then
        info "Bun installed successfully"
        bun_ok=1
      fi
    fi
    if [[ "$bun_ok" -eq 0 ]]; then
      record_failure "Bun install failed. claude-mem requires Bun. Install: curl -fsSL https://bun.sh/install | bash"
      return 1
    fi
  fi

  info "Installing claude-mem for ${target}..."
  local mem_output
  if mem_output="$(npx -y claude-mem install ${ide_flag} 2>&1)"; then
    printf '%s\n' "$mem_output"
    ok "claude-mem installed for ${target}"
  else
    local mem_rc=$?
    printf '%s\n' "$mem_output" >&2
    record_failure "claude-mem install failed for ${target} (exit ${mem_rc}). Manual: npx claude-mem install ${ide_flag}"
  fi
}

_install_claude_mem_for_targets() {
  local target
  for target in "${TARGETS[@]}"; do
    install_claude_mem_for_target "$target"
  done
}

configure_memory_hint() {
  local file=""
  if [[ "$ENV" == "opencode" ]]; then
    if [[ "$SCOPE" == "local" ]]; then
      file="./AGENTS.md"
    elif [[ -f "$HOME/.config/opencode/AGENTS.md" ]]; then
      file="$HOME/.config/opencode/AGENTS.md"
    fi
  elif [[ "$ENV" == "claude-code" ]]; then
    if [[ "$SCOPE" == "local" ]]; then
      file="./CLAUDE.md"
    elif [[ -f "$HOME/.claude/CLAUDE.md" ]]; then
      file="$HOME/.claude/CLAUDE.md"
    fi
  fi

  if [[ -n "$file" && -f "$file" ]] && ! grep -q "engineer-shovel" "$file" 2>/dev/null; then
    if [[ "$DRY_RUN" -eq 1 ]]; then
      info "DRY-RUN: append engineer-shovel hint -> ${file}"
      return 0
    fi
    cat >> "$file" <<'EOF'

## engineer-shovel
- Load on demand with: `skill(name="engineer-shovel")`
- Prefer cost modes: `--fast`, `--standard`, `--deep`.
EOF
    ok "Added engineer-shovel hint → ${file}"
  fi
}

verify_install() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    ok "Dry-run completed without writing files"
    return 0
  fi

  local missing_count=0
  [[ -s "$SKILL_DIR/engineer-shovel/SKILL.md" ]] || missing_count=1

  local names=(branch feat fix plan refactor review quick research graph update alias)
  for name in "${names[@]}"; do
    [[ -s "$COMMAND_DIR/tool-${name}.md" ]] || missing_count=1
  done

  if [[ "$missing_count" -eq 0 && "$FAILURES" -eq 0 ]]; then
    ok "Verification passed"
  elif [[ "$missing_count" -eq 0 ]]; then
    warn "Verification passed for Engineer Shovel files with ${FAILURES} optional setup warning(s)"
  else
    err "Verification failed: missing installed files or ${FAILURES} non-fatal setup failure(s)"
    exit 1
  fi
}

install_core_for_target() {
  local target="$1"
  prepare_target_dirs "$target"
  install_skill
  install_commands
  configure_memory_hint
  verify_install
}

main() {
  trap cleanup_tmp EXIT
  parse_args "$@"
  configure_interactive_choices
  validate_scope
  check_prereqs
  resolve_targets

  info "OS: ${OS} | target: ${TARGETS[*]} | scope: ${SCOPE} | mode: ${MODE}"

  case "$MODE" in
    minimal)
      ;;
    recommended)
      install_superpowers
      install_code_review_graph
      _install_caveman_for_targets
      install_rtk
      install_openspec
      _install_claude_mem_for_targets
      ;;
    full)
      install_ecc
      install_gsd
      install_superpowers
      install_code_review_graph
      _install_caveman_for_targets
      install_rtk
      install_openspec
      _install_claude_mem_for_targets
      ;;
  esac

  local target
  for target in "${TARGETS[@]}"; do
    install_core_for_target "$target"
  done

  info "Installed targets: ${TARGETS[*]}  scope: ${SCOPE}  mode: ${MODE}"
  for target in "${TARGETS[@]}"; do
    set_target_paths "$target"
    info "${ENV}: skill=${SKILL_DIR}/engineer-shovel/SKILL.md commands=${COMMAND_DIR}/tool-*.md"
  done
  info "Component strategy remains mixed by design: some tools are pinned, some follow upstream latest, and some are effectively global."

  # Print success summary
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  🪖 Engineer Shovel v${VERSION} — Installation Complete          ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  # Show installed version comparison
  local installed_version=""
  if [[ -f "$SKILL_DIR/engineer-shovel/SKILL.md" ]]; then
    installed_version="$(grep -o 'version: "[^"]*"' "$SKILL_DIR/engineer-shovel/SKILL.md" 2>/dev/null | head -1 | sed 's/version: "//;s/"//' || true)"
  fi

  ok "Next steps:"
  echo "  1. Restart your agent session (opencode or claude)"
  echo "  2. Load the skill: skill(name=\"engineer-shovel\")"
  echo "  3. Or run commands directly: /tool-quick, /tool-fix, /tool-feat, etc."
  echo ""

  if [[ -n "$installed_version" && "$installed_version" != "$VERSION" ]]; then
    info "Upgraded: v${installed_version} → v${VERSION}"
    echo ""
  fi

  info "Upgrade later:"
  echo "  bash install.sh --target opencode           # Re-run installer"
  echo "  bash install.sh --yes                       # One-click upgrade (no prompts)"
  echo ""
  info "Useful commands:"
  echo "  /tool-update --check    # Check installation status"
  echo "  /tool-graph status      # Check code-review-graph health"
  echo ""

  if [[ "$OS" == "linux" || "$OS" == "macos" ]]; then
    info "Windows users: use install.ps1 instead"
    echo "  powershell -c \"iex (iwr -useb https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/install.ps1)\""
  fi

  if [[ "$FAILURES" -gt 0 ]]; then
    echo ""
    warn "${FAILURES} optional component(s) had warnings. Run /tool-update --check for details."
  fi
}

main "$@"
