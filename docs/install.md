# Installation Modes

`install.sh` supports interactive setup plus explicit non-interactive flags. In a terminal, running `./install.sh` asks whether to install for OpenCode, Claude Code, both, or auto-detection, then asks for the install mode. Use `--dry-run` with any mode to preview target paths and pinned external sources without writing files.

## Targets

Choose where the skill and slash commands are installed:

```bash
./install.sh --target opencode --recommended
./install.sh --target claude --recommended
./install.sh --target all --recommended
./install.sh --target auto --recommended
```

- `opencode` installs the skill to `~/.agents/skills/engineer-shovel/` and commands to `~/.config/opencode/commands/`.
- `claude` installs the skill to `~/.claude/skills/engineer-shovel/` and commands to `~/.claude/commands/`.
- `all` installs the core skill and commands to both targets.
- `auto` detects `opencode` first, then `claude`; if neither command exists yet, it defaults to OpenCode paths so fresh OpenCode machines do not accidentally receive Claude-only commands.

## Minimal

Installs only Engineer Shovel skill and slash commands.

```bash
./install.sh --target opencode --minimal
```

## Recommended

Installs Engineer Shovel plus Caveman when possible. This gives the best token-saving baseline without forcing the whole stack.

```bash
./install.sh --target opencode --recommended
```

## Full

Installs the full toolchain: ECC/GSD, superpowers, Caveman, RTK, Engineer Shovel skill, and slash commands.

```bash
./install.sh --target opencode --full
```

## Dry Run

Preview the selected mode without copying files, cloning repositories, or appending memory hints:

```bash
./install.sh --target all --recommended --dry-run
```

Dry run output includes the selected target directories and pinned external sources that would be used.

## Supply Chain Notes

- External helper repositories are pinned to explicit commit SHAs in `install.sh`.
- Pinned clones are checked out in a temporary directory and verified with `git rev-parse HEAD` before files are staged or external installers are attempted.
- `--full` may still invoke upstream installer behavior for ECC after the pinned checkout is verified. Use `--dry-run` first when bootstrapping unfamiliar machines.
- If an optional dependency cannot be staged, the installer reports the specific failure and exits non-zero during final verification.

## Non-interactive Default

When no flag is provided in a terminal, the installer prompts for target and mode. In non-interactive contexts, it uses `--target auto --recommended`. Use `--target opencode`, `--target claude`, or `--target all` explicitly for scripts and CI.

## Compression Tools

- Caveman is recommended for most workflows and is staged by `--recommended` when possible.
- RTK is optional but recommended when available. It compresses Bash/tool outputs before they enter the LLM context; it does not compress model replies or prompts.
- The installer does not compile RTK by default in recommended mode because Rust builds can be slow. Use `--full`, then follow RTK's own setup instructions such as global hook initialization when appropriate.
- Use `--full` when you intentionally want every supporting tool installed or staged.
