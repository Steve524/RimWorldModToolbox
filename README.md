# RimWorld Mod Toolbox

A repeatable **AI agent team for RimWorld modding**. Open any mod folder in your AI coding harness, type `/rimworld-team <what you want>`, and a team of roles takes it from spec to tested build:

- a **Producer** that plans and runs the gates
- a **Librarian** that proves every Def field and C# member against your installed game
- **Builders** working in separate lanes
- independent **Reviewers**
- one **QA** that drives the live game
- **specialists** (design, writing, UI, art & audio, compatibility & saves, framework API, Multiplayer sync), pulled in automatically when the task needs them

It works for new mods and existing ones. It is built on three open-source MCP servers: [RimWorldForge](https://github.com/SenjuWoo/RimWorldForge) (Defs and validation), [DecompilerServer](https://github.com/pardeike/DecompilerServer) (the game's C#), and [GABS](https://github.com/pardeike/GABS) + [RimBridgeServer](https://github.com/pardeike/RimBridgeServer) (the live game).

```
/rimworld-team add a hotkey that opens and closes all doors
```

## Quick start

1. Install the prerequisites and the three MCP servers: [docs/install.md](docs/install.md).
2. Check everything: `python kit.py --doctor`
3. Add the kit to your mods: `python kit.py MyMod`, or `python kit.py --new MyNewMod` for a new one.
4. Open `<RimWorld>\Mods\MyMod` as the project in your harness, and run `/rimworld-team <task>`.

## What `kit.py` does

It puts the skills (`rimworld-team`, `rimworld-forge`) and the MCP server config into each mod folder, in the format every harness reads:

| Harness | Tested |
|---|---|
| T3 Code (recommended: per-role providers via `delegate_task`) | yes |
| Claude Code | yes |
| Codex | yes |
| OpenCode | yes |
| Antigravity | yes |
| Muse Code | yes |
| Cursor | config written, untested |

Nothing goes into your global harness config. The kit files are added to the mod's local git exclude, so they're never committed. See [docs/harness-setup.md](docs/harness-setup.md).

## How the team works

Nine gated steps: intake → triage → roster → recon → **your approval** → build → review rounds → live-game QA → **your sign-off**. Every fact cites a tool call. Review and QA run against the same file hashes, so nothing untested ships. Your mod list and saves are backed up and restored around every test. See [docs/how-it-works.md](docs/how-it-works.md).

Pick models per role in [`team/roster.yaml`](team/roster.yaml). It defaults to your main model.

## Layout

| Path | What |
|---|---|
| `kit.py` | Installs and refreshes the kit; `--doctor` checks your setup |
| `kit/` | Per-harness config templates |
| `team/` | The workflow: `SKILL.md`, `WORKFLOW.md`, `BRIEF.md`, `roster.yaml`, `roles/`, `snapshot.ps1` |
| `templates/` | A new-mod template, and an example `Mods\AGENTS.md` for your core mods |
| `docs/` | Install, how it works, harness setup, RimWorld findings, research, design history |
| `mcp/` | Where you install the MCP servers (not in git) |

## Requirements and limits

- Windows, Steam RimWorld 1.6. RimWorld 1.7 (the Waylith engine, on Steam's `unstable` branch) should work through `rw_doctor`, but RimBridgeServer needs a 1.7 build before in-game QA works there.
- Python 3.11+, Git, .NET 10 runtime, and .NET SDK for C# mods.
- Multiplayer is checked statically. Runtime MP tests need extra setup ([docs/rimworld-findings.md](docs/rimworld-findings.md)).
- Publishing: a Workshop upload ships the whole folder, so publish from a clean copy (`team\snapshot.ps1 -Mod <mod> -Copy <folder>`).

## License

MIT, see [LICENSE](LICENSE). The MCP servers and RimBridgeServer are separate projects under their own (MIT) licenses, and are not included here.
