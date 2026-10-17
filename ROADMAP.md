# Roadmap

The planned work for NATO Counters Expanded, in order, and the decisions that wait for the owner. How to do the work is in `GEMINI.md`; engine facts live in the knowledge register and appear here only as citations such as [LIM-003].

Last reviewed: 2026-10-18.

## Using this file

- Work on the first open item of the lowest open phase, unless the owner names another. Phases 1 and 2 belong before the freeze; Phases 3 to 5 can be taken in any order.
- An item marked **Owner (Dn)** waits for the owner. Put the question to them with the options the item lists, then record the answer and its date under [Decisions](#decisions) and move the row from Open to Taken.
- When an item is done, tick it and add the date and a one-line result after it. Update "Last reviewed".
- When a launch or a read teaches something about the engine, record it in the register (`GEMINI.md` section 6) and cite its id here.

## The freeze

The **freeze** is the moment the owner starts a campaign they mean to keep with this mod's counters. From then on every index in `assets/counters/index_manifest.json` is permanent (`GEMINI.md` section 5.5), and a new symbol can only take the next indices. The picker lists icons in index order, so after the freeze a new symbol always appears at the end of the picker, however closely it belongs to an earlier one.

Before the freeze the whole symbol list may be renumbered once: reorder `SYMBOLS` in `tools/counters/symbols.py` and run `python tools/generate_counters.py --renumber`, which hands out indices from 1080 in the order of `SYMBOLS`. This is the one exception to appending at the end of `SYMBOLS` (`GEMINI.md` section 5.2, step 3).

**Freeze status: not reached** as far as recorded on 2026-10-16. The owner's campaign saved on 2026-10-15 (`USA.hoi4`) loads RBM's GFX Overhaul but not this mod. Ask the owner whether the freeze has happened before any renumber, and record the answer here with its date.

## Where the mod stands (2026-10-15)

- One commit, `356b7e2`. 16 symbols, each in 4 echelons and 12 colours: 768 counters at indices 1080 to 1847.
- Every symbol matches its RBM battalion icon at 0.86 to 0.99 and duplicates none of RBM's counters (`python tools/check_references.py`).
- `build.ps1 -Test`: 55 tests pass.
- `hoi4.exe` 1.19.3 is patched with the picker limit at 65536. The last counter was picked, saved and drawn on the map [LIM-003].
- A local mod that is never published (`GEMINI.md` section 5.0).

## Phase 1: foundation (before the freeze)

- [x] **1.1 Picker preview.** Add a sheet to `generate_counters.py`, written to `artifacts/`, that lays the counters out as the division designer's picker shows them: in index order, 8 per row (`symbols_grid` in RBM's `interface/divisiondesignerview.gui`: `max_slots_horizontal = 8`, 504x400 with 76x50 slots, so 8 rows on screen), starting with RBM's last row so the seam at 1080 shows. 1.2 and 2.3 are judged on this sheet. Done when the sheet is written on every run and the owner has seen it.
  - 2026-10-16: done. `artifacts/picker_preview.png` is written on every run (red line at 1080, yellow line every 8 rows); the owner approved it.
- [x] **1.2 Owner (D1): variants per symbol.** 2026-10-16: every symbol keeps all 48 variants. Every symbol ships in 48 variants (`SHIPPED_VARIANTS` in `tools/counters/layout.py`), which fill 6 rows of the picker. After Phase 2 the picker holds 2,712 icons: RBM's 1,080 and 1,632 of this mod's (34 symbols). Options:
  - keep 48 for every symbol;
  - ship fewer colours or echelons for some symbols. This needs per-symbol variants in the generator and a change to `GEMINI.md` section 5.5, which says every symbol ships 48.
- [x] **1.3 Confirm that a save keeps a template's icon.** 2026-10-16: confirmed by the owner's save and reload test; [ICON-002] is now confirmed in the register. The unpatched case was dropped (D2).
  - With the game harness (`GEMINI.md` section 3) or a launch by the owner: give a template one of this mod's icons, save, quit, start the game again and load the save. Any index from 1080 up proves the same thing. The easiest to find is 1080, Artillery, corps, white: the first icon after RBM's arctic Super-Heavy Tanks. The harness has no recipe for the icon picker or for loading a save yet, and saves here are binary (`save_as_binary=yes`), so the save file itself cannot be read for the index.
  - 2026-10-16: the owner ran it by hand; the template kept its icon.
  - **Owner (D2), dropped 2026-10-16:** loading the save in the unpatched game. The owner expects a game update to break saves anyway, so whether this mod's icons survive one does not matter.
  - Done when ICON-002 is confirmed or corrected in the register, the unpatched case is recorded there, and `Set-HoiIconPickerLimit.ps1 -Status` reports the patched executable again.
- [x] **1.4 Local-only clean-up.** Done 2026-10-16. Make the repository match the decision in `GEMINI.md` section 5.0.
  - The Modding Manager keeps these files identical in every mod (`Get-HoiScaffoldFiles` in its `Scripts/HoiManager.Common.ps1`): `tools/HoiModBuild.ps1`, `tests/BuildEngine.Tests.ps1`, `tests/Run-Tests.ps1`, `.github/workflows/ci.yml` and `tests/Knowledge.Tests.ps1`. Make mod-specific changes in `build.ps1`.
  - [x] 2026-10-16: `build.ps1 -PublishSteam` stops with a message naming section 5.0. `-PublishSteam -DryRun` still stages, because the synced `BuildEngine.Tests.ps1` runs it.
  - [x] 2026-10-16: deleted the empty `.steam_username`.
  - [x] 2026-10-16: the `--renumber` help, the error for a removed symbol and `README.md` speak of the freeze instead of publishing.
  - [x] 2026-10-16: `build.ps1` checks the picker limit of `hoi4.exe` after a deploy or `-DevLink` and warns when this mod's highest index cannot be picked, or when the Manager or the game is not found.
  - [x] 2026-10-16 (D3): kept `.github/workflows/ci.yml`. It never runs, because the repository has no remote, but the Manager's scaffold sync would put it back if it were deleted.
  - [x] 2026-10-16 (D3): deleted `wiki/`. It held only the build commands, which `README.md` and `GEMINI.md` section 3 already give; `GEMINI.md` section 1 now says where development notes live.
  - Done when `build.ps1 -ValidateOnly` and `build.ps1 -Test` pass and `git status` shows only the intended changes.

## Phase 2: complete RBM's battalion set

Each symbol here has an RBM battalion icon to copy, so the RBM check applies in full. Add them one at a time by `GEMINI.md` section 5.2. Keys become permanent at the freeze: use the keys below unless the owner chooses others. The existing `sp_artillery`, `tank_destroyer` and `sp_anti_air` are the Light versions; their keys stay as they are.

- [x] **2.1 Shared parts.** Add to `tools/counters/symbols.py`, fitted with `python tools/check_references.py --reference <Name>`:
  - `weight_bars(pen, weight)`: RBM marks a vehicle's weight with vertical bars outside the oval. Light has none, Medium one thin bar at the left, Heavy one thick bar at the left, Super-Heavy a wider block at the left, Modern a bar at each side. Fit it on `Artillery.SPG.Medium`, `.Heavy`, `.SuperHeavy` and `.Modern`.
  - `amphibious_waves(pen)`: the wave line under the oval of `Armour.Amphibious.Light`.
  - 2026-10-18: done. Both are in `tools/counters/symbols.py`; `weighted(draw, weight)` adds the bars to an existing Light glyph.
- [x] **2.2 Symbols.** Done when every row is either added or set aside with its reason written here, the generator writes without refusing, `build.ps1 -Test` passes, and the owner has looked at `artifacts/counter_preview.png` and `artifacts/reference_comparison.png`.

| Keys | Display names | RBM references | Parts |
|---|---|---|---|
| `sp_artillery_medium`, `sp_artillery_heavy`, `sp_artillery_super_heavy`, `sp_artillery_modern` | Medium, Heavy, Super-Heavy, Modern Self-Propelled Artillery | `Artillery.SPG.Medium`, `.Heavy`, `.SuperHeavy`, `.Modern` | `armour_oval`, `gun_dot`, `weight_bars` |
| `tank_destroyer_medium`, `tank_destroyer_heavy`, `tank_destroyer_super_heavy`, `tank_destroyer_modern` | Medium, Heavy, Super-Heavy, Modern Tank Destroyer | `Artillery.TD.Medium`, `.Heavy`, `.SuperHeavy`, `.Modern` | `armour_oval`, `anti_tank_vee`, `gun_dot`, `weight_bars` |
| `sp_anti_air_medium`, `sp_anti_air_heavy`, `sp_anti_air_super_heavy`, `sp_anti_air_modern` | Medium, Heavy, Super-Heavy, Modern Self-Propelled Anti-Air | `Artillery.SPAA.Medium`, `.Heavy`, `.SuperHeavy`, `.Modern` | `armour_oval`, `anti_air_peak`, `weight_bars` |
| `modern_tank` | Modern Tank | `Armour.Tank.Modern` | `armour_oval`, `weight_bars` |
| `motorised_anti_tank` | Motorised Anti-Tank | `Artillery.AntiTank.Motorised` | `anti_tank_vee`, `gun_dot`, `solid_wheels` |
| `motorised_anti_air` | Motorised Anti-Air | `Artillery.AntiAircraft.Motorised` | `anti_air_peak`, `solid_wheels` |
| `motorised_rocket_artillery` | Motorised Rocket Artillery | `Artillery.Rocket.Motorised` | the `rocket_artillery` glyph, `solid_wheels` |
| `armoured_recon` | Armoured Recon | `Support.Recon.ArmouredCar` | `armour_oval`, `recon_slash`, wheels |
| `tank_recon` | Tank Recon | `Support.Recon.Tank` | `armour_oval`, `recon_slash` |
| `amphibious_tank` | Amphibious Tank | `Armour.Amphibious.Light` | `armour_oval`, `amphibious_waves` |
| `cavalry_recon` | Cavalry Recon | `Support.Recon.Cavalry` | a filled triangle |

2026-10-18: 18 of the 20 added (34 symbols, indices 1080 to 2711). Every one matches its RBM icon at 0.86 to 0.95 and passes the duplicate check; the closest, `sp_artillery_super_heavy`, scores 0.79 against RBM's Super-Heavy Tank counter, which differs from it only by the gun dot. Set aside as duplicates:
- `tank_recon`: RBM's `Support.Recon.Tank` is the same glyph as its Cavalry Tank counter (match 0.90).
- `cavalry_recon`: RBM's `Support.Recon.Cavalry` is the same glyph as its Horsed Cavalry counter (match 0.99).

2026-10-18: the owner looked at `artifacts/counter_preview.png` and `artifacts/reference_comparison.png` and approved them.

Watch for these:
- `modern_tank` may score as a duplicate of RBM's tank counters, `amphibious_tank` of RBM's Amphibious Mechanised, and `cavalry_recon` of RBM's Horsed Cavalry. When the generator refuses one as a duplicate, set it aside here with its score.
- RBM has two near-identical motorised rocket icons, `Artillery.Rocket.Motorised` and `Mobile.Rocket.Motorised`. Add one symbol for both.
- Out of scope: `Fake.Intel` and `No.Intel`, which are not branches, and every branch RBM already offers as a counter (`GEMINI.md` section 5.2, step 1).

- [x] **2.3 Owner (D4): group the families, then renumber once.** 2026-10-18: no. The owner keeps the order of `artifacts/picker_preview.png` (the 16 first symbols, then Phase 2's in the order of the table above); nothing is renumbered. Before the freeze only; after it this item lapses and new symbols append. If the owner wants related symbols side by side in the picker, reorder `SYMBOLS` by family, run `generate_counters.py --renumber` once, and show the owner the picker preview (1.1). A proposed order:
  1. Artillery, Motorised Artillery, then Self-Propelled Artillery from Light to Modern.
  2. Rocket Artillery, Motorised Rocket Artillery.
  3. Anti-Tank, Motorised Anti-Tank, then Tank Destroyer from Light to Modern.
  4. Anti-Air, Motorised Anti-Air, then Self-Propelled Anti-Air from Light to Modern.
  5. Modern Tank, Amphibious Tank.
  6. Motorised Recon, Armoured Recon, Armoured Car.
  7. Bicycle Infantry.
  8. Engineer, Signal, Medical, Logistics, Maintenance.

## Phase 3: symbols without an RBM icon

- [ ] **3.1 Owner (D5): propose designs.** Each design needs the owner's approval before it is drawn (`GEMINI.md` section 5.2, last bullet), and each report says it has no RBM reference. Candidates to propose:
  - airborne, mountain and marine versions of artillery, anti-tank, anti-air and engineers, built from the marks RBM puts on its Airborne, Mountain and Marine Infantry (`--reference Infantry.Airborne`, `Infantry.Mountain`, `Infantry.Marine`);
  - armoured and motorised engineers: the engineer glyph with `armour_oval` or `solid_wheels`.

  Show the proposals on the design sheet (4.2), add the approved ones as shared parts and symbols, and record each answer under Decisions. Done when the owner has accepted or declined every proposal.
  - 2026-10-18: 14 proposals in `tools/counters/proposals.py`: Mountain, Airborne and Marine versions of Artillery, Anti-Tank, Anti-Air and Engineer, plus Armoured and Motorised Engineer. The marks copy RBM's own template counters: a small filled peak (Mountain Infantry), a parachute (Airborne Infantry) and an anchor (Marine Infantry). Each mark sits at the bottom centre, where RBM's counters and the motorised wheels put theirs; on Anti-Tank the vee fills the bottom, so the mark sits above the dot. None is closer than 0.60 to an RBM counter (Armoured Engineer to Light Tank). Waiting for the owner.

## Phase 4: tools

- [ ] **4.1 Text primitive** in `tools/counters/canvas.py` (`GEMINI.md` section 5.4). Needed before any letter symbol.
- [x] **4.2 Design sheet.** Render proposed symbols that are not yet in `SYMBOLS` in a few colours and echelons next to the RBM counters they would sit beside, for the owner's approval in 3.1.
  - 2026-10-18: done. `python tools/design_sheet.py` writes `artifacts/design_sheet.png` from `tools/counters/proposals.py`: per proposal, the RBM counter with the same mark, this mod's base symbol, the proposal in 6 colours and its 4 echelons at map size, with its closest RBM counter and score.
- [ ] **4.3 In-game smoke check.** A script on the game harness (`GEMINI.md` section 3) that opens the picker, scrolls to its end, saves a screenshot and scans `error.log` for this mod's sprite names. Done when one command produces both results.

## Phase 5: a larger picker (blocked)

- [ ] **5.1 Owner (D6).** With 2,712 icons, reaching this mod's last counter means scrolling 339 rows of 8 in a picker that shows 8 rows (1.1). A larger picker is a change to a window, and this mod only appends icons (`GEMINI.md` section 5.1). Its home would be the 1440p UI mod (`C:\dev\hoi4-1440p-ui-mod`), but that mod's `wiki/Roadmap.md` puts the designers out of scope (owner, 2026-10-14), because RBM replaces `divisiondesignerview.gui` [RBM-001]. A second picker sits in `countrydeploymentview.gui` (Recruit & Deploy, reworked in that mod's phase A5). Options: revisit that decision for the picker windows alone, or keep the picker as RBM draws it.

## Maintenance

Each of these runs when its trigger happens, whatever phase is open.

- **After a game update.**
  1. Run `Set-HoiIconPickerLimit.ps1 -Status` (in the Modding Manager's `Scripts\Executable`). Patch again on the owner's word. If the script cannot find the compare, read the executable again as that folder's `README.md` describes.
  2. Repeat the picker check of [LIM-003]; until then treat confirmed register records from the older version as provisional.
  3. Update `supported_version` in `descriptor.mod`.
- **After an RBM update.** Run `python tools/generate_counters.py`; if RBM changed its plate artwork, run `python tools/extract_plates.py` first (`GEMINI.md` section 5.6). If the generator refuses, stop and bring the owner the case:
  - **Owner (D7): RBM no longer ends at 1079.** Options: this mod's sprites at the shared indices take the place of RBM's new ones [LOAD-012], which breaks `GEMINI.md` section 5.1; or the owner keeps a local copy of the last RBM version that ends at 1079 and loads it instead of the Workshop copy; or, before the freeze only, move `FIRST_INDEX` to RBM's new end and renumber.
  - **Owner (D7): RBM adds a counter for a branch this mod has.** The duplicate check refuses that symbol. Options: keep both, which needs an exception in the duplicate check; or, before the freeze only, remove this mod's symbol and renumber.
- **When the owner starts a campaign with a new set of counters.** Suggest a git tag on that commit, so the numbering the campaign uses can be found again. The first such campaign is the freeze.

## Decisions

### Taken

| Date | Decision | Where |
|---|---|---|
| 2026-10-15 | No icon of RBM's, the game's or the Anniversary Pack's is replaced. The picker limit is raised on this machine instead. | `GEMINI.md` section 5.0 |
| 2026-10-15 | A local mod, never published to the Steam Workshop. | `GEMINI.md` section 5.0 |
| 2026-10-16 | D1: every symbol ships all 4 echelons in all 12 colours. | 1.2 |
| 2026-10-16 | D3: keep the CI workflow; delete the wiki. | 1.4 |
| 2026-10-16 | D2: no test of a save in the unpatched game. A game update is expected to break saves anyway, so this mod does not plan for campaigns that run across one. | 1.3 |
| 2026-10-18 | D4: keep the current symbol order in the picker; no renumber. Phase 2's symbols follow Maintenance. | 2.3 |

### Open

| Id | Question | Item | Needed by |
|---|---|---|---|
| D5 | Which designs without an RBM icon to add? | 3.1 | each proposal |
| D6 | Enlarge the icon picker in the 1440p UI mod? | 5.1 | any time |
| D7 | What to do when RBM's index range or counters change? | Maintenance | when it happens |
