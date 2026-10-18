# NATO Counters Expanded - Counter Pipeline

Moved here from `GEMINI.md` on 2026-10-18, when the rule file was reduced to the rules that always apply; `GEMINI.md` says when to read which section.

## 5. Counter Generation Pipeline

### 5.0 The icon picker stops at index 1023: this mod needs the patched picker
- **The engine lists only icon indices 0 to 1023 and stops at the first index without a sprite** [LIM-001] [LIM-002]. RBM's GFX Overhaul declares 0 to 1079, the game and its DLC 0 to 121 [RBM-002], so every pickable index is taken and nothing a mod appends shows in an unpatched game. The lookup that draws a template's icon has no such bound [ICON-005], and no script sets a template's icon [ICON-003] [ICON-004]: the picker is the only way.
- **The owner's decisions (2026-10-15)**: no icon of RBM's, the game's or the Anniversary Pack's is ever replaced. Instead the picker's constant is raised on this machine with the Modding Manager's `Scripts\Executable\Set-HoiIconPickerLimit.ps1` (`-Status` shows the state, `-Restore` undoes it, the original executable stays beside it as `hoi4.exe.before-picker-patch`). A game update replaces the executable: run `-Status` after one and patch again.
- **A local mod, never published (owner's decision, 2026-10-15)**: do not upload it to the Steam Workshop. Do not run `build.ps1 -PublishSteam`, the Manager's `Publish-Mod.ps1` or the `hoi4-mod-release` skill for it, and leave `steamWorkshopId` in the Manager's registry empty. Without the patched picker none of its counters can be picked, so a Workshop copy would not work for anyone.
- **This mod starts at 1080, exactly where RBM ends.** A gap would hide every icon after it [LIM-002]; the generator refuses to write when the installed RBM no longer ends at 1079 or the game declares one of this mod's indices.
- **The counters work in the patched game**: on 2026-10-15 with RBM loaded and the picker limit raised, the picker ran through RBM's 1079 and on to this mod's 1847; the last counter was picked, shown in the designer and the template list, and drawn on the map [LIM-003] [ICON-001].

### 5.1 What this mod is
- **An expansion of RBM's GFX Overhaul, never a replacement**: it only appends icons after RBM's own. It must not ship a file at a path RBM or vanilla uses, define any sprite other than `GFX_div_templ_<1080 or higher>_large` and `_small`, or use `replace_path` in `descriptor.mod`. `tests/Counters.Tests.ps1` enforces all three.
- **RBM is the style authority, not the NATO standard**: RBM's symbols follow the MPU icon conventions, which differ from APP-6 in places. In RBM, anti-tank is a V pointing down with a dot, and anti-air is a peak with a crossbar. A symbol drawn from general NATO knowledge will contradict the icon RBM shows right next to it. Always copy the glyph RBM itself draws for that branch.
- **Generated files are never hand-edited**: everything under `gfx/interface/counters/` and `interface/nato_counters_expanded.gfx` is written by `python tools/generate_counters.py`. To change a counter, change `tools/counters/symbols.py` and regenerate. Install the Python packages once with `pip install -r tools/requirements.txt`.

### 5.2 Adding a symbol
Follow these steps in order. Do not skip step 1 or 2.
1. **Confirm it is new.** RBM already offers these as selectable division counters: Military Police, Harbour Defence, Militia, Garrison, Foot Infantry, Marine Infantry, Mountain Infantry, Airborne Infantry, Commando Infantry, Shock Infantry, Horsed Cavalry, Semi Motorised Infantry, Motorised Infantry, Mechanised Infantry, Amphibious Mechanised, Cavalry Tank, Infantry Tank, Light Tank, Medium Tank, Heavy Tank, Super-Heavy Tank. Do not add any of them or a lookalike. RBM's `Support.Recon.Tank` and `Support.Recon.Cavalry` battalion icons are the same glyphs as its Cavalry Tank and Horsed Cavalry counters, so they are lookalikes too.
2. **Find RBM's own glyph for the branch.** RBM draws most branches as battalion icons. `python tools/check_references.py --list` names them and `--reference <Name>` prints one pixel by pixel. They sit on the same plate as the map-size counters, so they are an exact target.
3. **Write the draw function** in `tools/counters/symbols.py` and append `Symbol("key", "Display Name", "<RBM battalion icon name>", function)` to the END of `SYMBOLS`. Build it from the shared parts wherever RBM's glyph contains them (`armour_oval`, `gun_dot`, `anti_tank_vee`, `anti_air_peak`, `recon_slash`, `hollow_wheels`, `solid_wheels`, `weight_bars`, `amphibious_waves`), so the same shape is identical on every counter.
4. **Fit it.** `python tools/check_references.py --show <key>` prints RBM's glyph and yours side by side with a match score from 0 to 1. Adjust until it is at least 0.80; the existing symbols score 0.86 to 0.99.
5. **Generate and look.** Run `python tools/generate_counters.py`, then open `artifacts/reference_comparison.png` (RBM's icon next to yours) and `artifacts/counter_preview.png` (all 12 colours, then the four echelons at map size); `artifacts/picker_preview.png` shows where the new counters fall in the picker. Finish with `build.ps1 -Test`.

- **A branch RBM has no icon for**: draw it first in `tools/counters/proposals.py` and show it to the user on the design sheet (`python tools/design_sheet.py`, written to `artifacts/design_sheet.png`). Only after the user has approved the design, move it to `SYMBOLS` with `None` as the reference, its marks with it as shared parts. Say in your report that it has no RBM reference.

### 5.3 What the generator refuses
`generate_counters.py` writes nothing and exits with an error when:
- a symbol matches its RBM reference below 0.80;
- a symbol matches one of RBM's existing counters at 0.80 or more (a duplicate; the closest legitimate symbol today, `sp_artillery_super_heavy` against Super-Heavy Tank, scores 0.79);
- RBM's GFX Overhaul no longer ends at icon index 1079, or the game declares one of this mod's indices (the icons would collide, or a gap would hide this mod's icons: stop and tell the user);
- a symbol was removed, renamed or its key changed (see 5.5).

If RBM's GFX Overhaul is not installed, the comparison is skipped with a warning. A build made that way is unverified; never report it as checked.

### 5.4 Drawing rules
- The drawing area is the inside of the plate: 45 units wide and 23 high, origin top left, y pointing down. Use the constants `W`, `H`, `CX`, `CY`.
- One function renders both counter sizes and every colour and echelon. Never write per-size or per-colour code.
- `Pen` offers `line`, `polygon`, `disc`, `ring`, `arc` and `oval`. Lines default to 1.6 units, which matches RBM's strokes. There is no text primitive yet; a letter symbol needs one added to `tools/counters/canvas.py` first.

### 5.5 Icon indices are permanent
- A division template keeps its icon as the index number [ICON-002], and `assets/counters/index_manifest.json` pins that number for every counter. Once a campaign uses the counters, never remove, rename or reorder a symbol key, never edit the manifest by hand and never pass `--renumber`. Any of these makes existing saves show the wrong icon.
- RBM's GFX Overhaul owns indices 0 to 1079; this mod starts at 1080 (`FIRST_INDEX` in `tools/counters/layout.py`), and every symbol ships in all 4 echelons and 12 colours (`SHIPPED_VARIANTS`), 48 indices per symbol.

### 5.6 Plates
- `assets/counters/plates/` and `assets/counters/palette.json` are derived from an installed RBM's GFX Overhaul by `python tools/extract_plates.py`. Re-run it only when RBM changes its plate artwork. Do not paint or edit plates by hand.


## 5.7 In-game check without the launcher
- **In-game check without the launcher**: the 1440p mod's harness drives the game. From the sibling repository `..\hoi4-1440p-ui-mod`: dot-source `tools\GameHarness.ps1`, then `Set-HoiPlayset -Mods @('mod/ugc_3496134789.mod', 'mod/nato-counters-expanded.mod')`, `Start-Hoi4`, `Start-HoiNewGame` (a paused 1936 game as Germany), `Send-HoiKey -Key u` for Recruit & Deploy, `Save-HoiScreenshot`, and `Stop-Hoi4` at the end, which restores the user's playset. Captures land in that repo's `scratch\checks`. The launcher file `mod/nato-counters-expanded.mod` must point at this folder (`build.ps1 -DevLink`).
