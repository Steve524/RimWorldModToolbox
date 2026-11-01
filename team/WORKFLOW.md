# rimworld-team workflow

You are the **Producer**: the main thread. You run every step below, talk to the user, and are the only one who delegates. Every task gets the team: the core roles always, plus the specialists its triggers pull in. Read `roles\core\producer.md` now for your rules and tools.

The skill that started you lists the real paths for this machine. Use them wherever these names appear, and replace the names with the real paths in every brief you send:

| Name | What it is |
|---|---|
| TOOLBOX | This repository (the folder that holds `team\`) |
| MODS | RimWorld's `Mods` folder |
| GAME | The RimWorld install folder |
| PLAYER | RimWorld's player-data folder (`Config\`, `Saves\`, `Player.log`) |
| RUN | `TOOLBOX\team\runs\<ModFolder>\<yyyymmdd-slug>` |
| SNAP | `powershell -NoProfile -ExecutionPolicy Bypass -File TOOLBOX\team\snapshot.ps1` |

**Write rule (everyone):** a delegate writes only its own `RUN\<role>-<i>\` folder and the mod globs its brief assigns. You write everything else in RUN. Inside MODS, nobody writes outside the mod folder named in the brief.

## Steps

1. **Intake.**
   - Your working folder must have the kit (`.agents\skills\rimworld-team\`): a mod folder directly in MODS, or TOOLBOX. Delegates run in the same folder, and the RimWorld MCPs are wired only in kit folders. If it is missing, stop and tell the user to run `python TOOLBOX\kit.py <ModFolder>`.
   - Working folder is a mod folder: that is the mod for this run. If it has no `About\About.xml`, it is a **new mod**. Working folder is TOOLBOX: the task must name the mod.
   - Read the task, `MODS\AGENTS.md` and `MODS\<Mod>\AGENTS.md` if they exist. They may list core mods the work must stay compatible with, and a `## Team` section that adds or drops specialists.
   - Run `rw_doctor`. Its `major.minor` is this run's game version. If an `AGENTS.md` names a different target version, tell the user in one line.
   - Run `rw_index` (serial; no delegate is running yet).
   - Make RUN. Existing mod: `SNAP -Mod MODS\<Mod> -Copy RUN\base`. Copy `PLAYER\Config\ModsConfig.xml` to `RUN\ModsConfig.xml`. If the mod is a git repo, record `git rev-parse HEAD` and `git status --short`.
   - New mod: baseline the (empty) folder anyway, so the diff shows everything you add. From TOOLBOX: no folder yet; it is made in step 5.
   - Done when the ledger has goal, out of scope (3 lines max), version, and baseline.
2. **Triage** (tables below): task type, category hint, specialists by trigger. Done when each pick has a one-line reason in the ledger.
3. **Resolve the roster.** Read `TOOLBOX\team\roster.yaml`. Call `orchestrator_capabilities` once. Map each role in the lineup to a provider, model, and that provider's own effort option. `inherit` means your own value. No capabilities tool (not T3 Code): use your harness's native subagents, everything `inherit`, and note it.
   - Errors: a role file in `roles\` (other than producer) with no roster line, a roster line with no role file, or `qa` instances not 1. More builders than lanes: use fewer and say so.
   - Done when every role resolves. If one can't, stop and tell the user exactly which. Never substitute.
   - Record resolved ids in the ledger.
4. **Recon.**
   - Librarian(s) in parallel, split by question area, plus **every triggered specialist**, drafting its part of the spec. One order to keep: when both run, Content & Quest writes the Def sheet first, then Systems & Balance balance-checks it. Done when every claim in `RUN\refs.md` has tool evidence.
   - Bug fix: first ask the user the repro consent line: "QA will run the game with mod list X and load save Y (backed up first). A Builder may add temporary `[DBG]` logs. Everything is restored after. OK?" Then loop until the bug is red:
     1. QA builds the red loop (see `qa.md`) and always ends with the game stopped.
     2. QA replies `NEED LOGS`: delegate a Builder to add only `[DBG-<slug>]` logs.
     3. Delegate a fresh QA to re-run the loop.
     Done when the loop is red. The Librarian still answers the questions the hypotheses raise.
5. **Consent.** Done when the user says yes to this exact version. Record it in the ledger.
   - Write `RUN\spec.md` (shape below) and ask the user to approve it.
   - Bug fix: the red loop replaces the design part. The spec is short: "Cause: X (loop: `<command>`). Fix: Y in files Z", lanes, and test steps, with the red loop going green as step 1.
   - New mod, after yes: copy the contents of `TOOLBOX\templates\rimworld-mod` into the mod folder, skipping files that already exist (the kit's). From TOOLBOX: copy it to `MODS\<spec name>`, run `python TOOLBOX\kit.py <spec name>`, then baseline it as in step 1.
6. **Build.**
   - The game must be closed (`games_status`). If it is running, ask the user to close it.
   - Lanes: disjoint globs. At most one C# lane, owning `Source/**`, `*.csproj`, `**/Assemblies/**`. Lane 1 also owns `About/**`, `LoadFolders.xml`, and the mod's `AGENTS.md`. XML lanes run in parallel. A specialist given a lane is a lane owner, under the Builder rules. Every `Wiring` row's Def file must fall in some lane.
   - Bug fix: the lane that owns each tagged file removes every `[DBG-<slug>]` line.
   - When every lane replies DONE: run `SNAP -Mod <mod> -Forge RUN\producer\forge-r<n>-<try> -Version <v>`, then `rw_validate` on it with the index. Use a new `<try>` number each time. Errors go back to the lane that owns the file.
   - Then run `SNAP -Mod <mod> -Hashes RUN\hashes.txt` and `SNAP -Mod <mod> -Copy RUN\candidate-r<n>`.
   - Done when validation is clean (or `NO XML`) and both are written.
7. **Review loop.**
   - Each round: a fresh delegate per reviewer instance (T3 Code: a new `delegate_task`). Never the builder's thread. Triggered MP sync, Compat & Save and Framework/API also re-check the diff each round, replying in the Reviewer's findings format.
   - Reviewers diff `git diff --no-index RUN\base RUN\candidate-r<n>`. Exit code 1 just means files differ.
   - Budget: `review_rounds` from the roster, +2 when the task touches saves, Multiplayer, or data loss. Round 1 is full. Later rounds check open ids and changed code only. Stop when a round returns only nits.
   - Check every finding yourself:
     - Agree: smallest fix, back to that lane, re-hash, new candidate.
     - Disagree: give evidence.
     - Nit or out of scope: decline in one line and list it as a follow-up.
   - Stuck: an item is still disputed after two replies, or the budget runs out. Show the user both sides in 2–3 lines each. Budget end is not approval.
   - A CHANGES verdict with only nits counts as APPROVE. Going back from QA to step 6 does not reset the budget.
   - Done when every reviewer APPROVEs a candidate that matches `hashes.txt`.
8. **QA gate.**
   - First run `SNAP -Mod <mod> -Check RUN\hashes.txt`. Fail: back to 7.
   - QA runs the spec's test steps (see `qa.md`) and ends with `games_stop` plus restores.
   - QA red: add a ledger item, go back to 6.
   - Done when the test gate is green and `-Check` still passes afterwards.
9. **Human gates, then done.**
   - If Art, Sound or UI/UX ran, ask the user to sign off on style, loudness and feel. Give them the screenshot paths and the sounds to listen to.
   - Report: gate table, highest evidence tier, files changed, follow-ups, resolved models and taskIds.
   - Publish only if the user asks, and from a clean copy (`SNAP -Mod <mod> -Copy <folder>` drops the harness kit).
   - Rollback (only if the user asks): move the mod folder to `TOOLBOX\backups\<Mod>-<date>`, then copy `RUN\base` back. New mod: move it to backups.

**Crash recovery** (step 4 or 8, when a QA delegate crashes or is BLOCKED with the game possibly open):
1. Run `games_stop` (the only time you may), or ask the user to close the game.
2. Copy `RUN\ModsConfig.xml` back to `PLAYER\Config\`.
3. Copy the save backups from `RUN\qa-<i>\` back to `PLAYER\Saves\`.

## Triage

**Task type.** First match wins:
1. Error, crash, red text, broken → **bug fix**
2. Port or version update → **port**
3. Works with another mod, conflict, load order → **compat patch**
4. Working folder has `About\About.xml`, or the task names an existing mod → **feature**
5. Step 1 found a new mod (no `About\About.xml`) → **new mod**

**Category hint.** Record one or more, with a reason. Categories only hint at triggers. They never pick roles.

| # | Category | Usual triggers |
|---|---|---|
| 1 | Quality of life: controls, menus, convenience | UI/UX |
| 2 | Content expansion: items, animals, factions, events | Content & Quest, Systems & Balance, Writer, Art |
| 3 | Gameplay overhaul: major systems or mechanics | Systems & Balance, Compat & Save, MP sync |
| 4 | Visual or audio: graphics, textures, sounds | Art, Sound |
| 5 | Utility or framework: supports other mods or development | Framework/API, Compat & Save |

**Specialists come in only by trigger.** Re-check triggers after the spec. Bug fixes add a specialist only if the cause hits its trigger.

| Specialist (`roles\specialists\`) | Trigger in the task or spec |
|---|---|
| `systems-balance.md` | A new or changed system or mechanic; raid-point or wealth scaling; any stat, cost, market-value or raid-point numbers (it leads a pure rebalance) |
| `content-quest.md` | New or changed gameplay Defs (e.g. items, weapons, apparel, buildings, animals, pawn kinds, factions, research, hediffs, genes); new incidents, quests, events |
| `writer.md` | Player-visible text |
| `ui-ux.md` | Gizmo, window, tab, settings UI, hotkey, float menu |
| `art.md` | A new or changed texture, `graphicData`, render tree or icon, including any new Def that needs one (not when it reuses vanilla art) |
| `sound.md` | A new or changed sound effect or song (`SoundDef`, `SongDef`, audio files). Pointing a Def at an existing vanilla sound is the Builder's job |
| `compat-save.md` | PatchOperation, `MayRequire`, LoadFolders, dependency, `defName` rename or removal, `ExposeData`, other-mod conflict, port |
| `framework-api.md` | Other mods consume this mod |
| `mp-sync.md` | C# that changes game state, when the RimWorld Multiplayer mod is a core mod or the mod claims Multiplayer support |

The Reviewer always runs its blast-radius check on bug fixes.

## Shapes

`RUN\spec.md`:
```
# <Mod>: <task>    version <n>
Goal / Non-goals / Type, categories
Systems: steps + balance table (systems & balance)
Def sheet: one row per Def (content & quest)
Wiring: Def file (owner lane) | defName | field | value (art, sound; the owning lane applies these)
Sound manifest: file | use | length | loudness | provenance (sound)
Lanes: lane | owner | globs
Test steps for QA: numbered, each with an expected result
Old save to load: <name | none>   Removal expectation: <what happens | n/a>   Perf budget: <e.g. +0.5 ms/tick | none>
Player-data writes: test mod list, saves loaded (backed up)
Multiplayer / save impact: one line each
```

`RUN\ledger.md`:
```
## Gates     gate | state | evidence link
## Runs      role | i | provider/model/effort | taskId | round | status
## Findings  id | round | from | sev | file:line | claim | outcome | evidence
```
