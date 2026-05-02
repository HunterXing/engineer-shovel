#!/usr/bin/env bash
# engineer-shovel — token-aware installer

set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com"
REPO_OWNER="HunterXing"
REPO_NAME="engineer-shovel"
REPO_URL="${REPO_RAW}/${REPO_OWNER}/${REPO_NAME}/main"

ECC_REPO="https://github.com/affaan-m/everything-claude-code"
CAVEMAN_REPO="https://github.com/JuliusBrussee/caveman"
SUPERPOWERS_REPO="https://github.com/anthropics/claude-plugins-official.git"
RTK_REPO="https://github.com/rtk-ai/rtk"

ECC_SHA="841beea45cb25ba51f29fa45b7e272938d19b80a"
CAVEMAN_SHA="ef6050c5e1848b6880ff47c32ade1a608a64f85e"
SUPERPOWERS_SHA="b392f51899343f35a203260a4b344803de236d13"
RTK_SHA="4338f029ec43b69eb959748ec02cd7885200c264"

MODE="recommended"
ENV="standalone"
SKILL_DIR="$HOME/.agents/skills"
COMMAND_DIR="$HOME/.claude/commands"
PLUGIN_MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces"
PLUGIN_CACHE_DIR="$HOME/.claude/plugins/cache"
DRY_RUN=0
FAILURES=0
TMP_ROOT=""

info() { printf 'ℹ %s\n' "$1"; }
ok() { printf '✔ %s\n' "$1"; }
warn() { printf '⚠ %s\n' "$1"; }
err() { printf '✘ %s\n' "$1" >&2; }

usage() {
  cat <<'USAGE'
Usage: ./install.sh [--minimal|--recommended|--full]

Modes:
  --minimal      Install only engineer-shovel skill and slash commands.
  --recommended Install skill, commands, and Caveman plugin staging. Default.
  --full         Install/stage ECC, superpowers, Caveman, RTK, skill, commands.
  --dry-run      Print planned actions without writing files or cloning repos.
USAGE
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --minimal) MODE="minimal" ;;
      --recommended) MODE="recommended" ;;
      --full) MODE="full" ;;
      --dry-run) DRY_RUN=1 ;;
      -h|--help) usage; exit 0 ;;
      *) err "Unknown option: $1"; usage; exit 1 ;;
    esac
    shift
  done
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

  git clone --no-tags --filter=blob:none "$repo_url" "$target_dir" >/dev/null 2>&1
  git -C "$target_dir" checkout --detach "$commit_sha" >/dev/null 2>&1
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

detect_env() {
  if command -v opencode >/dev/null 2>&1; then
    ENV="opencode"
    SKILL_DIR="$HOME/.agents/skills"
    COMMAND_DIR="$HOME/.config/opencode/commands"
  elif command -v claude >/dev/null 2>&1; then
    ENV="claude-code"
    SKILL_DIR="$HOME/.claude/skills"
    COMMAND_DIR="$HOME/.claude/commands"
  fi

  run_or_print mkdir -p "$SKILL_DIR" "$COMMAND_DIR"
  ok "Mode: ${MODE}; environment: ${ENV}"
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
  local names=(feat fix plan refactor review brainstorm quick blueprint research statistic)
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

stage_caveman() {
  local plugin_dir="$PLUGIN_MARKETPLACE_DIR/caveman"

  if [[ -d "$PLUGIN_CACHE_DIR/caveman/caveman" ]]; then
    ok "Caveman already installed"
    return 0
  fi

  ensure_tmp_root
  local checkout_dir="$TMP_ROOT/caveman"
  if clone_pinned_repo "$CAVEMAN_REPO" "$CAVEMAN_SHA" "$checkout_dir"; then
    run_or_print mkdir -p "$plugin_dir"
    run_or_print cp -r "$checkout_dir/." "$plugin_dir/"
    ok "Staged Caveman plugin → ${plugin_dir}"
  else
    record_failure "Could not stage Caveman. Install manually: /plugin install caveman@caveman"
  fi
}

install_ecc() {
  if [[ -d "$PLUGIN_CACHE_DIR/ecc/ecc" || -d "$HOME/.claude/ecc" || -d "${OPENCODE_HOME:-$HOME/.config/opencode}/ecc" ]]; then
    ok "ECC already installed"
    return 0
  fi

  ensure_tmp_root
  local checkout_dir="$TMP_ROOT/ecc"
  if clone_pinned_repo "$ECC_REPO" "$ECC_SHA" "$checkout_dir"; then
    if [[ -f "$checkout_dir/install.sh" ]]; then
      if [[ "$DRY_RUN" -eq 1 ]]; then
        info "DRY-RUN: bash ${checkout_dir}/install.sh"
      elif ! bash "$checkout_dir/install.sh"; then
        record_failure "ECC installer returned non-zero; check manually"
      fi
    fi
    ok "ECC install attempted"
  else
    record_failure "Could not clone pinned ECC source. Install manually: /plugin install ecc@ecc"
  fi
}

stage_superpowers() {
  local plugin_dir="$PLUGIN_MARKETPLACE_DIR/claude-plugins-official"

  if [[ -d "$PLUGIN_CACHE_DIR/claude-plugins-official/superpowers" ]]; then
    ok "superpowers already installed"
    return 0
  fi

  ensure_tmp_root
  local checkout_dir="$TMP_ROOT/superpowers"
  if clone_pinned_repo "$SUPERPOWERS_REPO" "$SUPERPOWERS_SHA" "$checkout_dir"; then
    run_or_print mkdir -p "$plugin_dir"
    run_or_print cp -r "$checkout_dir/." "$plugin_dir/"
    ok "Staged superpowers marketplace → ${plugin_dir}"
  else
    record_failure "Could not stage pinned superpowers source. Install manually: /plugin install superpowers@claude-plugins-official"
  fi
}

install_rtk() {
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
  if [[ "$ENV" == "opencode" && -f "$HOME/.config/opencode/AGENTS.md" ]]; then
    file="$HOME/.config/opencode/AGENTS.md"
  elif [[ "$ENV" == "claude-code" && -f "$HOME/.claude/CLAUDE.md" ]]; then
    file="$HOME/.claude/CLAUDE.md"
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

  local names=(feat fix plan refactor review brainstorm quick blueprint research statistic)
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

main() {
  trap cleanup_tmp EXIT
  parse_args "$@"
  check_prereqs
  detect_env

  case "$MODE" in
    minimal)
      install_skill
      install_commands
      ;;
    recommended)
      stage_caveman
      install_skill
      install_commands
      ;;
    full)
      install_ecc
      stage_superpowers
      stage_caveman
      install_rtk
      install_skill
      install_commands
      configure_memory_hint
      ;;
  esac

  verify_install
  info "Done. Use skill(name=\"engineer-shovel\") or run /tool-* commands."
}

main "$@"
