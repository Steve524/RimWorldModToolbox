# RimWorld and tool findings

Facts verified against the real game and tools while building this (RimWorld 1.6.4871, October 2026). Each one changed a rule somewhere in `team\`.

## The game

| Finding | Evidence | Rule it led to |
|---|---|---|
| Every top-level folder in `Mods` loads as a mod, dot-folders included | `Verse.ModLister.RebuildModList` → `new DirectoryInfo(ModsFolderPath).GetDirectories()`; `TryAddMod` has no filter | Never put tool or harness folders at the `Mods` root. Kit folders live inside mod folders |
| Only the top level is scanned | Same method | A `.claude` inside a mod folder is ignored by the mod scan |
| A Workshop upload ships the whole mod folder | `GetWorkshopUploadDirectory()` returns the mod's root; no filter | Publish from a clean copy: `snapshot.ps1 -Copy` skips the kit and build output |
| Defs load only from `Defs/` in the active load folders | `ModContentPack.LoadDefs` | Validation must follow `LoadFolders.xml` |
| defNames only need to be unique within one Def type | e.g. a `BiomeDef` and a `FeatureDef` both named `ZBiome_AlpineMeadow` in a working mod | Forge's `def.duplicate` across types is a false positive |
| A running game locks mod DLLs | Build fails while RimWorld runs | The game is closed before every build |
| 1.7 moves RimWorld from Unity to Ludeon's Waylith engine, on Steam's `unstable` branch | Ludeon's announcement, Oct 2026 | Never hardcode the version or the `RimWorldWin64_Data\Managed` path; trust `rw_doctor`, and load the decompiler by `gameDir` with an `assemblyPath` fallback. Copy the C# target framework from a mod that already works on the version |

## RimWorldForge (MCP)

| Finding | Where | Rule |
|---|---|---|
| 11 MCP tools; C# helpers (`csharp-scaffold`, `csharp-build`) and `stage` are CLI-only | `mcp_server/server.py`, `src/rwforge/cli.py` | Role files name only real tools |
| `stage --approve` deletes `Mods\<name>` (`rmtree`) before copying | `builder.py` → `util.copytree_clean` | Nobody runs `stage` or `rw_build`; builders edit the mod folder directly |
| `rw_project_new` without `workspace` writes into the current folder | `project.py` | Always pass an explicit `workspace` in the run folder |
| `rw_validate` only scans a flat `source\{About,Defs,Patches,Textures}` workspace, and writes `reports\validation.json` | `validator.py` | `snapshot.ps1 -Forge` flattens the real candidate (following `LoadFolders.xml`) into a scratch workspace, and exits `NO XML` instead of a false pass |
| `rw_index` writes one shared JSON, non-atomically | `indexer.py`, `util.py` | Only the Producer runs it, at intake, before any delegate |
| `rw_def_search` misses content the indexer doesn't see | `indexer.py` (only `1.6/` + `Common/`) | A search miss is not proof of absence; check raw `Data\` XML or the decompiler |
| 1.6 is hardcoded in defaults and the version warning | `project.py`, `generator.py`, `validator.py` | Set versions explicitly; re-check `About.xml` after generation |
| `csharp-scaffold` needs a Forge workspace made by `project-new` first | CLI run | Builder runs `project-new`, then `csharp-scaffold` |

## DecompilerServer (MCP)

- 44 tools: 38 read-only, 6 stateful (`load_assembly`, `unload`, `select_context`, `set_decompile_settings`, `clear_caches`, `warm_index`).
- Each harness, and each delegate, runs its own server process. Loaded assemblies are **not** shared, so every role that needs it loads its own context.

## GABS + RimBridgeServer (MCP, live game)

- One game, one profile, one process. GABS takes an ownership lease; `forceTakeover` steals it.
- `games_call_tool` reaches about 128 bridge tools. Some persist player data: `rimworld/set_mod_enabled` and `rimworld/reorder_mod` write `ModsConfig.xml`, `rimworld/update_mod_settings` writes settings, `save_game` writes saves.
- A mod-list change needs a restart. `rimworld/get_mod_configuration_status` reports whether a restart is required and what is loaded.
- Two drivers would wreck each other's state. **Only QA drives the game.** Everyone else hands QA test steps.
- Runtime Multiplayer testing needs the RimBridgeServer Multiplayer companion and a second GABS profile (host and client). Without them, MP checks are static.
- RimBridgeServer shipped only a `1.6` load folder at the time of writing. On 1.7 it may not load until it ships a 1.7 build.
