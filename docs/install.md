# Install

Windows only for now: the snapshot script is PowerShell, and the paths assume a Windows Steam install.

## What you need

| Thing | Why | Get it |
|---|---|---|
| RimWorld (Steam) | The game the team builds for | Steam. 1.7 is on the `unstable` beta branch; 1.6 is the main branch. |
| Python 3.11+ | Runs `kit.py` and RimWorldForge | python.org |
| Git | Clones, diffs, git excludes | git-scm.com |
| .NET 10 runtime | Runs DecompilerServer | dotnet.microsoft.com |
| .NET SDK | Only to build C# mods (`dotnet build`) | dotnet.microsoft.com |
| At least one AI harness | Runs the team | T3 Code (recommended: it can run each role on a different provider), Claude Code, Codex, OpenCode, Antigravity, Cursor, Muse Code |

## Steps

### 1. Clone this repo

Put it anywhere outside the RimWorld `Mods` folder. RimWorld loads every folder in `Mods` as a mod.

```
git clone https://github.com/<you>/RimWorldModToolbox
cd RimWorldModToolbox
```

### 2. RimWorldForge (Def index, XML validation, Player.log analysis)

```
git clone https://github.com/SenjuWoo/RimWorldForge mcp\RimWorldForge
python -m venv mcp\RimWorldForge\.venv
mcp\RimWorldForge\.venv\Scripts\python -m pip install -e mcp\RimWorldForge
```

It also ships the `rimworld-forge` skill that `kit.py` installs.

### 3. DecompilerServer (read the game's C#)

Download the latest `win-x64` zip from https://github.com/pardeike/DecompilerServer/releases and extract it to `mcp\DecompilerServer\`, so that `mcp\DecompilerServer\DecompilerServer.exe` exists.

### 4. GABS (drive the live game)

Download the latest `windows-amd64` zip from https://github.com/pardeike/GABS/releases and extract it to `mcp\GABS\`, so that `mcp\GABS\gabs.exe` exists.

Then tell GABS about RimWorld. Either run `mcp\GABS\gabs.exe games add rimworld` and follow the prompts, or put this in `%USERPROFILE%\.gabs\config.json` (fix the path to your install):

```json
{
  "version": "1.0",
  "games": {
    "rimworld": {
      "id": "rimworld",
      "name": "RimWorld",
      "launchMode": "DirectPath",
      "target": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\RimWorld\\RimWorldWin64.exe",
      "stopProcessName": "RimWorldWin64.exe",
      "defaultProfile": "dev",
      "profiles": { "dev": { "description": "Default local RimWorld session" } }
    }
  }
}
```

### 5. RimBridgeServer (the in-game half of GABS)

Download the latest release from https://github.com/pardeike/RimBridgeServer/releases and extract it to `<RimWorld>\Mods\RimBridgeServer\`. Enable it in the game's mod list, together with Harmony (`Mods\Harmony` or the Workshop).

### 6. Check

```
python kit.py --doctor
```

It finds your `Mods` folder through Steam. If it picks the wrong one, set it: `python kit.py --mods "D:\SteamLibrary\steamapps\common\RimWorld\Mods" --doctor`. The path is saved in `local.json`.

### 7. Install the kit into your mods

```
python kit.py MyMod OtherMod     existing mods (folder names in Mods)
python kit.py --new MyNewMod     a brand-new, empty mod folder
```

That writes the skills and MCP config for every harness into each mod folder (see [harness-setup.md](harness-setup.md)), trusts the folder in Codex, Muse and the Antigravity CLI (`--no-trust` to skip), and adds the kit files to the mod's git exclude.

### 8. Optional

- Copy `templates\mods-folder-AGENTS.md` to `<RimWorld>\Mods\AGENTS.md` and list your core mods. The team keeps every mod compatible with them.
- Edit `team\roster.yaml` to pick a provider, model, effort and instance count per role. Everything defaults to `inherit` (the main thread's model).
- Optional skills the roles use if you have them installed: `diagnosing-bugs` and `blast-radius`. The role files carry the core of both, so nothing breaks without them.

## Use

Open a mod folder (for example `<RimWorld>\Mods\MyMod`) as the project in your harness and type:

```
/rimworld-team add a hotkey that toggles all doors
```

## Update

- Pull this repo, then `python kit.py --refresh` (updates every mod that has the kit).
- RimWorldForge: `git -C mcp\RimWorldForge pull`, reinstall with pip, then `kit.py --refresh` (its skill may have changed).
- DecompilerServer, GABS, RimBridgeServer: replace the folders with the new release.
