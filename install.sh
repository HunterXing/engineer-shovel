#!/usr/bin/env bash
# engineer-shovel — token-aware installer

set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com"
REPO_OWNER="HunterXing"
REPO_NAME="engineer-shovel"
REPO_URL="${REPO_RAW}/${REPO_OWNER}/${REPO_NAME}/main"

ECC_REPO="https://github.com/affaan-m/everything-claude-code"
RTK_REPO="https://github.com/rtk-ai/rtk"

ECC_SHA="841beea45cb25ba51f29fa45b7e272938d19b80a"
RTK_SHA="4338f029ec43b69eb959748ec02cd7885200c264"

MODE="full"
MODE_SET=0
TARGET="auto"
TARGET_SET=0
SCOPE="global"
SCOPE_SET=0
ENV="opencode"
SKILL_DIR="$HOME/.agents/skills"
COMMAND_DIR="$HOME/.config/opencode/commands"
PLUGIN_CACHE_DIR="$HOME/.claude/plugins/cache"
DRY_RUN=0
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

Modes:
  --minimal      Install only engineer-shovel skill and slash commands.
  --recommended Install skill, commands, and Caveman plugin.
  --full         Install ECC, GSD, superpowers, Caveman, RTK, engineer-shovel skill, and commands.
                  Interactive default.
  --dry-run      Print planned actions without writing files or cloning repos.

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

When run in a terminal without explicit mode/target/scope, the installer prompts interactively
in order: target → mode → scope.
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
   1) Full: ECC, GSD, superpowers, Caveman, RTK, engineer-shovel skill, and commands (default)
  2) Recommended: skill + commands + Caveman
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
    info "DRY-RUN: curl -fsSL --retry 3 ${url} -o ${target_path}"
    return 0
  fi

  curl -fsSL --retry 3 --retry-delay 2 "$url" -o "$target_path"
}

ensure_tmp_root() {
  if [[ -z "$TMP_ROOT" ]]; then
    TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/engineer-shovel.XXXXXX")"
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
    exit 1
  fi

  if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    warn "Running as root will install files under HOME=${HOME}. Re-run without sudo if this is not intended."
  fi
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
      else
        SKILL_DIR="$HOME/.agents/skills"
        COMMAND_DIR="$HOME/.config/opencode/commands"
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
  local src_dir="$(dirname "$0")/commands"
  local names=(branch feat fix plan refactor review brainstorm quick blueprint research statistic update)
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

  ok "Installed ${count} slash commands → ${COMMAND_DIR}/"
}

# ---------- Caveman: Official installer ----------

CAVEMAN_INSTALLER_URL="https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh"

_caveman_installed() {
  local target="$1"
  case "$target" in
    opencode)
      # Check multiple possible locations for caveman skill
      [[ -d "$HOME/.agents/skills/caveman" ]] && return 0
      [[ -d "$HOME/.agents/skills/JuliusBrussee-caveman" ]] && return 0
      # Check if caveman command exists in OpenCode commands
      [[ -f "$HOME/.config/opencode/commands/caveman.md" ]] && return 0
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
  local agent_flag=""

  # Map target to Caveman's --only flag
  case "$target" in
    opencode) agent_flag="--only opencode" ;;
    claude-code) agent_flag="--only claude" ;;
    *) record_failure "Unknown target for Caveman: ${target}"; return 1 ;;
  esac

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: Caveman official installer for ${target}"
    info "  curl -fsSL ${CAVEMAN_INSTALLER_URL} | bash -s -- ${agent_flag} --minimal"
    if [[ "$SCOPE" == "local" ]]; then
      warn "DRY-RUN: Caveman does not support project-scoped installation."
      warn "  Will install globally. Agent discovers skills from home directory."
    fi
    return 0
  fi

  if _caveman_installed "$target"; then
    ok "Caveman already installed for ${target}"
    return 0
  fi

  if [[ "$SCOPE" == "local" ]]; then
    warn "Caveman does not support project-scoped installation."
    warn "  Installing globally. Agent discovers skills from home directory."
  fi

  info "Installing Caveman for ${target} via official installer..."
  local caveman_output
  if caveman_output="$(curl -fsSL "$CAVEMAN_INSTALLER_URL" | bash -s -- ${agent_flag} --minimal 2>&1)"; then
    printf '%s\n' "$caveman_output"
    ok "Caveman installed for ${target}"
  else
    local rc=$?
    printf '%s\n' "$caveman_output" >&2
    record_failure "Caveman install failed for ${target} (exit ${rc}). Install manually: curl -fsSL ${CAVEMAN_INSTALLER_URL} | bash -s -- ${agent_flag}"
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
    return 0
  fi

  ensure_tmp_root
  local checkout_dir="$TMP_ROOT/ecc"
  if clone_pinned_repo "$ECC_REPO" "$ECC_SHA" "$checkout_dir"; then
    if [[ -f "$checkout_dir/install.sh" ]]; then
      if [[ "$DRY_RUN" -eq 1 ]]; then
        info "DRY-RUN: timeout 600 bash ${checkout_dir}/install.sh"
      else
        local ecc_output
        local ecc_rc
        if ecc_output="$(timeout 600 bash "$checkout_dir/install.sh" 2>&1)"; then
          printf '%s\n' "$ecc_output"
        else
          ecc_rc=$?
          printf '%s\n' "$ecc_output" >&2
          if [[ "$ecc_rc" -eq 124 ]]; then
            record_failure "ECC installer timed out after 600 seconds; retry manually if needed"
          else
            record_failure "ECC installer exited with code ${ecc_rc}; run manually to diagnose"
          fi
        fi
      fi
    fi
    ok "ECC install attempted"
  else
    record_failure "Could not clone pinned ECC source. Install manually: /plugin install ecc@ecc"
  fi
}

_gsd_provisioned() {
  local target check_dir
  for target in "${TARGETS[@]}"; do
    case "$target" in
      opencode)
        if [[ "$SCOPE" == "local" ]]; then
          check_dir="./.opencode/commands"
        else
          check_dir="$HOME/.config/opencode/commands"
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
    ls "$check_dir"/gsd-*.md >/dev/null 2>&1 || return 1
  done
  return 0
}

install_gsd() {
  # Resolve GSD target flag from the already-resolved TARGETS array
  if [[ ${#TARGETS[@]} -eq 2 ]]; then
    gsd_target="--both"
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
    info "DRY-RUN: npx -y get-shit-done-cc@latest ${gsd_target} ${gsd_scope}"
    return 0
  fi

  if _gsd_provisioned; then
    ok "GSD already installed for ${TARGET} / ${SCOPE}"
    return 0
  fi

  info "Installing GSD via official installer (npx get-shit-done-cc@latest)..."
  local gsd_output
  if gsd_output="$(npx -y get-shit-done-cc@latest "${gsd_target}" "${gsd_scope}" 2>&1)"; then
    printf '%s\n' "$gsd_output"
    ok "GSD installed"
  else
    local gsd_rc=$?
    printf '%s\n' "$gsd_output" >&2
    record_failure "GSD installer exited with code ${gsd_rc}; run manually: npx -y get-shit-done-cc@latest ${gsd_target} ${gsd_scope}"
  fi
}

SUPERPOWERS_REPO="https://github.com/obra/superpowers.git"

_superpowers_opencode_installed() {
  local config_file="$HOME/.config/opencode/opencode.json"
  [[ -f "$config_file" ]] && grep -q "superpowers" "$config_file" 2>/dev/null
}

install_superpowers_opencode() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: Add superpowers plugin to ~/.config/opencode/opencode.json"
    return 0
  fi

  if _superpowers_opencode_installed; then
    ok "Superpowers already configured for OpenCode"
    return 0
  fi

  local config_dir="$HOME/.config/opencode"
  local config_file="$config_dir/opencode.json"
  
  mkdir -p "$config_dir"
  
  if [[ ! -f "$config_file" ]]; then
    # Create new config file with plugin array
    cat > "$config_file" <<'EOF'
{
  "plugin": ["superpowers@git+https://github.com/obra/superpowers.git"]
}
EOF
    ok "Created opencode.json with superpowers plugin"
    return 0
  fi

  # Config file exists, try to add superpowers to plugin array
  if command -v node >/dev/null 2>&1; then
    # Use node to safely modify JSON
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
    ok "Superpowers plugin added to opencode.json"
  else
    # Fallback: use Python to safely modify JSON
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
" "$config_file" || \
        warn "Could not auto-add superpowers. Add manually: \"superpowers@git+https://github.com/obra/superpowers.git\""
  fi
}

install_superpowers_claude() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN: claude plugin install superpowers@claude-plugins-official"
    return 0
  fi

  local out
  out="$(claude plugin list 2>/dev/null)" || true
  if echo "$out" | grep -qi superpowers; then
    ok "Superpowers already installed for Claude Code"
    return 0
  fi

  info "Installing superpowers for Claude Code..."
  if claude plugin install superpowers@claude-plugins-official 2>&1; then
    ok "Superpowers installed for Claude Code"
  else
    local rc=$?
    record_failure "Superpowers Claude install failed (exit ${rc}). Manually: claude plugin install superpowers@claude-plugins-official"
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
    return 0
  fi

  if command -v cargo >/dev/null 2>&1; then
    warn "RTK not installed. To avoid surprise compile time, install manually when needed: cargo install rtk --git ${RTK_REPO} --rev ${RTK_SHA}"
  else
    warn "RTK not installed and cargo not found. Install RTK manually if needed."
  fi
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

  local missing=0
  [[ -s "$SKILL_DIR/engineer-shovel/SKILL.md" ]] || missing=1

  local names=(branch feat fix plan refactor review brainstorm quick blueprint research statistic update)
  for name in "${names[@]}"; do
    [[ -s "$COMMAND_DIR/tool-${name}.md" ]] || missing=1
  done

  if [[ "$missing" -eq 0 && "$FAILURES" -eq 0 ]]; then
    ok "Verification passed"
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

  case "$MODE" in
    minimal)
      ;;
    recommended)
      _install_caveman_for_targets
      ;;
    full)
      install_ecc
      install_gsd
      install_superpowers
      _install_caveman_for_targets
      install_rtk
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
  info "Next: restart your agent session, then use skill(name=\"engineer-shovel\") or run /tool-* commands."
}

main "$@"
