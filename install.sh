#!/usr/bin/env bash
# ============================================================================
# optimal-workflow — One-command bootstrap installer
# ============================================================================
# Installs the full development toolchain for OpenCode / Claude Code:
#   ECC + GSD + superpowers + Caveman + RTK + optimal-workflow skill
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/<user>/optimal-workflow/main/install.sh | bash
#   # or after cloning:
#   ./install.sh
# ============================================================================

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()  { echo -e "${CYAN}ℹ${NC} $1"; }
ok()    { echo -e "${GREEN}✔${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
err()   { echo -e "${RED}✘${NC} $1"; }
header(){ echo -e "\n${BOLD}${BLUE}═══ $1 ═══${NC}\n"; }

# ── Config ───────────────────────────────────────────────────────────────────
REPO_RAW="https://raw.githubusercontent.com"
REPO_OWNER="HunterXing"
REPO_NAME="engineer-shovel"
REPO_URL="${REPO_RAW}/${REPO_OWNER}/${REPO_NAME}/main"

ECC_REPO="https://github.com/affaan-m/everything-claude-code"
CAVEMAN_REPO="https://github.com/JuliusBrussee/caveman"
RTK_REPO="https://github.com/rtk-ai/rtk"
SUPERPOWERS_MARKETPLACE="claude-plugins-official"

# ── Step 0: Prerequisites ───────────────────────────────────────────────────
check_prereqs() {
  header "Checking Prerequisites"

  local missing=()
  for cmd in git curl; do
    if ! command -v "$cmd" &>/dev/null; then
      missing+=("$cmd")
    fi
  done

  if [[ ${#missing[@]} -gt 0 ]]; then
    err "Missing required tools: ${missing[*]}"
    echo "  Install them first:"
    echo "    apt install -y git curl    # Debian/Ubuntu"
    echo "    brew install git curl      # macOS"
    exit 1
  fi
  ok "git and curl are installed"

  # Check for Rust (needed for RTK)
  if command -v cargo &>/dev/null; then
    HAS_CARGO=true
    ok "cargo is installed (can build RTK from source)"
  else
    HAS_CARGO=false
    warn "cargo not found — RTK will need manual installation (see docs)"
  fi
}

# ── Step 1: Detect environment ──────────────────────────────────────────────
detect_env() {
  header "Detecting Environment"

  if command -v opencode &>/dev/null; then
    ENV="opencode"
    CONFIG_DIR="$HOME/.config/opencode"
    SKILL_DIR="$HOME/.agents/skills"
    ok "Detected: OpenCode (OhMyOpenCode)"
  elif command -v claude &>/dev/null; then
    ENV="claude-code"
    CONFIG_DIR="$HOME/.claude"
    SKILL_DIR="$HOME/.claude/skills"
    ok "Detected: Claude Code"
  else
    ENV="standalone"
    SKILL_DIR="$HOME/.agents/skills"
    warn "No AI coding tool detected — installing skill files only"
    warn "Install Claude Code or OpenCode first, then re-run this script"
  fi

  mkdir -p "$SKILL_DIR"
}

# ── Step 2: Install ECC (Everything Claude Code) ────────────────────────────
install_ecc() {
  header "Installing ECC (Everything Claude Code)"

  if [[ -d "$HOME/.claude/plugins/cache/ecc/ecc" ]]; then
    ok "ECC is already installed"
    return 0
  fi

  info "Cloning ECC from ${ECC_REPO}..."
  git clone --depth 1 "$ECC_REPO" /tmp/everything-claude-code 2>/dev/null || {
    warn "Could not clone ECC. You can install it manually later:"
    echo "  /plugin install ecc@ecc"
    return 0
  }

  # Install via the ECC installer
  if [[ -f /tmp/everything-claude-code/install.sh ]]; then
    bash /tmp/everything-claude-code/install.sh 2>/dev/null && ok "ECC installed" || warn "ECC installation skipped"
  else
    # Manual install: copy skills and rules
    mkdir -p "$HOME/.claude/skills" "$HOME/.claude/rules" "$HOME/.claude/agents"
    cp -r /tmp/everything-claude-code/.agents/skills/* "$HOME/.claude/skills/" 2>/dev/null || true
    ok "ECC skills copied"
  fi

  rm -rf /tmp/everything-claude-code
}

# ── Step 3: Install superpowers plugin ──────────────────────────────────────
install_superpowers() {
  header "Installing superpowers plugin"

  if [[ -d "$HOME/.claude/plugins/cache/claude-plugins-official/superpowers" ]]; then
    ok "superpowers is already installed"
    return 0
  fi

  # Try plugin install via Claude Code
  if command -v claude &>/dev/null; then
    info "Installing via /plugin install..."
    claude /plugin install "superpowers@${SUPERPOWERS_MARKETPLACE}" 2>/dev/null && {
      ok "superpowers plugin installed"
      return 0
    }
  fi

  # Fallback: clone marketplace and install manually
  info "Cloning official plugins marketplace..."
  MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces/${SUPERPOWERS_MARKETPLACE}"
  git clone --depth 1 "https://github.com/anthropics/claude-plugins-official.git" \
    /tmp/claude-plugins-official 2>/dev/null || {
    warn "Could not clone plugin marketplace. Install manually:"
    echo "  /plugin install superpowers@claude-plugins-official"
    return 0
  }

  mkdir -p "$MARKETPLACE_DIR"
  cp -r /tmp/claude-plugins-official/* "$MARKETPLACE_DIR/" 2>/dev/null || true
  rm -rf /tmp/claude-plugins-official
  ok "superpowers plugin files staged (may need Claude Code restart)"
}

# ── Step 4: Install Caveman plugin ──────────────────────────────────────────
install_caveman() {
  header "Installing Caveman plugin"

  if [[ -d "$HOME/.claude/plugins/cache/caveman/caveman" ]]; then
    ok "Caveman is already installed"
    return 0
  fi

  git clone --depth 1 "$CAVEMAN_REPO" /tmp/caveman 2>/dev/null || {
    warn "Could not clone Caveman repo. Install manually:"
    echo "  /plugin install caveman@caveman"
    return 0
  }

  MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces/caveman"
  mkdir -p "$MARKETPLACE_DIR"
  cp -r /tmp/caveman/* "$MARKETPLACE_DIR/" 2>/dev/null || true

  # Register the marketplace if not already registered
  local known="$HOME/.claude/plugins/known_marketplaces.json"
  if [[ -f "$known" ]]; then
    python3 -c "
import json
with open('$known') as f: d = json.load(f)
if 'caveman' not in d:
    d['caveman'] = {'source': {'source': 'github', 'repo': 'JuliusBrussee/caveman'}, 'installLocation': '$MARKETPLACE_DIR'}
    with open('$known', 'w') as f: json.dump(d, f, indent=2)
" 2>/dev/null || true
  fi

  rm -rf /tmp/caveman
  ok "Caveman plugin staged (run '/plugin install caveman@caveman' in Claude Code to activate)"
}

# ── Step 5: Install RTK (Rust Token Killer) ─────────────────────────────────
install_rtk() {
  header "Installing RTK (Rust Token Killer)"

  if command -v rtk &>/dev/null; then
    ok "RTK $(rtk --version 2>/dev/null || echo '')is already installed"
    return 0
  fi

  if [[ "$HAS_CARGO" == true ]]; then
    info "Building RTK from source (this may take a few minutes)..."
    cargo install rtk --git "$RTK_REPO" 2>/dev/null && {
      ok "RTK installed via cargo"
      # Add ~/.cargo/bin to PATH if not already
      if [[ ":$PATH:" != *":$HOME/.cargo/bin:"* ]]; then
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$HOME/.bashrc"
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
        warn "Added ~/.cargo/bin to PATH in .bashrc/.zshrc (restart shell or run: export PATH=\"\$HOME/.cargo/bin:\$PATH\")"
      fi
      return 0
    }
    warn "Cargo build failed"
  fi

  warn "RTK requires manual installation:"
  echo "  1. With cargo: cargo install rtk --git ${RTK_REPO}"
  echo "  2. Or download a binary from: ${RTK_REPO}/releases"
}

# ── Step 6: Install optimal-workflow skill ──────────────────────────────────
install_skill() {
  header "Installing optimal-workflow Skill"

  local target="$SKILL_DIR/optimal-workflow"
  mkdir -p "$target"

  # Try to get SKILL.md from local repo first, then from GitHub
  if [[ -f "$(dirname "$0")/SKILL.md" ]]; then
    cp "$(dirname "$0")/SKILL.md" "$target/SKILL.md"
    info "Installed from local repo"
  elif curl -fsSL "${REPO_URL}/SKILL.md" -o "$target/SKILL.md" 2>/dev/null; then
    info "Downloaded from GitHub"
  else
    err "Could not find SKILL.md. Clone the repo manually:"
    echo "  git clone https://github.com/${REPO_OWNER}/${REPO_NAME}.git"
    echo "  cd ${REPO_NAME} && ./install.sh"
    exit 1
  fi

  ok "optimal-workflow skill installed → ${target}/SKILL.md"
}

# ── Step 7: Configure AGENTS.md (OpenCode only) ─────────────────────────────
configure_agents() {
  header "Configuring AGENTS.md"

  local agents_file
  if [[ "$ENV" == "opencode" && -f "$HOME/.config/opencode/AGENTS.md" ]]; then
    agents_file="$HOME/.config/opencode/AGENTS.md"
  elif [[ "$ENV" == "claude-code" && -f "$HOME/.claude/AGENTS.md" ]]; then
    agents_file="$HOME/.claude/AGENTS.md"
  else
    # Download default AGENTS.md from repo
    if [[ "$ENV" == "opencode" ]]; then
      agents_file="$HOME/.config/opencode/AGENTS.md"
      mkdir -p "$HOME/.config/opencode"
    elif [[ "$ENV" == "claude-code" ]]; then
      agents_file="$HOME/.claude/AGENTS.md"
    else
      return 0
    fi
    curl -fsSL "${REPO_URL}/AGENTS.md" -o "$agents_file" 2>/dev/null || return 0
  fi

  # Add optimal-workflow reference if not already present
  if [[ -f "$agents_file" ]] && ! grep -q "optimal-workflow" "$agents_file" 2>/dev/null; then
    cat >> "$agents_file" << 'EOF'

## optimal-workflow
- Load with: `skill(name="optimal-workflow")`
- Covers: New Feature, Bug Fix, Brainstorming, Refactoring, Code Review, Quick Tasks, Complex Projects, Deep Research
EOF
    ok "AGENTS.md updated with optimal-workflow reference"
  else
    ok "AGENTS.md already references optimal-workflow"
  fi
}

# ── Step 8: Verify installation ─────────────────────────────────────────────
verify() {
  header "Verification Report"
  local all_ok=true

  echo ""
  echo -e "${BOLD}Component                Status${NC}"
  echo "──────────────────────────────────────────"

  # ECC
  if ls "$HOME/.claude/plugins/cache/ecc/"* 1>/dev/null 2>&1 || [[ -d "$HOME/.claude/ecc" ]]; then
    echo -e "  ECC                     ${GREEN}installed${NC}"
  else
    echo -e "  ECC                     ${YELLOW}not detected (run: /plugin install ecc@ecc)${NC}"; all_ok=false
  fi

  # GSD
  if command -v gsd &>/dev/null || [[ -f "$HOME/.claude/get-shit-done/gsd.sh" ]]; then
    echo -e "  GSD                     ${GREEN}installed${NC}"
  else
    echo -e "  GSD                     ${YELLOW}part of ECC — install ECC first${NC}"; all_ok=false
  fi

  # superpowers
  if ls "$HOME/.claude/plugins/cache/claude-plugins-official/superpowers/"* 1>/dev/null 2>&1; then
    echo -e "  superpowers             ${GREEN}installed${NC}"
  else
    echo -e "  superpowers             ${YELLOW}not detected (run: /plugin install superpowers@claude-plugins-official)${NC}"; all_ok=false
  fi

  # Caveman
  if ls "$HOME/.claude/plugins/cache/caveman/"* 1>/dev/null 2>&1; then
    echo -e "  Caveman                 ${GREEN}installed${NC}"
  else
    echo -e "  Caveman                 ${YELLOW}not detected (run: /plugin install caveman@caveman)${NC}"; all_ok=false
  fi

  # RTK
  if command -v rtk &>/dev/null; then
    echo -e "  RTK                     ${GREEN}installed ($(rtk --version 2>/dev/null))${NC}"
  else
    echo -e "  RTK                     ${YELLOW}not detected (run: cargo install rtk --git ${RTK_REPO})${NC}"; all_ok=false
  fi

  # optimal-workflow skill
  if [[ -f "$SKILL_DIR/optimal-workflow/SKILL.md" ]]; then
    local lines=$(wc -l < "$SKILL_DIR/optimal-workflow/SKILL.md")
    echo -e "  optimal-workflow skill  ${GREEN}installed (${lines} lines)${NC}"
  else
    echo -e "  optimal-workflow skill  ${RED}NOT FOUND — install failed${NC}"; all_ok=false
  fi

  echo "──────────────────────────────────────────"

  if [[ "$all_ok" == true ]]; then
    echo -e "\n${GREEN}${BOLD}✅ All components installed successfully!${NC}"
  else
    echo -e "\n${YELLOW}${BOLD}⚠️  Some components need manual steps (see above)${NC}"
  fi
}

# ── Summary ──────────────────────────────────────────────────────────────────
print_summary() {
  header "🎯 Setup Complete!"

  echo -e "${BOLD}To start using the optimal-workflow:${NC}"
  echo ""
  echo "  1. In OpenCode or Claude Code, load the skill:"
  echo "     skill(name=\"optimal-workflow\")"
  echo ""
  echo "  2. Then choose your workflow:"
  echo "     /plan → /prp-implement    # New feature"
  echo "     /gsd-debug                # Bug fixing"
  echo "     /refactor → /review-work  # Refactoring"
  echo "     /gsd-fast                 # Quick tasks"
  echo "     /gsd-explore              # Brainstorming"
  echo ""
  echo -e "${BOLD}Token-saving tips:${NC}"
  echo "     /caveman full        # Compress communication (~75% savings)"
  echo "     /caveman-stats       # Check real token usage"
  echo "     /strategic-compact   # Compact context mid-session"
  echo ""
  echo -e "${BOLD}📖 Full documentation:${NC}"
  echo "     https://github.com/${REPO_OWNER}/${REPO_NAME}"
  echo ""
  echo -e "${BOLD}Happy coding! 🚀${NC}"
}

# ── Main ─────────────────────────────────────────────────────────────────────
main() {
  echo ""
  echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}${BLUE}║   optimal-workflow — Full Toolchain Installer    ║${NC}"
  echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════╝${NC}"
  echo ""
  echo "This script will install: ECC, GSD, superpowers, Caveman, RTK,"
  echo "and the optimal-workflow skill for your AI coding environment."
  echo ""

  check_prereqs
  detect_env
  install_ecc
  install_superpowers
  install_caveman
  install_rtk
  install_skill
  configure_agents
  verify
  print_summary
}

main "$@"
