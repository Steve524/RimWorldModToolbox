# Harness setup: project-only skills and MCP servers

Everything here is wired **per project folder**, never in a global harness config, apart from the per-folder trust entries below. `kit.py` writes it into each mod folder. These are the findings that shaped it, all tested on Windows in October 2026.

## Where each harness looks

| Harness | Project MCP servers | Project skills | Needs the folder trusted? |
|---|---|---|---|
| Claude Code | `.mcp.json` (+ approval in `.claude\settings.json`) | `.claude\skills\` | Yes: its trust dialog, once per folder (T3 Code accepts it when you open the project) |
| Codex | `.codex\config.toml` (`[mcp_servers.*]`) | `.agents\skills\` | Yes: `[projects."<path, lowercased>"] trust_level = "trusted"` in `~/.codex/config.toml` |
| Cursor | `.cursor\mcp.json` | `.agents\skills\`, `.cursor\skills\` | Cursor asks in its UI |
| OpenCode | `opencode.json` (v2: servers under `mcp.servers`) | `.agents\skills\`, `.claude\skills\`, `.opencode\skills\` | No |
| Antigravity | `.agents\mcp_config.json` (`mcpServers`, same shape as Claude) | `.agents\skills\` | Yes: `trustedWorkspaces` in `~/.gemini/antigravity-cli/settings.json` |
| Muse Code | `.mcp.json` | `.agents\skills\`, `.claude\skills\`, `.codex\skills\` | Yes: `~/.config/muse/trust.json` |

`kit.py` writes all of these, and the trust entries too (skip with `--no-trust`). It backs up each global file before its first edit. Each skill goes into both `.claude\skills` and `.agents\skills`; Muse and OpenCode read both and report the second copy as shadowed. That's harmless.

## Gotchas found while testing

- **Trust does not inherit.** Trusting `C:\Users\you` did not make a folder under it trusted in Codex, Muse or the Antigravity CLI. Each project folder needs its own entry.
- **Discovery stops at the git root.** Codex, OpenCode and Antigravity look for project config from the working folder up to the repository root. Each mod is usually its own git repo, so the config has to be in the mod folder itself, not in a parent.
- **Claude Code ignores MCP approval in the shared `.claude\settings.json` until the folder's trust dialog has been accepted.** `claude -p` (headless) skips the dialog. In T3 Code, opening the folder as a project accepts it.
- **Muse starts MCP servers with a stripped environment.** Without `USERPROFILE`/`HOME`, RimWorldForge failed with "Could not determine home directory" and GABS did not start. The JSON configs pass an `env` block. Codex and OpenCode pass the full environment, so their files don't need one.
- **OpenCode v2 wants `mcp.servers`.** The v1 shape (`mcp.<name>`) loads into config but `opencode mcp list` reports no servers. The first `opencode mcp list` in a new folder can also print nothing; run it again.
- **`agy mcp list` shows only global servers.** Antigravity still loads `.agents\mcp_config.json` in a session. In headless `agy -p`, MCP calls need a permission rule or `--dangerously-skip-permissions`.
- **Muse prefers `AGENTS.md` over `CLAUDE.md`** in the same folder and warns about the other one. Keep `CLAUDE.md` as a one-line `@AGENTS.md`.
- **T3 Code delegates run in the parent thread's project folder.** `delegate_task` rejects a different `projectId` for local tasks. So the team must be started from the mod folder (or the toolbox) for every delegate to get the MCPs.

## How to check a harness

Run these from inside a mod folder that has the kit:

| Harness | Command | Expect |
|---|---|---|
| Codex | `codex mcp list` | `rimworldforge`, `decompiler`, `gabs` enabled |
| OpenCode | `opencode mcp list` | all three `connected` |
| Claude Code | `claude mcp list`, or `claude -p "call rw_doctor"` | servers listed / a version |
| Muse | `muse skills list`; `muse exec "call rw_doctor"` | `rimworld-team`, `rimworld-forge` as `project`; a version |
| Antigravity | `agy -p "call rw_doctor"` | a version (headless needs MCP permission) |

Outside a kit folder, none of them should list the RimWorld servers or skills.

## Why not global, and why not in `Mods`

- Global configs would load the RimWorld servers in every project.
- RimWorld treats **every top-level folder in `Mods`** as a mod, dot-folders included (`Verse.ModLister.RebuildModList` scans `Mods` with `GetDirectories()`). So `Mods\.claude` would show up as a broken mod.
- Folders *inside* a mod folder are fine: they are not load folders and hold no XML RimWorld reads.
