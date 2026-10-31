# Delegate brief

Paste this, filled in, as the `task` of every `delegate_task`. The child sees nothing else, so inline the role file body. Don't just pass its path. Replace every `<TOOLBOX>`, `<MODS>`, `<GAME>`, `<PLAYER>`, `<RUN>`, and the same bare names inside the role file, with the real paths.

```
You are the <ROLE> (<i> of <N>) on a RimWorld mod team. Do only this role.
Write only: <RUN>\<role>-<i>\  and these mod globs: <globs | none>.
Do not start subagents or delegates.
<QA only: You are the only agent that runs RimWorld.>

== First ==
1. Tool check, only for servers your role needs: rimworldforge `rw_doctor`, decompiler `status`, gabs `games_status`.
   If one is missing, reply `STATUS: BLOCKED missing MCP <name>` and stop.
2. Read <MODS>\AGENTS.md and <Mod>\AGENTS.md if they exist.

== Hard rules ==
- Game version = what rw_doctor reports (<version>). Not memory, not docs.
- <GAME> and <PLAYER> are read-only, unless this brief names a write.
- Inside Mods, write only the mod folder named here. Never add other folders there.
- Forge tools always get an explicit `workspace` inside your own run folder. Never run `rw_build` or `rwforge stage`.
- Never delete. Move old files to <TOOLBOX>\backups.
- <Only if Multiplayer matters for this mod:> game-state changes go through [SyncMethod] / MP.RegisterSync*. Randomness uses Verse.Rand, never System.Random.
- Only QA touches gabs beyond games_status.

== Role ==
<role file body, verbatim>

== Task ==
Mod: <abs path>   Type: <type>   Round: <n>
Goal: <1–3 lines>
Out of scope: <list>
Inputs: <abs paths: spec.md, refs.md, base\, candidate-r<n>\, hashes.txt, prior findings>
Script: <TOOLBOX>\team\snapshot.ps1 (run with powershell -File)
Player-data writes allowed: <from the user's consent line | none>
<Re-review: check only open ids <S2,S5> and code changed since candidate-r<n-1>.>

== Done when ==
<the role's done-when line>

== Reply ==
STATUS: DONE | BLOCKED: <reason>
<the role's reply block>
```
