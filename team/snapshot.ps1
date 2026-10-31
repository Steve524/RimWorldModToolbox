<#
.SYNOPSIS
  Snapshot, hash, check, or Forge-flatten a RimWorld mod folder for rimworld-team runs.
  Skips build output (.git, obj, bin, .vs) and the harness kit (.claude, .agents, .codex, .cursor, .muse,
  root .mcp.json and opencode.json), so -Copy also gives a clean copy for Workshop upload.
  Never writes inside the Mods folder.

.EXAMPLE
  snapshot.ps1 -Mod <mod> -Copy   <run>\base                 # copy the mod (baseline or candidate)
  snapshot.ps1 -Mod <mod> -Hashes <run>\hashes.txt           # write sha256 list
  snapshot.ps1 -Mod <mod> -Check  <run>\hashes.txt           # exit 1 if anything changed
  snapshot.ps1 -Mod <mod> -Forge  <scratch>\forge-r1 -Version 1.6  # flat workspace for rw_validate (follows LoadFolders.xml)
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$Mod,
  [string]$Copy,
  [string]$Hashes,
  [string]$Check,
  [string]$Forge,
  [string]$Version
)
$ErrorActionPreference = 'Stop'
$Skip = @('.git', 'obj', 'bin', '.vs', '.claude', '.agents', '.codex', '.cursor', '.muse')  # build output + harness kit
$SkipRootFiles = @('.mcp.json', 'opencode.json')  # kit files at the mod root
# The Mods folder comes from kit.py's local.json. As a fallback, any path inside a ...\RimWorld\Mods folder is refused too.
$LocalJson = Join-Path (Split-Path $PSScriptRoot -Parent) 'local.json'
$ModsRoot = if (Test-Path -LiteralPath $LocalJson) { ((Get-Content -LiteralPath $LocalJson -Raw) | ConvertFrom-Json).mods.TrimEnd('\') } else { $null }
function Test-InMods([string]$full) {
  if ($ModsRoot -and ($full -ieq $ModsRoot -or $full.StartsWith($ModsRoot + '\', 'OrdinalIgnoreCase'))) { return $true }
  return $full -match '\\RimWorld\\Mods(\\|$)'
}
$Mod = (Resolve-Path -LiteralPath $Mod).Path.TrimEnd('\')
function Get-Full([string]$p) { $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($p) }

function Get-RelFiles([string]$root) {
  Get-ChildItem -LiteralPath $root -Recurse -File -Force | ForEach-Object {
    $rel = $_.FullName.Substring($root.Length + 1)
    $dirs = $rel.Split('\') | Select-Object -SkipLast 1
    if (-not $dirs -and $SkipRootFiles -contains $rel) { return }
    if (-not ($dirs | Where-Object { $Skip -contains $_ })) { $rel }
  }
}

function Assert-NewDest([string]$path) {
  $full = (Get-Full $path).TrimEnd('\')
  if (Test-InMods $full) {
    throw "Refusing to write inside Mods: $full"
  }
  if ((Test-Path -LiteralPath $full) -and (Get-ChildItem -LiteralPath $full -Force | Select-Object -First 1)) {
    throw "Destination exists and is not empty: $full"
  }
  New-Item -ItemType Directory -Force -Path $full | Out-Null
  $full
}

function Copy-Rel([string]$from, [string]$to, [string[]]$rels) {
  foreach ($rel in $rels) {
    $dest = Join-Path $to $rel
    New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
    Copy-Item -LiteralPath (Join-Path $from $rel) -Destination $dest -Force
  }
}

function Get-HashLines([string]$root) {
  $lines = [string[]]@(Get-RelFiles $root | ForEach-Object {
    "{0}  {1}" -f (Get-FileHash -LiteralPath (Join-Path $root $_) -Algorithm SHA256).Hash, $_
  })
  [Array]::Sort($lines, [StringComparer]::Ordinal)
  return ,$lines
}

if ($Copy) {
  $dest = Assert-NewDest $Copy
  $rels = @(Get-RelFiles $Mod)
  Copy-Rel $Mod $dest $rels
  "copied $($rels.Count) files -> $dest"
}

if ($Hashes) {
  $full = Get-Full $Hashes
  if (Test-InMods $full) { throw "Refusing to write inside Mods: $full" }
  $lines = Get-HashLines $Mod
  [IO.File]::WriteAllLines($full, $lines)
  "hashed $($lines.Count) files -> $full"
}

if ($Check) {
  $want = @{}; foreach ($l in [IO.File]::ReadAllLines((Get-Full $Check))) { $h, $p = $l -split '  ', 2; $want[$p] = $h }
  $have = @{}; foreach ($l in (Get-HashLines $Mod)) { $h, $p = $l -split '  ', 2; $have[$p] = $h }
  $diff = @()
  foreach ($p in $want.Keys) { if (-not $have.ContainsKey($p)) { $diff += "removed  $p" } elseif ($have[$p] -ne $want[$p]) { $diff += "changed  $p" } }
  foreach ($p in $have.Keys) { if (-not $want.ContainsKey($p)) { $diff += "added    $p" } }
  if ($diff.Count) { $diff | Sort-Object; "CHECK FAILED: $($diff.Count) difference(s)"; exit 1 }
  "CHECK OK: $($have.Count) files match"
}

if ($Forge) {
  if (-not $Version) { throw "-Forge needs -Version (major.minor from rw_doctor, e.g. 1.6)" }
  $src = Join-Path (Assert-NewDest $Forge) 'source'
  if (Test-Path -LiteralPath (Join-Path $Mod 'About')) { Copy-Rel $Mod $src @(Get-RelFiles $Mod | Where-Object { $_ -like 'About\*' }) }
  # Same folders RimWorld loads: LoadFolders.xml <v$Version> if present, else root + Common + $Version.
  $folders = @('', 'Common', $Version)
  $lf = Join-Path $Mod 'LoadFolders.xml'
  if (Test-Path -LiteralPath $lf) {
    $node = ([xml](Get-Content -LiteralPath $lf -Raw)).DocumentElement.ChildNodes | Where-Object { $_.Name -eq "v$Version" }
    if ($node) {
      $folders = @($node.ChildNodes | Where-Object { $_.Name -eq 'li' } | ForEach-Object {
        if ($_.Attributes.Count) { "NOTE: conditional folder included: $($_.InnerText) ($($_.Attributes[0].Name)=$($_.Attributes[0].Value))" | Write-Host }
        $_.InnerText.Trim().Trim('/', '\').Replace('/', '\')
      })
    } else { Write-Host "NOTE: LoadFolders.xml has no <v$Version>; used root, Common, $Version." }
  }
  $copied = 0
  foreach ($base in $folders) {
    foreach ($sub in @('Defs', 'Patches', 'Textures')) {
      $from = if ($base) { Join-Path (Join-Path $Mod $base) $sub } else { Join-Path $Mod $sub }
      if (-not (Test-Path -LiteralPath $from)) { continue }
      $from = (Resolve-Path -LiteralPath $from).Path.TrimEnd('\')
      $rels = @(Get-RelFiles $from)
      if ($sub -ne 'Textures') { $copied += $rels.Count }
      # Textures merge so texPath stays valid; Defs/Patches keep a per-folder prefix so names don't collide.
      $tag = if ($base) { $base.Replace('\', '_') } else { 'root' }
      $to = if ($sub -eq 'Textures') { Join-Path $src $sub } else { Join-Path (Join-Path $src $sub) $tag }
      Copy-Rel $from $to $rels
    }
  }
  if ($copied -eq 0) { "NO XML: no Defs or Patches in the load folders for $Version. rw_validate would check nothing; skip it and say so."; exit 1 }
  "forge workspace -> $src  ($copied Def/Patch files; run rw_validate with workspace = $(Split-Path $src))"
}

exit 0
