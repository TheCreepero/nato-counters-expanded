# NATO Counters Expanded - Agent Rules

Shared rules for every mod in this tree (file encodings, build commands, engine knowledge, git) are in the Modding Manager's `../../GEMINI.md`; Claude Code loads it by itself, Antigravity reads it first.

## What this mod is
- Division counter icons appended after RBM's GFX Overhaul: an expansion of RBM, never a replacement, for the owner's own game. Its content, `gfx/` and `interface/`, is all generated. `README.md` is for people, `ROADMAP.md` holds the planned work and the owner's pending decisions, `docs/counter-pipeline.md` the full pipeline rules.
- Local only, never published (owner, 2026-10-15): the icon picker stops at index 1023 [LIM-001] [LIM-002], so the mod needs the picker patched on this machine with the Manager's `Scripts\Executable\Set-HoiIconPickerLimit.ps1`. Do not run `-PublishSteam`, `Publish-Mod.ps1` or the `hoi4-mod-release` skill for it; its `steamWorkshopId` stays empty.

## Mod invariants
- Never ship a file at a path RBM or vanilla uses, define a sprite other than `GFX_div_templ_<1080 or higher>_large` and `_small`, or use `replace_path` (`tests/Counters.Tests.ps1`).
- Indices start at 1080, where RBM ends; a gap would hide every icon after it [LIM-002]. Indices are permanent [ICON-002]: never remove, rename or reorder a symbol key, edit `assets/counters/index_manifest.json` by hand or pass `--renumber`.
- Generated files are never hand-edited: change `tools/counters/symbols.py` and run `python tools/generate_counters.py`, which refuses a symbol below 0.80 against its RBM reference, a lookalike of an RBM counter, or an index collision (pipeline section 5.3).
- RBM's glyph is the style authority, not the NATO standard: copy the glyph RBM draws for the branch (`python tools/check_references.py`). A branch RBM has no icon for is drawn in `tools/counters/proposals.py` and shown to the user on the design sheet first.
- After a game update run `Set-HoiIconPickerLimit.ps1 -Status` and patch again. A build made without RBM installed is unverified and is reported as such.

## Commands beyond build.ps1
- `python tools/generate_counters.py`, `python tools/check_references.py --list | --show <key>`, `python tools/design_sheet.py` (`--text` for the glyphs of the text primitive), `python tools/check_references.py --text <TEXT> --reference <Name>`, `python tools/extract_plates.py` (only when RBM changes its plates); packages with `pip install -r tools/requirements.txt`.
- In-game check without the launcher: the 1440p mod's harness, `..\hoi4-1440p-ui-mod\tools\GameHarness.ps1` (pipeline section 5.7); the launcher file must point at this folder (`build.ps1 -DevLink`).

## Read when
| Task | Read |
|---|---|
| Choosing what to work on; adding or renumbering symbols; after a game or RBM update | `ROADMAP.md` |
| Adding a symbol | `docs/counter-pipeline.md` sections 5.2 to 5.4 |
| Setup and commands for people | `README.md` |

## Engine Knowledge
- Engine facts live in the Modding Manager's register, reached through the user-level `hoi4-modding-knowledge` skill: search it before a new kind of file and before asking for a game launch, cite ids here, never write a fact into this repository.
- Topics this mod leans on: `division-icons`, `engine-limits`, `mods/rbm`, `gui-sprites-and-fonts`, `loading-and-overrides`.
- `tests/Knowledge.Tests.ps1` runs the register's audit for this repository; it is a copy the Manager keeps current.
