# rimworld-team

A repeatable mod team. Every task runs the same gated workflow: core roles always, plus the specialists the task triggers.

**How to call it:** open a mod folder (e.g. `<RimWorld>\Mods\MyMod`) as the project in your harness, then type `/rimworld-team <task>`.

- **Mod without the kit yet:** run `python <toolbox>\kit.py <ModFolder>` once.
- **New mod:** run `python <toolbox>\kit.py --new <slug>`, open `Mods\<slug>`, then describe the mod to `/rimworld-team`.
- **Skill source:** `team\SKILL.md`. The copies in each mod's `.claude\skills` and `.agents\skills` come from `kit.py`.

You never pick roles. The Producer sorts the task and pulls in each specialist when the task triggers it. The trigger table is in `WORKFLOW.md`.

| File | What it is |
|---|---|
| `SKILL.md` | Skill source. `kit.py` fills in the machine's paths |
| `WORKFLOW.md` | The steps the main thread (Producer) follows: triage, gates, review loop |
| `BRIEF.md` | The text every delegate gets |
| `roster.yaml` | **Edit this.** One line per role: provider, model, effort, instances |
| `roles\core\` | Producer, Librarian, Builder, Reviewer, QA. Always on |
| `roles\specialists\` | Designer, Writer, UI/UX, Art & Audio, Compat & Save, Framework/API, MP sync. Pulled in by trigger |
| `snapshot.ps1` | Baseline copy, hashes, change check, flat Forge workspace for `rw_validate` |
| `runs\` | One folder per task: spec, ledger, baseline, delegate scratch. Kept outside the mod, so nothing leaks to the Workshop |

Your gates: approve the spec, sign off on taste (art/audio) and feel (UI), and decide when to publish.

More: [../docs/how-it-works.md](../docs/how-it-works.md).

## Known issues

1. RimWorld 1.7 (Waylith engine) is on Steam's `unstable` branch. Roles trust `rw_doctor` for the installed version. On 1.7, in-game QA needs a RimBridgeServer 1.7 build.
2. RimWorldForge and its skill default to 1.6. Set versions explicitly.
3. Cursor's project MCP file is written but untested.
4. Runtime Multiplayer tests need the RimBridgeServer MP companion and a second GABS profile. Without them, MP checks are static.
5. A Workshop upload ships the whole mod folder, kit included. Publish from a clean copy (`snapshot.ps1 -Copy`).
6. The first `opencode mcp list` in a new folder may print nothing. Run it again.
