# Installation Modes

`install.sh` supports three modes so users do not need to install the entire ecosystem by default. Use `--dry-run` with any mode to preview target paths and pinned external sources without writing files.

## Minimal

Installs only Engineer Shovel skill and slash commands.

```bash
./install.sh --minimal
```

## Recommended

Installs Engineer Shovel plus Caveman when possible. This gives the best token-saving baseline without forcing the whole stack.

```bash
./install.sh --recommended
```

## Full

Installs the full toolchain: ECC/GSD, superpowers, Caveman, RTK, Engineer Shovel skill, and slash commands.

```bash
./install.sh --full
```

## Dry Run

Preview the selected mode without copying files, cloning repositories, or appending memory hints:

```bash
./install.sh --recommended --dry-run
```

Dry run output includes the detected environment, target directories, and pinned external sources that would be used.

## Supply Chain Notes

- External helper repositories are pinned to explicit commit SHAs in `install.sh`.
- Pinned clones are checked out in a temporary directory and verified with `git rev-parse HEAD` before files are staged or external installers are attempted.
- `--full` may still invoke upstream installer behavior for ECC after the pinned checkout is verified. Use `--dry-run` first when bootstrapping unfamiliar machines.
- If an optional dependency cannot be staged, the installer reports the specific failure and exits non-zero during final verification.

## Non-interactive Default

When no flag is provided, the installer uses `--recommended`. Use `--full` explicitly for complete bootstrap behavior.

## Compression Tools

- Caveman is recommended for most workflows and is staged by `--recommended` when possible.
- RTK is optional but recommended when available. It compresses Bash/tool outputs before they enter the LLM context; it does not compress model replies or prompts.
- The installer does not compile RTK by default in recommended mode because Rust builds can be slow. Use `--full`, then follow RTK's own setup instructions such as global hook initialization when appropriate.
- Use `--full` when you intentionally want every supporting tool installed or staged.
