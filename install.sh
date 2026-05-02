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

MODE="recommended"
ENV="standalone"
SKILL_DIR="$HOME/.agents/skills"
COMMAND_DIR="$HOME/.claude/commands"

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
USAGE
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --minimal) MODE="minimal" ;;
      --recommended) MODE="recommended" ;;
      --full) MODE="full" ;;
      -h|--help) usage; exit 0 ;;
      *) err "Unknown option: $1"; usage; exit 1 ;;
    esac
    shift
  done
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

  mkdir -p "$SKILL_DIR" "$COMMAND_DIR"
  ok "Mode: ${MODE}; environment: ${ENV}"
}

copy_or_download_file() {
  local local_path="$1"
  local remote_path="$2"
  local target_path="$3"

  if [[ -f "$local_path" ]]; then
    cp "$local_path" "$target_path"
  else
    curl -fsSL "${REPO_URL}/${remote_path}" -o "$target_path"
  fi
}

install_skill() {
  local target="$SKILL_DIR/engineer-shovel"
  mkdir -p "$target"
  copy_or_download_file "$(dirname "$0")/SKILL.md" "SKILL.md" "$target/SKILL.md"
  ok "Installed skill → ${target}/SKILL.md"
}

install_commands() {
  local src_dir="$(dirname "$0")/commands"
  local names=(feat fix plan refactor review brainstorm quick blueprint research statistic)
  local count=0

  mkdir -p "$COMMAND_DIR"
  for name in "${names[@]}"; do
    local target="$COMMAND_DIR/tool-${name}.md"
    if [[ -d "$src_dir" && -f "$src_dir/tool-${name}.md" ]]; then
      cp "$src_dir/tool-${name}.md" "$target"
    else
      curl -fsSL "${REPO_URL}/commands/tool-${name}.md" -o "$target"
    fi
    count=$((count + 1))
  done

  ok "Installed ${count} slash commands → ${COMMAND_DIR}/"
}

stage_caveman() {
  local plugin_dir="$HOME/.claude/plugins/marketplaces/caveman"

  if [[ -d "$HOME/.claude/plugins/cache/caveman/caveman" ]]; then
    ok "Caveman already installed"
    return 0
  fi

  if git clone --depth 1 --single-branch "$CAVEMAN_REPO" /tmp/engineer-shovel-caveman >/dev/null 2>&1; then
    mkdir -p "$plugin_dir"
    cp -r /tmp/engineer-shovel-caveman/. "$plugin_dir/"
    rm -rf /tmp/engineer-shovel-caveman
    ok "Staged Caveman plugin → ${plugin_dir}"
  else
    warn "Could not stage Caveman. Install manually: /plugin install caveman@caveman"
  fi
}

install_ecc() {
  if [[ -d "$HOME/.claude/plugins/cache/ecc/ecc" || -d "$HOME/.claude/ecc" ]]; then
    ok "ECC already installed"
    return 0
  fi

  if git clone --depth 1 --single-branch "$ECC_REPO" /tmp/engineer-shovel-ecc >/dev/null 2>&1; then
    if [[ -f /tmp/engineer-shovel-ecc/install.sh ]]; then
      bash /tmp/engineer-shovel-ecc/install.sh >/dev/null 2>&1 || warn "ECC installer returned non-zero; check manually"
    fi
    rm -rf /tmp/engineer-shovel-ecc
    ok "ECC install attempted"
  else
    warn "Could not clone ECC. Install manually: /plugin install ecc@ecc"
  fi
}

stage_superpowers() {
  local plugin_dir="$HOME/.claude/plugins/marketplaces/claude-plugins-official"

  if [[ -d "$HOME/.claude/plugins/cache/claude-plugins-official/superpowers" ]]; then
    ok "superpowers already installed"
    return 0
  fi

  if git clone --depth 1 --single-branch "$SUPERPOWERS_REPO" /tmp/engineer-shovel-superpowers >/dev/null 2>&1; then
    mkdir -p "$plugin_dir"
    cp -r /tmp/engineer-shovel-superpowers/. "$plugin_dir/"
    rm -rf /tmp/engineer-shovel-superpowers
    ok "Staged superpowers marketplace → ${plugin_dir}"
  else
    warn "Could not stage superpowers. Install manually: /plugin install superpowers@claude-plugins-official"
  fi
}

install_rtk() {
  if command -v rtk >/dev/null 2>&1; then
    ok "RTK already installed"
    return 0
  fi

  if command -v cargo >/dev/null 2>&1; then
    warn "RTK not installed. To avoid surprise compile time, install manually when needed: cargo install rtk --git ${RTK_REPO}"
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
    cat >> "$file" <<'EOF'

## engineer-shovel
- Load on demand with: `skill(name="engineer-shovel")`
- Prefer cost modes: `--fast`, `--standard`, `--deep`.
EOF
    ok "Added engineer-shovel hint → ${file}"
  fi
}

verify_install() {
  local missing=0
  [[ -f "$SKILL_DIR/engineer-shovel/SKILL.md" ]] || missing=1

  local names=(feat fix plan refactor review brainstorm quick blueprint research statistic)
  for name in "${names[@]}"; do
    [[ -f "$COMMAND_DIR/tool-${name}.md" ]] || missing=1
  done

  if [[ "$missing" -eq 0 ]]; then
    ok "Verification passed"
  else
    err "Verification failed: missing installed files"
    exit 1
  fi
}

main() {
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
