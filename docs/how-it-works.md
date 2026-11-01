# How the team works

`/rimworld-team <task>` starts the **Producer** (the main thread). It runs a fixed, repeatable sequence of gates and delegates every role with a self-contained brief. The full procedure is `team\WORKFLOW.md`; this is the overview.

## The flow

| # | Step | Who | Gate |
|---|---|---|---|
| 1 | Intake: read `AGENTS.md` files, `rw_doctor`, rebuild the Def index, baseline the mod | Producer | Goal, version, baseline recorded |
| 2 | Triage: task type, category hint, specialists by trigger | Producer | Each pick has a reason |
| 3 | Resolve the roster (`team\roster.yaml`) against the harness's models | Producer | Every role has a model, or stop |
| 4 | Recon: facts with tool evidence, specialist drafts. Bug fix: QA builds a failing repro first | Librarian, specialists, QA | `refs.md` all proven / repro is red |
| 5 | Spec, approved by you | Producer + you | **Your yes** |
| 6 | Build in disjoint lanes, then validate and hash the candidate | Builders | Compiles, validates, `hashes.txt` |
| 7 | Review rounds: fresh independent reviewers, findings ledger, fix loop | Reviewer(s) | Every reviewer approves this exact candidate |
| 8 | QA in the live game, against the same hashes, then restore your player data | QA (the only game driver) | Test steps pass with evidence |
| 9 | Taste and feel sign-off when art or UI changed; report | You | **Your yes** |

## Roles

**Core (every task):** Producer (main thread), Librarian, Builder, Reviewer, QA.

**Specialists (pulled in by trigger, never by hand):**

| Specialist | Trigger |
|---|---|
| Systems & Balance | A new or changed system or mechanic; any numbers (balance-checked against vanilla) |
| Content & Quest | New items, animals, factions, research; incidents, quests, events |
| Writer & Strings | Player-visible text |
| UI/UX | Gizmos, windows, settings, hotkeys |
| Art | Textures, `graphicData`, icons |
| Sound | `SoundDef`, `SongDef`, sound files |
| Compat & Save | PatchOperations, dependencies, renames, `ExposeData`, ports |
| Framework/API | Other mods consume this one |
| MP sync | C# that changes game state, when Multiplayer matters |

Each role file lists its owned files, the exact MCP tools it may call, the skills it uses, its steps, and its reply format.

## Rules that make it repeatable

- **One writer per file.** Builders get disjoint globs. At most one C# lane.
- **One game driver.** Only QA touches the live game.
- **Evidence, not claims.** Every fact cites a tool call. Every gate links its evidence.
- **Independent review.** Fresh reviewer each round, never the builder.
- **Frozen candidate.** Review and QA test the same file hashes. Any change after review goes back to review.
- **Your data is safe.** Player-data writes need your consent, and QA restores your mod list and saves afterwards. Nothing is deleted: old files move to `backups\`.

## Files

| Path | What |
|---|---|
| `team\SKILL.md` | Skill source (rendered into each mod by `kit.py`) |
| `team\WORKFLOW.md` | The Producer's procedure |
| `team\BRIEF.md` | The brief every delegate gets |
| `team\roster.yaml` | Who runs each role |
| `team\roles\` | One file per role |
| `team\snapshot.ps1` | Baseline copy, hashes, change check, flat Forge workspace |
| `team\runs\` | One folder per task (spec, ledger, baselines, delegate scratch) |
