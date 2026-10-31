# RimWorld Mods

<!--
Optional. Copy this file to your RimWorld Mods folder as AGENTS.md (a plain file is safe there; a folder is not).
Every agent working on any of your mods reads it. /rimworld-team uses the core-mods table for compatibility checks.
-->

**Target game version: 1.6** (`rw_doctor` reports what is actually installed; build and test against that.)

## Core mods

The mods you always play with. Every mod you build must work alongside them. Delete the Multiplayer row if you don't play Multiplayer; with it, the team adds the MP sync specialist to any C# that changes game state.

| Mod | Folder | packageId |
|---|---|---|
| Harmony | `Harmony` | `brrainz.harmony` |
| Multiplayer | `Multiplayer` | `rwmt.Multiplayer` |

## Rules

- Only mods go in this folder. RimWorld loads every folder here as a mod, dot-folders included.
- The game folder and the player-data folder (`%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios`) are read-only, unless you ask for a change.
- Move old versions to the toolbox's `backups\`, never delete them.
