# <Mod Name>

<!--
RimWorld mod template. Fill in the <placeholders> and delete any section that doesn't apply.
Every line should change a decision the agent would otherwise get wrong.
-->

This mod lives in RimWorld's `Mods` folder. If `Mods\AGENTS.md` exists, read it first: it has the game version, the core mods this mod must work with, and the read-only paths. This file only adds what is specific to this mod.

## What this is

`<Mod Name>` (`<author.modname>`) is `<one sentence: what it adds or changes in the game>`.

## Never compromise on

1. Works alongside the core mods listed in `Mods\AGENTS.md`, if any.
2. `<the thing that matters most for this mod, e.g. "vanilla balance", "no new research tab">`

## Dependencies

Frameworks this mod uses. Each one is in `About/About.xml` under `modDependencies` and `loadAfter`.

- `<e.g. Harmony (brrainz.harmony): patches X>`

## Glossary

Words that mean something specific in this mod. Use them back to me.

- **`<word>`**: `<what it means here>`

## Layout

- `About/About.xml`: name, packageId, supported versions, dependencies.
- `<1.6/Defs/>`: `<what Defs live here>`
- `<Source/>`: `<C# project, if any. Build output goes to 1.6/Assemblies/>`

## Team

Optional. Used by `/rimworld-team`. Remove this section if you don't need it.

- Always add: `<specialists, e.g. systems-balance>`
- Leave out: `<specialists, e.g. art: art is hand-made>`

## Build and test

- Build: `<e.g. dotnet build Source/<Mod>.csproj -c Release, or "XML only, no build">`
- Validate: `rw_validate` can't read a mod folder directly. Run `powershell -NoProfile -ExecutionPolicy Bypass -File <toolbox>\team\snapshot.ps1 -Mod <this folder> -Forge <scratch> -Version <v>`, then `rw_validate` on `<scratch>`.
- In game: `gabs` → `games_start rimworld`, then `<how to see this mod working: debug action, spawn X, open tab Y>`.
- Read errors: `rimworldforge` `rw_log_analyze` on `Player.log`.

## Ways to hurt yourself here

From real mistakes. Replace with yours.

1. **`<mistake>`**: `<what happened, and what to do instead>`
