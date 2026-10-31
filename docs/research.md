# Research

What we studied before building, and what we took from it. Six research agents (two providers) covered roles, specialists, prior art, MCP tools, orchestration and packaging. Their findings were then reviewed over several council rounds (see [design-history.md](design-history.md)).

## Prior art

| Source | What we took |
|---|---|
| [Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) | Named artifacts + a short return contract instead of chat dumps; "a skipped check that says nothing looks like a check that passed"; announce the active lineup |
| [OpenCode-Game-Studios](https://github.com/Cipher-85/OpenCode-Game-Studios) | Deny-by-default tool lists per role; strict reviewer independence (fresh context, no author conclusions in the packet) |
| [BMAD game dev](https://game-dev-studio-docs.bmad-method.org/reference/agents/) | Brief → spec → build → clean-context review chain; standing rules must live where every agent reads them |
| [agency-agents](https://github.com/msitarzewski/agency-agents) | Deliverable templates and measurable success criteria per role |
| [universal-modder](https://github.com/rehan-remade/universal-modder) | One game driver; cheapest route first (data → loader API → patches); backups before touching the game |
| [VoltAgent subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | "No message bus: coordinate through files and the orchestrator; one writer per file" |
| Anthropic, *Building effective agents* and *multi-agent research system* | Workflows over free agents; parallelize only independent work; pass file references, not text |
| t3dotgg/tstack `sol-loop` and `council` skills | Review loop with a budget and a findings ledger; multi-provider council review |

None of these had RimWorld-specific roles. The RimWorld knowledge (Defs, PatchOperations, `MayRequire`, save compatibility, Multiplayer sync) is written fresh here.

## Roles: 13 drafted, 7 specialists kept

The first draft had 13 specialists. They were merged where the work produced one artifact or ended at the same human gate:

| Kept | Absorbed |
|---|---|
| Designer | Systems designer, content designer, balance analyst, quest/event designer |
| Writer & Strings | Lore writer, localization (English strings) |
| Art & Audio | Art director, texture artist, technical artist, sound designer |
| Compat & Save | Compat/versioning engineer, save compatibility |
| UI/UX, Framework/API, MP sync | Unchanged |

Specialists come in **by trigger** (a concrete signal in the task or spec), not by category label. Categories (QoL, content, overhaul, visual/audio, framework) only hint at which triggers usually fire.

## Decisions worth knowing

- **The Producer is the main thread.** Delegates can't talk to you mid-task, and the ledger needs one writer.
- **No solo mode.** Every task runs the team. A shortcut mode was tried and removed: the point is a repeatable workflow.
- **Run files live in the toolbox, not the mod.** A Workshop upload ships the whole mod folder.
- **Builders edit the mod directly.** Forge's staging step deletes the target folder, so it's banned.
- **The review and QA gates are pinned to file hashes** of the candidate, so nothing untested ships.
- **Roster in YAML**, one line per role, with `inherit` by default. Model choice is yours, not the workflow's.

Details per finding: [rimworld-findings.md](rimworld-findings.md) and [harness-setup.md](harness-setup.md).
