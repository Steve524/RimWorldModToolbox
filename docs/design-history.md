# Design history

How this toolbox got its shape: research, then council review rounds (three models from three providers reviewing each version). Written during the build; paths and names are generalized. Current behavior lives in `team\WORKFLOW.md`, the role files and `kit.py`; when this file disagrees, they win.

# Plan: `rimworld-team` — repeatable agentic roles workflow for RimWorld mods

Status: design record, not instructions. **Current packaging is in "Round 6 change set" at the bottom** (project-only in the toolbox). Earlier sections mention the author's global skills repo stub and global MCP gaps; those are superseded. v3 went to council round 3. The round-3 fixes went straight into the built files (see "Round 3" at the bottom). If this file and WORKFLOW.md or a role file disagree, the WORKFLOW.md or role file wins.

## Goal

the author types `/rimworld-team <task>` in any harness (mainly T3 Code). The main thread (Producer) triages the task, picks roles by trigger, delegates each role with a self-contained brief, runs gates, and reports. Roles live in separate files. A separate roster file sets provider / model / effort / instances per role.

Out of scope: picking models (roster ships as `inherit`), fixing RimWorldForge's 1.6 hardcodes, fixing the mod template's 1.6 strings, MP runtime test rig, worktree isolation, multi-provider reviewer panels.

## Facts the design rests on (verified)

1. Installed game is **1.6.4871** (`Version.txt`, `rw_doctor`). Target is 1.7 per the author (Steam `unstable`); installed is 1.6. Role files never hardcode a version.
2. RimWorld scans only **top-level** folders of `Mods`. Workshop upload ships the **whole mod folder**.
3. the skills repo's sync script **copies** skill folders. A machine-only skills folder installs only on this machine.
4. Forge: `rw_index` writes one shared JSON non-atomically. `rw_validate` writes `reports/validation.json`, scans only flat Forge workspaces. `rw_project_new` with no `workspace` writes into the current folder. CLI `stage` `rmtree`s `Mods/<name>`. `rw_build` writes only inside its workspace. No Def index exists yet.
5. Decompiler: one process per harness/delegate; contexts not shared.
6. GABS: one game, one profile, ownership lease. Some bridge tools persist `ModsConfig.xml` / settings. A running game locks mod DLLs.
7. MP runtime test impossible today.
8. `blast-radius` is user-invoked: read and follow by path. Its proof step writes and runs a script.
9. T3 delegates get only the `task` text. Other providers may lack the RimWorld MCPs.
10. Most mod folders have no own `AGENTS.md` (a few).

## Layout

```
RimWorldModToolbox/team/
  README.md          ~10 lines for the author
  WORKFLOW.md        Producer's steps, triage, modes, spec + ledger shapes
  BRIEF.md           delegate brief template + hard rules
  roster.yaml        provider / model / effort / instances per role
  roles/core/        producer.md librarian.md builder.md reviewer.md qa.md
  roles/specialists/ designer.md writer.md ui-ux.md art-audio.md
                     compat-save.md framework-api.md mp-sync.md
  runs/<ModFolder>/<yyyymmdd-slug>/
    spec.md refs.md ledger.md hashes.txt     Producer writes
    base/                                     Producer: copy of the mod at intake (+ ModsConfig.xml copy)
    <role>-<i>/                               each child's own scratch: replies, forge/ workspace, proof/, screenshots, logs

(author's skills repo) rimworld-team/SKILL.md   stub, user-invoked → WORKFLOW.md
```

**One write rule for everyone:** a child writes only (a) its own `runs/…/<role>-<i>/` folder and (b) the mod globs its brief assigns. The Producer writes everything else in `runs/`. Inside `Mods`, nobody writes outside the mod folder named in the brief.

## The skill

`rimworld-team`, `disable-model-invocation: true`, one human-facing description line. Stub: "Read and follow `C:\...\team\WORKFLOW.md` with the task text."

## Roles

### Core 5

| Role | Runs as | Owns | Gate |
|---|---|---|---|
| **Producer** | The main thread. Never delegated | Intake, baseline, `rw_index`, triage, spec, lanes, ledger, hashes, human gates, report. Never writes mod code in team mode | Scope + Done |
| **Librarian** | Delegate, edits no mod files | Facts for `refs.md`: every Def field, parent, class, Harmony target, texture path → tool evidence | Reference: every claim resolved by `rw_def_inspect` / decompiler / raw `Data/` XML, version stamped |
| **Builder** | Delegate, one per lane, edits the mod folder directly in its lane's globs | XML lanes run in parallel. **At most one C# lane**: owns `Source/**`, `*.csproj`, `Assemblies/**`. Lane 1 owns `About/**`, `LoadFolders.xml`. Adds tagged debug logs when QA asks | Build: compiles; highest evidence tier stated |
| **Reviewer** | Delegate, fresh each round, read-only on the mod | Findings `S1 [blocker|should|nit] file:line` on `diff base/ ↔ mod`. Always checks MP determinism, `Scribe`/save, hardcoded strings, core-mod compat, least-powerful surface. Runs `blast-radius` when triggered; proof scripts in its own scratch | Diff: APPROVE, no blocker/should open |
| **QA / Game operator** | Delegate, **instances locked to 1** | Only role that drives `gabs`. Sets the test mod list (core mods + frameworks from `Mods/AGENTS.md` + this mod), restores `ModsConfig.xml` after. Test script, Player.log, old-save, removal, perf, screenshots. Owns `diagnosing-bugs` | Test: run against the recorded hashes, 0 new red errors, every spec test step has evidence |

### Specialists (7)

Designer (systems, content, balance, quest/event) · Writer & Strings (lore, English `Keyed`/`DefInjected`) · UI/UX (gizmos, windows, settings, hotkeys) · Art & Audio (direction, textures, `graphicData`, sounds; human taste gate) · Compat & Save (PatchOps, `MayRequire`, LoadFolders, load order, `ExposeData`, renames) · Framework/API (public API, `DefModExtension`, consumers) · MP sync (`[SyncMethod]`, `MP.RegisterSync*`, `Rand`).

They draft artifacts and reply with them. They edit mod files only if given a lane. None drives the game.

## Triage (in WORKFLOW.md)

**Task type** (first match wins): bug fix → port → compat patch → feature (names an existing mod) → new mod.

**Category** (1 QoL, 2 Content, 3 Overhaul, 4 Visual/Audio, 5 Framework): one-line reason. A hint only.

**Specialists by trigger** (each file's `trigger:` line; re-checked after the spec):

| Specialist | Trigger |
|---|---|
| Designer | New Def of a gameplay type, stat/recipe/raid-point numbers, or a new system |
| Writer & Strings | Player-visible text |
| UI/UX | Gizmo, window, tab, settings UI, hotkey, float menu |
| Art & Audio | Texture, `graphicData`, sound, song |
| Compat & Save | PatchOperation, `MayRequire`, LoadFolders, dependency, `defName` rename/removal, `ExposeData`, other-mod conflict, port |
| Framework/API | Other mods consume this mod |
| MP sync | C# that changes game state |

Category hints: 1 → UI/UX · 2 → Designer, Writer, Art & Audio · 3 → Designer, Compat & Save, MP sync · 4 → Art & Audio · 5 → Framework/API, Compat & Save.

### Modes

| Mode | When | What runs |
|---|---|---|
| **solo** | No C#/Harmony, no PatchOperation, no save/MP surface, no new Def *type* | Producer takes the Librarian, Builder and QA rows (incl. their MCP rights). One confirm line instead of a spec. Run folder with `base/`, `hashes.txt`, short ledger. One fresh Reviewer delegate |
| **team** | Everything else | Core 5 + triggered specialists. Instance counts from roster |

Producer states the mode in one line; `/rimworld-team solo|team <task>` overrides.

## Skills attached

| Skill | Owner | Also | Trigger |
|---|---|---|---|
| `rimworld-forge` | Producer 1–2, Librarian 3–5, Builder 6–9 + 11 (C# via CLI, copy DLL into the mod's `Assemblies`), QA 12. Steps 10 `rw_build` and staging are skipped | Designer, Art & Audio (art pipeline), Compat & Save | Any Def / PatchOp / C# / Harmony / Player.log work |
| `diagnosing-bugs` | QA: Phases 1–4, 6 | Builder: Phase 5 + tagged instrumentation | Bug fix, or QA gate red with unknown cause |
| `blast-radius` | Reviewer | Builder answers risks; QA runs game-side proof steps | Harmony (esp. transpilers), Def overrides, save format, MP sync, core-mod edits, framework API change, any bug fix |

Referenced by name + absolute the author's global skills repo source path; `blast-radius` by path only.

## MCP access (each role file carries its own list)

| Tools | Producer | Librarian | Builder | Reviewer | QA | Specialists |
|---|---|---|---|---|---|---|
| Forge read: `rw_doctor` `rw_capabilities` `rw_def_search` `rw_def_inspect` `rw_log_analyze` `rw_plan_validate` | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| `rw_index` (intake, serial) | 🔒 | | | | | |
| `rw_project_new` `rw_generate` `rw_validate`, CLI `csharp-*` — explicit `workspace` in own scratch only | | | ✔ | ✔ (validate a copy) | | |
| `rw_build`, CLI `stage` | never | never | never | never | never | never |
| Decompiler (own process, `load_assembly` from the game's `Managed` folder) | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| `games_list/show/status` | ✔ | | | | ✔ | |
| All other gabs, every `games_call_tool` | | | | | 🔒 | |

Solo: Producer also holds the Librarian, Builder and QA rows. A `rw_def_search` miss is not proof of absence. `forceTakeover` only with Producer's OK. Player-data writes only those named in the consent line.

## Workflow (Producer)

| # | Step | Done when |
|---|---|---|
| 1 | **Intake**: task, `Mods/AGENTS.md`, mod's `AGENTS.md` if it exists (+ optional `## Team`), `rw_doctor`. `rw_index` if missing or older than `Version.txt`/any `Mods/*/About/About.xml`. New mod: copy `toolbox/templates/rimworld-mod` to `Mods/<name>` (per `Mods/AGENTS.md`). Copy the mod to `runs/…/base/`, plus `ModsConfig.xml`; record git SHA + `git status` if git | Goal + out-of-scope ≤3 lines; version + baseline recorded |
| 2 | **Triage**: type, category hint, triggered specialists, mode | One-line reason per pick |
| 3 | **Resolve roster**: `orchestrator_capabilities` once; map roles to provider/model and that provider's effort option. Non-T3 → native subagents, all `inherit`, noted | Every role resolves, or stop and report. Never substitute |
| 4 | **Recon** (parallel): Librarian(s) + design specialists. **Bug fix**: instead, QA builds a red loop (diagnosing-bugs 1–4), then stops the game | Reference gate green / loop is red |
| 5 | **Consent**: spec + human gate 1 (team), confirm line (solo), or hypothesis line (bug fix). Each names any player-data writes (QA's test mod list) | the author said yes to this version |
| 6 | **Build** (parallel XML lanes, one C# lane). Game must be closed first (`games_status`) | Each lane DONE; Producer records `hashes.txt` of the whole mod folder |
| 7 | **Review loop**: reviewers parallel, rounds serial; `review_rounds` from roster, +2 for save/MP/data loss; later rounds = open ids + changed code; stop on nits only; Producer checks every finding; stuck → the author | All reviewers APPROVE the diff matching `hashes.txt` |
| 8 | **QA gate** (one QA). Any file change after review → hashes change → back to 7 | Test gate green on the same hashes |
| 9 | **Human gates** 2/3 (art/audio, UI feel) if triggered, then **Done** + report. Rollback = copy `base/` back (move current to `toolbox/backups` first) | Ledger all green; publish only if the author asks |

QA red → back to 6 as a ledger item.

## Brief (`BRIEF.md`)

Pasted into every `delegate_task`:
1. Role, instance i of N, write scope (own scratch + assigned globs), "no subagents", QA-only line.
2. **Tool check first**, only for servers the role file's `needs:` lists: Forge `rw_doctor`, decompiler `status`, gabs `games_status`. Missing → `STATUS: BLOCKED missing MCP <name>`.
3. Read `Mods\AGENTS.md`, and `<Mod>\AGENTS.md` if it exists.
4. Hard rules (≤8 lines): version = `rw_doctor`; game + player-data folders read-only unless the brief names a write; inside `Mods` write only the named mod folder; Forge always explicit `workspace` in own scratch; never `rw_build` or `stage`; move to `toolbox\backups`, never delete; MP: `[SyncMethod]`/`MP.RegisterSync*`, `Verse.Rand`; only QA touches gabs.
5. Role file body, verbatim.
6. Task fields: mod path, type, mode, round, goal, out of scope, owned globs, absolute input paths.
7. Done-when + reply: `STATUS: DONE|BLOCKED`, role block (Reviewer: `VERDICT`, `SCORE n/10`, findings).

## Roster (`roster.yaml`)

```yaml
version: 1
review_rounds: 3          # base; save/MP/data-loss tasks get +2
defaults: { provider: inherit, model: inherit, effort: inherit, instances: 1 }
roles:
  librarian: {}
  builder: {}             # instances: 2 → two lanes (max one C# lane)
  reviewer: {}            # instances: 2 → two independent votes
  qa: {}                  # instances locked to 1
  specialist: {}          # default for every specialist
  # designer: { provider: <id>, model: <id>, effort: <value> }   ids/values from orchestrator_capabilities
```

`inherit` = main thread's value. Validation: unknown role → error; QA ≠ 1 → error; values must resolve; builders > lanes → reduce and say so. Unavailable → stop and report. Resolved IDs + taskIds go in the ledger.

## Known issues (README)

- Target is 1.7 per the author (Steam `unstable`); installed game is 1.6.4871.
- RimWorldForge, its skill, RimBridgeServer and the mod template hardcode 1.6.
- Codex and other harness configs lack the RimWorld MCPs; those roles will report BLOCKED.
- MP runtime testing blocked.

## Round 2 ledger

| Id | Outcome |
|---|---|
| Opus N1, Sol S2, Muse N2 (solo vs QA/Builder rights) | fixed: solo Producer holds Librarian/Builder/QA rows; solo excludes PatchOperations |
| Opus N2, Opus S8, Sol S1, Muse Sol-S3 (where Builders write, staging, diff, rollback) | fixed: Builders edit mod directly; `base/` copy at intake = diff + rollback; "stage" step removed; "shared isolation" dropped |
| Sol S3 (candidate) | fixed: `hashes.txt` of whole mod folder; any change resets to review |
| Sol S7, Muse S6 (scratch homes) | fixed: one write rule, per-child `runs/…/<role>-<i>/` |
| Sol N1 (DLL lock) | fixed: game closed before build |
| Muse Sol-S6 / S4 (red loop order) | fixed: bug fix step 4 = QA red loop before build |
| Muse Opus-S2 (tool check) | fixed: check per role `needs:`; dropped unverifiable step-3 warn |
| Muse N1 (new mod folder) | fixed: intake copies template into `Mods/<name>` |
| Muse N3 (C# lanes race) | fixed: at most one C# lane owns csproj + Assemblies |
| Muse N4 (ModsConfig) | fixed: QA sets/restores; `base/` copy; consent line names it |
| Opus N3 (forge steps vs rw_build) | fixed: Builder 6–9 + 11, step 10 skipped |
| Opus N4, Muse N6 (panel, precedence, effort) | fixed: panel cut; +2 rule; placeholders |
| Muse N5 | fixed: "if it exists" |
| Muse N7 | fixed: staleness rule |

## Round 3 (scores Opus 9, Sol 8, Muse 8; all CHANGES, no disputes; fixed in build)

| Id | Fix in built files |
|---|---|
| Sol N1, Muse N1 (repro before consent) | WORKFLOW step 4: repro consent line before QA runs; QA backs up saves |
| Muse N2 (ModsConfig in base/) | `RUN\ModsConfig.xml`, sibling of `base\` |
| Sol N2, Muse N3, Opus N3 (validate the candidate, keep resolve step) | `snapshot.ps1 -Forge` flattens the real candidate for `rw_validate`; Builder runs rimworld-forge 6–10 minus `rw_build` |
| Sol N3 (index staleness) | `rw_index` every intake |
| Muse N4, Opus nit (hash churn) | `snapshot.ps1` skips `.git`, `obj`, `bin`, `.vs` |
| Muse N5, Opus nit (new mod too early) | Template copied after step-5 consent; rollback moves it to backups |
| Muse N6 (who closes the game) | QA always ends with `games_stop` + restore; Producer asks the author if a game is running at build |
| Muse N7 (solo branches) | Solo line in steps 4–6; solo bug fix uses the hypothesis line |
| Muse N8, Opus nit (forge → mod copy, disjoint) | Builder step 3; lanes disjoint |
| Opus S1 (debug logs owner) | Step 4 may delegate a Builder for `[DBG-<slug>]` logs only; step 6 removes them; QA greps |
| Opus nits (diff command, QA crash restore, known issues order) | `git diff --no-index base candidate-r<n>`; step 8 restore; README lists AGENTS.md first |

## Round 1 ledger

All 27 round-1 ids resolved in v2 (blockers: stage/rw_build ban, explicit workspace, per-delegate decompiler, serial `rw_index`). See v2 notes in round-2 reviews.

## Round 4 (built files; Opus 8, Sol 8, Muse 8; all CHANGES; fixed)

- `snapshot.ps1 -Forge` follows `LoadFolders.xml <v{ver}>` (incl. conditional folders), exits `NO XML` instead of a false green, resolves relative paths, exits 0 on success. Tested on MoreBiomes, SmarterConstruction, AllowTool, Harmony.
- Forge folders per round (`forge-r<n>`). Builders validate only their own lane; Producer validates the whole candidate after all lanes. `def.duplicate` across Def types noted as a Forge false positive (verified on MoreBiomes).
- C# lane owns `**/Assemblies/**`; `OutputPath` from the version load folder; scaffold via `rwforge csharp-scaffold`.
- QA: set mod list, persist, restart, confirm `get_mod_configuration_status` before testing. Old save / removal / perf only when the spec names them (now in the spec shape). `NEED LOGS` reply.
- Bug-fix loop: consent covers temp `[DBG]` logs; QA stops game, Builder adds logs, fresh QA reruns. Solo bug fix: Producer is QA.
- `spec.md` and `refs.md` always written (short in solo/bug fix).
- Specialists scheduled: all triggered draft in step 4; lane-holders follow Builder rules; MP/Compat/Framework re-check each review round.
- Crash recovery: Producer may `games_stop` only here; restores ModsConfig and saves.
- BRIEF has a `Player-data writes allowed` line. `needs:` aligned with each role's Tools.

## Round 5 (final; Opus APPROVE 9, Muse APPROVE 9, Sol CHANGES 9)

- Sol N1 (scaffold needs a workspace): fixed. Builder runs `rwforge project-new` then `csharp-scaffold`; verified both exit 0 and produce a `.csproj`.
- Nits fixed: bug-fix "no spec" wording, `forge-r<n>-<try>` for Producer retries, `reorder_mod` before BLOCKED, solo row lists spec/refs, script path in BRIEF, Builder lane-copy subfolders.
- Budget (5 rounds) used. No open blockers or shoulds.

## Round 6 change set (the author's feedback, 2026-10-31)

- **Project-only, not global.** The author's dotfiles repo stub was moved out (sync uninstalled it from all global skill folders). The toolbox is now the T3 project `RimWorldModToolbox`, with project-level skills (`.claude/skills`, `.agents/skills`) and MCP configs for all 6 harnesses (`.mcp.json`, `.codex/config.toml`, `.cursor/mcp.json`, `opencode.json` v2 `mcp.servers`, `.agents/mcp_config.json`). `Verse.ModLister.RebuildModList` loads every folder in `Mods` (dot-folders too), so none of this can live in `Mods`.
- **Tested per harness from the toolbox:**
  - Claude `-p`, Muse `exec` and Antigravity `-p`: all 3 tools answered.
  - Codex `mcp list`: all 3 enabled. OpenCode `mcp list`: all 3 connected.
  - Codex and OpenCode outside the toolbox: none.
  - Cursor: untested (disabled in T3, no CLI).
- **Needed for that:** trust entries for Codex, Muse and the Antigravity CLI. An `env` block in the JSON configs, because Muse strips HOME/USERPROFILE. OpenCode v2 nesting.
- **Roster** lists every role explicitly, one line each. WORKFLOW step 3 errors if a role file has no roster line, or a roster line has no role file. Specialists are pulled by trigger only.
- **1.7** is on Steam `unstable` (Waylith engine, off Unity). Decompiler loads via `gameDir`, with an `assemblyPath` fallback. The Builder copies the target framework from a working mod for the version.
- WORKFLOW step 1 stops unless the run starts in the toolbox project, because T3 delegates inherit the parent's project.

## Round 8 change set (the author: "use the skill from inside any mod folder, old and new"; move rimworld-forge)

- **Per-mod kit.** `kit.py` installs the skills (`team/SKILL.md`, the RimWorldForge-shipped `rimworld-forge` with absolute doc links) and the per-harness MCP files (`kit/`) into a mod folder.
  - It also adds trust entries (Codex, Muse, Antigravity CLI) and git `info/exclude` lines, keeps `Mods/.mcp.json` in sync, and moves replaced files to backups via a manifest (`.agents/rimworld-kit.json`).
  - Idempotent: a second run writes nothing (manifest included, after round-8 fix).
- **Installed** in the author's 9 mod repos and the toolbox. Not in the framework folders (Harmony, HugsLib, RimBridgeServer, XmlExtensions, VEF).
- **Why per mod:**
  - Harnesses stop discovery at the git root, and each mod is its own repo.
  - The `Mods` root can't hold harness folders.
  - Folders *inside* a mod are ignored by RimWorld's mod scan.
- **Tested from inside a mod folder:** Claude `-p`, Muse `exec`, agy `-p` all called the 3 tools. Codex and OpenCode list all 3. Muse lists both skills as project skills in MoreBiomes and none outside. Kit files don't show in `git status`.
- **`rimworld-forge` left the author's global skills repo** (committed and pushed). Sync removed it from all global skill folders. Role files point at the toolbox's installed copy.
- **WORKFLOW:**
  - Runs from any kit folder.
  - A mod folder with no `About.xml` is a new mod; the template is copied into it after consent.
- **Known:** kit files ship with a Workshop upload (publish from a clean copy). Cursor untested.

## Round 10: public package (no council round yet at time of writing)

- **Solo mode removed.** The author: "the point is a repeatable team agentic workflow." Every task runs the core roles plus triggered specialists. Bug fixes still replace the design spec with a red repro loop.
- **Machine-neutral.** `kit.py` finds the Mods folder through Steam (registry + `libraryfolders.vdf`), or takes `--mods`, and saves it in `local.json`. It fills `{{TOOLBOX}}`, `{{MODS}}`, `{{GAME}}`, `{{PLAYER}}`, `{{HOME}}`, `{{APPDATA}}`, `{{LOCALAPPDATA}}` in the kit templates and the skill. `team\` files use the names TOOLBOX, MODS, GAME, PLAYER; the rendered skill gives the Producer the real paths.
- `--doctor` checks every prerequisite. `--no-trust` skips the trust edits.
- Personal core mods are out of the role files. Core mods now come from the user's optional `Mods\AGENTS.md` (example in `templates\`). The MP sync specialist triggers only when Multiplayer is a core mod or the mod claims MP support.
- The `diagnosing-bugs` and `blast-radius` skills had no license, so they are optional-by-name, and the core of each is written into the role files.
- `docs\` written; this history moved here from `team\DESIGN.md`.

## Round 11: specialist split (author's request)

- Designer split in two: **Systems & Balance** (systems designer + balance analyst) and **Content & Quest** (content designer + quest/event designer). When both run, Content & Quest writes the Def sheet first and Systems & Balance balance-checks it.
- **Sound** split out of Art & Audio into its own specialist; Art keeps textures and graphics wiring. Separate human sign-offs: style (Art), loudness (Sound).
- 9 specialists now. Roster, triggers, category hints and docs updated.
