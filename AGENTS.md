# RimWorld Mod Toolbox

The source for the RimWorld tooling: the `/rimworld-team` workflow, and the **kit** that puts skills and MCP server config into each mod folder. Mods live in RimWorld's `Mods` folder (the path is in `local.json`, written by `kit.py`). If `<Mods>\AGENTS.md` exists, read it before mod work.

## What's here

| Path | What it is |
|---|---|
| `kit.py` | Installs the kit: `python kit.py <ModFolder>`, `--new <slug>`, `--refresh`, `--doctor` |
| `kit/` | Kit templates: per-harness MCP and settings files, with `{{TOOLBOX}}`-style placeholders |
| `team/` | The workflow. `team\SKILL.md` is the skill source. Start at `team\README.md` |
| `mcp/` | The installed MCP servers (not in git). The `rimworld-forge` skill source is `mcp\RimWorldForge\skills\rimworld-forge\SKILL.md` |
| `templates/` | New-mod template; example `Mods\AGENTS.md` |
| `docs/` | Install, how it works, harness setup, findings, research, design history |
| `backups/` | Moved-aside files. Never delete; move here (not in git) |

## Editing

- Change a skill, server or setting in its source (`team\SKILL.md`, `kit\`, the Forge skill), then run `python kit.py --refresh`. Never hand-edit the installed copies in mod folders or in this folder's `.claude\`, `.agents\`, `.codex\`, `.cursor\`, `.mcp.json` and `opencode.json`. Those are generated, and not in git.
- `team\` files use the names TOOLBOX, MODS, GAME and PLAYER instead of real paths. The installed `SKILL.md` gives the Producer the real ones.
- Keep it machine-neutral: no personal paths, names or mod lists in committed files.

## Never

- Put a folder in `Mods` that isn't a mod. RimWorld loads every top-level folder there as a mod, dot-folders included. Kit folders sit *inside* a mod folder, which is fine.
- Add these MCP servers or skills to a global harness config.
