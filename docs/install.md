# Installation Modes

`install.sh` supports three modes so users do not need to install the entire ecosystem by default.

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

## Non-interactive Default

When no flag is provided, the installer uses `--recommended`. Use `--full` explicitly for complete bootstrap behavior.

## Compression Tools

- Caveman is recommended for most workflows and is staged by `--recommended` when possible.
- RTK is optional but recommended when available. It compresses Bash/tool outputs before they enter the LLM context; it does not compress model replies or prompts.
- The installer does not compile RTK by default in recommended mode because Rust builds can be slow. Use `--full`, then follow RTK's own setup instructions such as global hook initialization when appropriate.
- Use `--full` when you intentionally want every supporting tool installed or staged.
