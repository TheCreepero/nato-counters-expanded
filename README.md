# NATO Counters Expanded

Adds more NATO-style division counters to [RBM's GFX Overhaul](https://steamcommunity.com/sharedfiles/filedetails/?id=3496134789), in the same style, every colour and every echelon.

The counters are not drawn by hand. Each symbol is a few lines of drawing code, and a generator renders it onto the counter plates for all 12 colours, 4 echelons and both sizes.

## Overview

> **Status: a local mod, not published.** The division designer's icon picker lists only icon indices below 1024 [LIM-001], and with RBM's GFX Overhaul every one of them is taken [RBM-002]. This mod's counters start at 1080, right after RBM's last icon, and show only in a game whose picker limit has been raised on this machine (see The picker limit below). The owner decided on 2026-10-15 to keep it local: it is not uploaded to the Steam Workshop.

- **Game**: Hearts of Iron IV
- **Supported Version**: `1.19.*`
- **Mod Version**: `1.0`
- **Tags**: Graphics, Military
- **Requires**: RBM's GFX Overhaul, loaded before this mod

## An expansion, not a replacement

This mod only adds. It appends its counters after RBM's own and changes nothing RBM, the base game or its DLC ship:

- No file sits at a path that RBM's GFX Overhaul or vanilla uses. Every texture carries the `nce.` prefix.
- The only sprites defined are new division template icons, numbered from 1080. RBM's GFX Overhaul uses 0 to 1079, the base game and its DLC 0 to 121.
- `descriptor.mod` has no `replace_path`.

The test suite checks all three on every run.

## The picker limit

The game lists only icon indices 0 to 1023 in the division designer's picker, and stops at the first index that has no sprite [LIM-001] [LIM-002]. RBM's GFX Overhaul fills 0 to 1079, so nothing a mod appends can be picked in an unpatched game, while the lookup that draws a template's icon has no such bound [ICON-005]. The limit is one constant in `hoi4.exe`. The Modding Manager's `Scripts\Executable\Set-HoiIconPickerLimit.ps1` raises it on this machine after saving the original executable (`-Status` shows the state, `-Restore` puts it back). A game update replaces the executable; run the script with `-Status` after one and patch again if needed.

## Symbols

RBM's GFX Overhaul offers 21 selectable division counters, covering infantry, cavalry, motorised and mechanised troops, tanks, militia, garrison and military police. This mod adds the branches it only draws as battalion icons:

Artillery, Motorised Artillery, Anti-Tank, Anti-Air, Rocket Artillery, Self-Propelled Artillery, Tank Destroyer, Self-Propelled Anti-Air, Motorised Recon, Armoured Car, Bicycle Infantry, Engineer, Signal, Medical, Logistics, Maintenance.

Each symbol comes as Corps, Division, Brigade and Regiment in white, urban, black, red, orange, desert, mountain, jungle, forest, marine, airborne and arctic: 48 counters per symbol.

Every symbol copies the glyph RBM's GFX Overhaul itself uses for that branch. RBM follows the MPU icon conventions, which differ from the NATO standard in places: anti-tank is a V pointing down with a dot, anti-air a peak with a crossbar.

---

## How the counters are made

```
tools/counters/symbols.py        one draw function per symbol, each naming the RBM icon it copies
        |
tools/generate_counters.py  ---> gfx/interface/counters/division_templates_large/nce.*.designer.dds   (76x42)
        |                        gfx/interface/counters/division_templates_small/nce.*.map.dds        (56x31)
        |                        interface/nato_counters_expanded.gfx
        |                        artifacts/counter_preview.png
        |                        artifacts/reference_comparison.png
        |                        artifacts/picker_preview.png
assets/counters/plates/          blank plates, one per colour, echelon and size
assets/counters/palette.json     ink colour per plate colour
assets/counters/index_manifest.json   the icon index of every counter
```

Setup, once:

```powershell
pip install -r tools\requirements.txt
```

Regenerate everything after changing a symbol:

```powershell
python tools\generate_counters.py
```

Three sheets are written to `artifacts\`:

- `counter_preview.png`: one row per symbol, the division counter in all 12 colours followed by the four echelons at map size.
- `reference_comparison.png`: RBM's battalion icon next to this mod's counter for the same branch, with the match score.
- `picker_preview.png`: the counters as the division designer's picker lists them, 8 per row in index order, starting with RBM's last row. A red line marks where this mod begins at 1080; a yellow line every 8 rows marks one screen of the picker.

### The RBM check

Before writing anything, the generator compares every symbol with an installed copy of RBM's GFX Overhaul and stops if:

- a symbol does not match the RBM icon it claims to copy (match below 0.80 on a scale of 0 to 1);
- a symbol duplicates a counter RBM already offers;
- RBM's GFX Overhaul no longer ends at icon index 1079, or the game declares one of this mod's indices: the icons would collide, or a gap would hide this mod's icons from the picker.

Run the check on its own, or inspect one symbol pixel by pixel:

```powershell
python tools\check_references.py
python tools\check_references.py --show anti_tank
python tools\check_references.py --list
```

If RBM's GFX Overhaul is not installed the check is skipped with a warning, and the build is unverified.

### Adding a symbol

1. Make sure RBM's GFX Overhaul does not already offer it as a division counter.
2. Find the battalion icon RBM draws for the branch: `python tools\check_references.py --list`, then `--reference <Name>` to print it.
3. In `tools/counters/symbols.py`, write a function that draws on `pen`, reusing the shared parts (`armour_oval`, `gun_dot`, `anti_tank_vee` and so on). The drawing area is the inside of the plate, 45 units wide and 23 high, with `(0, 0)` at the top left.
4. Append a `Symbol("key", "Display Name", "<RBM icon name>", function)` line to the end of `SYMBOLS`.
5. Fit it with `python tools\check_references.py --show key`, then run the generator and look at both sheets.

```python
def tank_destroyer(pen):
    armour_oval(pen)
    anti_tank_vee(pen)
    gun_dot(pen)
```

### Icon indices must stay stable

The game stores a division template's icon as a number. `assets/counters/index_manifest.json` records the number of every counter so that it never changes between releases; a new counter takes the next index after the last one. The range starts at 1080 (`FIRST_INDEX` in `tools/counters/layout.py`), right after RBM's last icon, because the picker stops at a gap.

Once a campaign uses the counters, only append symbols. Removing, renaming or reordering one would make that campaign's templates show the wrong icon. The generator refuses to run if a symbol disappears; `--renumber` overrides that and is only safe before the freeze, the first campaign kept with these counters (see `ROADMAP.md`).

### Plates

The blank plates are derived from an installed copy of RBM's GFX Overhaul. They only need rebuilding if RBM changes its plate artwork:

```powershell
python tools\extract_plates.py
```

---

## Directory Architecture

```
C:\dev\nato-counters-expanded/
|-- descriptor.mod                  # Clausewitz engine descriptor
|-- thumbnail.png                   # Launcher thumbnail (512x512)
|-- build.ps1                       # Core build and lifecycle engine
|-- gfx/                            # Generated counter textures
|-- interface/                      # Generated sprite definitions
|-- assets/                         # Plates, palette and index manifest (generator input)
|-- tools/                          # Counter generator and RBM check (Python)
|-- artifacts/                      # Preview sheets and release archives (git-ignored)
|-- tests/                          # Automated Pester test suites
|-- GEMINI.md                       # Development rules for agents (CLAUDE.md includes it)
\-- ROADMAP.md                      # Planned work and the decisions waiting for the owner
```

---

## Development & Automation Commands

All lifecycle tasks are managed through `build.ps1`:

```powershell
# 1. Deploy mod to local Paradox Interactive Hearts of Iron IV mod folder
.\build.ps1 -Deploy

# 2. Configure zero-copy DevLink (the launcher loads this folder itself; restart the game to see a change)
.\build.ps1 -DevLink

# 3. Validate syntax and bracket balance without deploying
.\build.ps1 -ValidateOnly

# 4. Run automated test suites (Pester)
.\build.ps1 -Test

# 5. Package clean release zip archive
.\build.ps1 -Package

# 6. Clean deployed mod files and temporary archives
.\build.ps1 -Clean
```

---

## Automated Testing

Unit tests are written with [Pester](https://pester.dev) and located in `tests/`. `Counters.Tests.ps1` checks that every sprite has its texture, that textures have the size and format RBM's GFX Overhaul uses, that the icon indices form one unbroken range starting at 1080, and that the mod replaces nothing.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Run-Tests.ps1
```

---

## Credits

- **Author**: TheCreepero
- The counter plates and the visual style come from [RBM's GFX Overhaul](https://steamcommunity.com/sharedfiles/filedetails/?id=3496134789) by RBM, published under CC BY-NC-SA 4.0.
- RBM's GFX Overhaul credits the NATO counters to the [MPU Division Icons](https://steamcommunity.com/sharedfiles/filedetails/?id=1331463070) by mpu.daemos.
