"""Install the RimWorld project kit into a mod folder, so every AI harness opened there gets the
RimWorld skills (rimworld-team, rimworld-forge) and the project-only MCP servers.

    python kit.py --doctor                       check prerequisites and show the paths in use
    python kit.py MyMod [OtherMod ...]           install or refresh in existing mods (name under Mods, or full path)
    python kit.py --new <slug>                   make an empty Mods\\<slug> with the kit, for a brand-new mod
    python kit.py --refresh                      refresh this toolbox and every mod that already has the kit
    python kit.py --mods "D:\\SteamLibrary\\steamapps\\common\\RimWorld\\Mods" --doctor   set the Mods folder

Sources (edit these, then run --refresh):
    team\\SKILL.md                                        -> rimworld-team skill
    mcp\\RimWorldForge\\skills\\rimworld-forge\\SKILL.md     -> rimworld-forge skill (doc links made absolute)
    kit\\*                                                -> per-harness MCP and settings files

{{TOOLBOX}}, {{MODS}}, {{GAME}}, {{PLAYER}}, {{HOME}}, {{APPDATA}}, {{LOCALAPPDATA}} in the sources are
replaced with this machine's paths. The Mods path is saved in local.json (not committed).

It also adds the folder to Codex, Muse and Antigravity CLI trusted projects (they only load project
config from trusted folders; skip with --no-trust), and to the mod's local git exclude so kit files are
never committed. Replaced files are moved to backups\\kit\\, never deleted.
Windows only for now. Python 3.11+, standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

TOOLBOX = Path(__file__).resolve().parent
LOCAL = TOOLBOX / "local.json"
BACKUPS = TOOLBOX / "backups" / "kit"
STAMP = time.strftime("%Y%m%d-%H%M%S")
MANIFEST = ".agents/rimworld-kit.json"
FORGE_ROOT = TOOLBOX / "mcp" / "RimWorldForge"
KIT_DIRS = [".claude/", ".agents/", ".codex/", ".cursor/", ".muse/", ".mcp.json", "opencode.json"]
# Frameworks, not the user's own mods: updates replace these folders wholesale.
FRAMEWORKS = {"harmony", "hugslib", "rimbridgeserver", "xmlextensions", "vanillaexpandedframework"}
# Note: a file dropped from kit_files() stays in mods that already have it. Move it to backups by hand.
MODS: Path = Path()  # set by load_paths()
PATHS: dict[str, str] = {}


# ---------- paths ----------

def steam_mods_candidates() -> list[Path]:
    """RimWorld Mods folders in every Steam library this machine knows about."""
    roots: list[Path] = []
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
            roots.append(Path(winreg.QueryValueEx(k, "SteamPath")[0]))
    except OSError:
        pass
    roots.append(Path(r"C:\Program Files (x86)\Steam"))
    libs: list[Path] = []
    for r in roots:
        libs.append(r)
        vdf = r / "steamapps" / "libraryfolders.vdf"
        if vdf.is_file():
            text = vdf.read_text(encoding="utf-8", errors="replace")
            libs += [Path(m.replace("\\\\", "\\")) for m in re.findall(r'"path"\s+"([^"]+)"', text)]
    seen, out = set(), []
    for lib in libs:
        m = (lib / "steamapps" / "common" / "RimWorld" / "Mods").resolve()
        if str(m).lower() not in seen:
            seen.add(str(m).lower())
            out.append(m)
    return out


def load_paths(mods_arg: str | None) -> None:
    global MODS
    saved = json.loads(LOCAL.read_text(encoding="utf-8")) if LOCAL.is_file() else {}
    if mods_arg:
        mods = Path(mods_arg).resolve()
    elif saved.get("mods"):
        mods = Path(saved["mods"])
    else:
        found = [m for m in steam_mods_candidates() if m.is_dir()]
        if not found:
            raise SystemExit('Could not find RimWorld\'s Mods folder. Run: python kit.py --mods "<path to RimWorld\\Mods>" --doctor')
        mods = found[0]
    if not mods.is_dir():
        raise SystemExit(f"Mods folder not found: {mods}")
    home = Path.home()
    MODS = mods
    PATHS.update({
        "TOOLBOX": str(TOOLBOX), "MODS": str(mods), "GAME": str(mods.parent),
        "PLAYER": str(home / "AppData" / "LocalLow" / "Ludeon Studios" / "RimWorld by Ludeon Studios"),
        "HOME": str(home),
        "APPDATA": os.environ.get("APPDATA", str(home / "AppData" / "Roaming")),
        "LOCALAPPDATA": os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local")),
    })
    if saved.get("mods") != str(mods):
        LOCAL.write_text(json.dumps({"mods": str(mods)}, indent=2) + "\n", encoding="utf-8")


# ---------- rendering ----------

def fill(text: str, slash: str = "\\") -> str:
    for k, v in PATHS.items():
        text = text.replace("{{" + k + "}}", v.replace("\\", slash))
    return text


def fill_json(text: str) -> str:
    def walk(o):
        if isinstance(o, dict):
            return {k: walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [walk(v) for v in o]
        if isinstance(o, str) and "{{" in o:
            return os.path.normpath(fill(o))
        return o
    return json.dumps(walk(json.loads(text)), indent=2) + "\n"


def kit_files() -> dict[str, str]:
    """Relative target path -> file text, filled in for this machine."""
    def read(p: Path) -> str:
        return p.read_text(encoding="utf-8").replace("\r\n", "\n")

    team = fill(read(TOOLBOX / "team" / "SKILL.md"))
    forge_src = FORGE_ROOT / "skills" / "rimworld-forge" / "SKILL.md"
    forge = None
    if forge_src.is_file():
        base = FORGE_ROOT.as_posix()
        forge = read(forge_src).replace("`docs/", f"`{base}/docs/").replace("`knowledge/", f"`{base}/knowledge/")
    mcp = fill_json(read(TOOLBOX / "kit" / "mcp.json"))
    files = {
        ".mcp.json": mcp,
        ".cursor/mcp.json": mcp,
        ".agents/mcp_config.json": mcp,
        ".codex/config.toml": fill(read(TOOLBOX / "kit" / "codex-config.toml"), "/"),
        "opencode.json": fill_json(read(TOOLBOX / "kit" / "opencode.json")),
        ".claude/settings.json": fill_json(read(TOOLBOX / "kit" / "claude-settings.json")),
    }
    tomllib.loads(files[".codex/config.toml"])
    for root in (".claude/skills", ".agents/skills"):
        files[f"{root}/rimworld-team/SKILL.md"] = team
        if forge is not None:
            files[f"{root}/rimworld-forge/SKILL.md"] = forge
    return files


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------- install ----------

def resolve_target(arg: str) -> Path:
    """The real folder (links resolved). Only the toolbox or a folder directly inside Mods passes."""
    p = Path(arg)
    target = (p if p.is_absolute() else MODS / arg).resolve()
    if target == TOOLBOX:
        return target
    if target.parent != MODS.resolve():
        raise SystemExit(f"Refusing {target}: the kit goes only in a folder directly inside Mods, or the toolbox.")
    if target.name.lower() in FRAMEWORKS:
        raise SystemExit(f"Refusing {target.name}: it's a framework, not one of your mods.")
    return target


def install(target: Path, files: dict[str, str], do_trust: bool) -> None:
    man_path = target / MANIFEST
    old = json.loads(man_path.read_text(encoding="utf-8")) if man_path.is_file() else {}
    wrote, backed = 0, 0
    for rel, text in files.items():
        dest = target / rel
        if dest.is_file():
            current = dest.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
            if current == text:
                continue
            if sha(current) != old.get(rel):  # not something the kit wrote: keep a copy
                b = BACKUPS / f"{target.name}-{STAMP}" / rel
                b.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dest), b)
                backed += 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8", newline="\n")
        wrote += 1
    manifest = json.dumps({k: sha(v) for k, v in files.items()}, indent=2) + "\n"
    if not man_path.is_file() or man_path.read_text(encoding="utf-8") != manifest:
        man_path.parent.mkdir(parents=True, exist_ok=True)
        man_path.write_text(manifest, encoding="utf-8")
    excluded = git_exclude(target)
    trusted = trust(target) if do_trust and target != TOOLBOX else []
    print(f"{target.name}: {wrote} file(s) written, {backed} moved to backups"
          f"{', git exclude updated' if excluded else ''}{', trusted in ' + ', '.join(trusted) if trusted else ''}")


def git_exclude(target: Path) -> bool:
    """Add the kit to the repo's local exclude file. Works when .git is a folder or a file.
    Not a repo yet: nothing to do (the mod template's .gitignore covers new mods)."""
    if not (target / ".git").exists():
        return False
    r = subprocess.run(["git", "-C", str(target), "rev-parse", "--git-path", "info/exclude"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False
    ex = Path(r.stdout.strip())
    ex = ex if ex.is_absolute() else target / ex
    ex.parent.mkdir(parents=True, exist_ok=True)
    lines = ex.read_text(encoding="utf-8").splitlines() if ex.is_file() else []
    missing = [p for p in KIT_DIRS if p not in lines]
    if missing:
        header = "# rimworld kit (machine-specific, see RimWorldModToolbox kit.py)"
        old_header = "# rimworld kit (machine-specific, see RimWorldModToolbox\\kit.py)"
        has_header = header in lines or old_header in lines
        ex.write_text("\n".join(lines + ([] if has_header else [header]) + missing) + "\n", encoding="utf-8")
    return bool(missing)


def backup_global(p: Path) -> None:
    b = BACKUPS / f"global-{STAMP}" / p.relative_to(Path.home())
    if p.is_file() and not b.exists():
        b.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, b)


def trust(target: Path) -> list[str]:
    done = []
    path = str(target)
    codex = Path.home() / ".codex" / "config.toml"
    if codex.is_file():
        s = codex.read_text(encoding="utf-8")
        keys = {k.lower() for k in tomllib.loads(s).get("projects", {})}
        if path.lower() not in keys:
            backup_global(codex)
            s = s.rstrip("\n") + f"\n\n[projects.'{path.lower()}']\ntrust_level = \"trusted\"\n"
            tomllib.loads(s)
            codex.write_text(s, encoding="utf-8")
            done.append("Codex")
    muse = Path.home() / ".config" / "muse" / "trust.json"
    if muse.is_file():
        d = json.loads(muse.read_text(encoding="utf-8"))
        key = "\\\\?\\" + path
        if key.lower() not in {k.lower() for k in d.get("projects", {})}:
            backup_global(muse)
            d.setdefault("projects", {})[key] = {"decision": "trusted"}
            muse.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
            done.append("Muse")
    agy = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
    if agy.is_file():
        d = json.loads(agy.read_text(encoding="utf-8"))
        ws = d.setdefault("trustedWorkspaces", [])
        if path.lower() not in {w.lower() for w in ws}:
            backup_global(agy)
            ws.append(path)
            agy.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
            done.append("Antigravity")
    return done


# ---------- doctor ----------

def doctor() -> int:
    bad = 0

    def line(ok: bool | None, what: str, hint: str = "") -> None:
        nonlocal bad
        mark = {True: "ok  ", False: "MISS", None: "info"}[ok]
        bad += ok is False
        print(f"[{mark}] {what}" + (f"\n         -> {hint}" if hint and ok is not True else ""))

    print("Paths:")
    for k in ("TOOLBOX", "MODS", "GAME", "PLAYER"):
        print(f"  {k:8} {PATHS[k]}")
    line(sys.platform == "win32", "Windows", "Only Windows is supported for now.")
    line(sys.version_info >= (3, 11), f"Python {sys.version.split()[0]} (3.11+)", "Install Python 3.11 or newer.")
    line(bool(shutil.which("git")), "git on PATH", "Install Git for Windows.")
    v = Path(PATHS["GAME"]) / "Version.txt"
    line(v.is_file(), f"RimWorld found: {v.read_text().strip() if v.is_file() else '-'}", "Wrong Mods folder? Use --mods.")
    line(Path(PATHS["PLAYER"]).is_dir(), "RimWorld player-data folder", "Start RimWorld once so it creates it.")
    fpy = FORGE_ROOT / ".venv" / "Scripts" / "python.exe"
    line(fpy.is_file() and (FORGE_ROOT / "mcp_server" / "server.py").is_file(),
         "RimWorldForge in mcp\\RimWorldForge (with .venv)", "See docs\\install.md, RimWorldForge.")
    line((FORGE_ROOT / "skills" / "rimworld-forge" / "SKILL.md").is_file(),
         "rimworld-forge skill (ships with RimWorldForge)", "Update RimWorldForge.")
    line((TOOLBOX / "mcp" / "DecompilerServer" / "DecompilerServer.exe").is_file(),
         "DecompilerServer in mcp\\DecompilerServer", "See docs\\install.md, DecompilerServer.")
    rt = subprocess.run(["dotnet", "--list-runtimes"], capture_output=True, text=True) if shutil.which("dotnet") else None
    line(bool(rt and "Microsoft.NETCore.App 10." in rt.stdout), ".NET 10 runtime (for DecompilerServer)", "Install the .NET 10 runtime.")
    line((TOOLBOX / "mcp" / "GABS" / "gabs.exe").is_file(), "GABS in mcp\\GABS", "See docs\\install.md, GABS.")
    gcfg = Path.home() / ".gabs" / "config.json"
    has_rw = gcfg.is_file() and "rimworld" in json.loads(gcfg.read_text(encoding="utf-8")).get("games", {})
    line(has_rw, "GABS has a 'rimworld' game in ~/.gabs/config.json", "See docs\\install.md, GABS.")
    mods_ids = set()
    for d in MODS.iterdir() if MODS.is_dir() else []:
        a = d / "About" / "About.xml"
        if a.is_file():
            m = re.search(r"<packageId>\s*([^<]+?)\s*</packageId>", a.read_text(encoding="utf-8", errors="replace"), re.I)
            if m:
                mods_ids.add(m.group(1).lower())
    line("brrainz.rimbridgeserver" in mods_ids, "RimBridgeServer mod in Mods (in-game half of GABS)", "See docs\\install.md, RimBridgeServer.")
    line(True if "brrainz.harmony" in mods_ids else None, "Harmony mod in Mods", "Or subscribe on the Workshop. Most C# mods need it.")
    for name, exe in (("Claude Code", "claude"), ("Codex", "codex"), ("OpenCode", "opencode"),
                      ("Antigravity CLI", "agy"), ("Muse Code", "muse")):
        line(True if shutil.which(exe) else None, f"{name} CLI", "Optional: install the harnesses you use.")
    print("All required checks passed." if not bad else f"{bad} required check(s) missing.")
    return 1 if bad else 0


# ---------- main ----------

def main() -> None:
    ap = argparse.ArgumentParser(description="Install the RimWorld project kit into mod folders.")
    ap.add_argument("mods", nargs="*", help="mod folder names under Mods, or full paths")
    ap.add_argument("--new", metavar="SLUG", help="create an empty Mods\\<slug> and install the kit")
    ap.add_argument("--refresh", action="store_true", help="refresh the toolbox and every mod that has the kit")
    ap.add_argument("--doctor", action="store_true", help="check prerequisites and show paths")
    ap.add_argument("--mods", dest="mods_dir", metavar="PATH", help="RimWorld Mods folder (saved in local.json)")
    ap.add_argument("--no-trust", action="store_true", help="don't add trust entries to Codex / Muse / Antigravity")
    a = ap.parse_args()
    load_paths(a.mods_dir)
    if a.doctor:
        sys.exit(doctor())
    targets: list[Path] = []
    if a.new:
        t = resolve_target(a.new)
        if t.exists():
            raise SystemExit(f"{t} already exists. Use: python kit.py {a.new}")
        t.mkdir()
        print(f"Created {t}. Until /rimworld-team fills it in, RimWorld lists it as a mod with no About.xml.")
        targets.append(t)
    if a.refresh:
        targets.append(TOOLBOX)
        for d in sorted(MODS.iterdir()):
            if d.is_dir() and (d / MANIFEST).is_file():
                try:
                    targets.append(resolve_target(str(d)))
                except SystemExit as e:
                    print(f"Skipped: {e}")
    targets += [resolve_target(m) for m in a.mods]
    if not targets:
        ap.print_help()
        sys.exit(1)
    files = kit_files()
    if not any(k.endswith("rimworld-forge/SKILL.md") for k in files):
        print("Note: RimWorldForge not found in mcp\\RimWorldForge, so the rimworld-forge skill was skipped. Run --doctor.")
    for t in dict.fromkeys(targets):
        if not t.is_dir():
            raise SystemExit(f"No such folder: {t}")
        install(t, files, not a.no_trust)
    # MODS\.mcp.json (a plain file, safe in Mods) serves Claude and Muse when Mods itself is the project.
    mods_mcp, text = MODS / ".mcp.json", files[".mcp.json"]
    if not mods_mcp.is_file() or mods_mcp.read_text(encoding="utf-8").replace("\r\n", "\n") != text:
        if mods_mcp.is_file():
            b = BACKUPS / f"Mods-{STAMP}" / ".mcp.json"
            b.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(mods_mcp, b)
        mods_mcp.write_text(text, encoding="utf-8", newline="\n")
        print("Mods\\.mcp.json refreshed (old copy in backups\\kit)")


if __name__ == "__main__":
    main()
