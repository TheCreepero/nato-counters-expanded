import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from counters import dds, rbm, reference
from counters.canvas import Pen
from counters.layout import (COLOURS, COMPARISON_PATH, COUNTERS_DIR, ECHELONS, FILE_PREFIX, FIRST_INDEX, GFX_PATH, LARGE,
                             MANIFEST_PATH, PALETTE_PATH, PREVIEW_PATH, REPO_ROOT, SHIPPED_VARIANTS, SIZES, SMALL,
                             counter_file_name, counter_key, plate_path)
from counters.symbols import SYMBOLS

PREVIEW_SCALE = 3
PREVIEW_LABEL_WIDTH = 170
PREVIEW_BACKGROUND = (60, 70, 60, 255)
COMPARISON_SCALE = 5


def check_against_rbm(rbm_dir):
    if rbm_dir is None or not rbm_dir.is_dir():
        print("WARNING: RBM's GFX Overhaul was not found, so the symbols were NOT compared with its icons.")
        print("         Install it or pass --rbm-dir before trusting this build.")
        return None
    rows, problems = reference.check_symbols(rbm_dir, SYMBOLS)
    if problems:
        sys.exit("Nothing was written.\n" + "\n".join(problems) + "\nRun tools/check_references.py for the full report.")
    return rows


def write_comparison(rbm_dir, rows, counters):
    cell_width = SMALL.width * COMPARISON_SCALE + 10
    cell_height = SMALL.height * COMPARISON_SCALE + 10
    label_width = 330
    sheet = Image.new("RGBA", (label_width + 2 * cell_width, len(rows) * cell_height), PREVIEW_BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    for row, (symbol, score, _closest_name, _closest_score) in enumerate(rows):
        label = f"{symbol.name}  |  RBM: {symbol.reference or 'no reference'}"
        if score is not None:
            label += f"  |  match {score:.2f}"
        draw.text((6, row * cell_height + cell_height // 2 - 6), label, fill=(255, 255, 255, 255))
        echelon, colour = SHIPPED_VARIANTS[0]
        cells = [counters[(symbol.key, echelon, colour, SMALL.name)]]
        if symbol.reference is not None:
            cells.insert(0, rbm.battalion_nato_frame(rbm_dir, symbol.reference))
        for column, pixels in enumerate(cells):
            image = Image.fromarray(pixels, "RGBA")
            image = image.resize((image.width * COMPARISON_SCALE, image.height * COMPARISON_SCALE), Image.NEAREST)
            sheet.alpha_composite(image, (label_width + column * cell_width + 5, row * cell_height + 5))
    COMPARISON_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(COMPARISON_PATH)


def load_manifest(renumber):
    if renumber or not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["counters"]


def assign_indices(manifest):
    expected_keys = [counter_key(symbol.key, echelon, colour) for symbol in SYMBOLS for echelon, colour in SHIPPED_VARIANTS]
    retired = sorted(set(manifest) - set(expected_keys))
    if retired:
        sys.exit(
            f"{len(retired)} counters in {MANIFEST_PATH.name} have no symbol any more (first: {retired[0]}). "
            "Removing a symbol leaves a gap in the icon indices. Restore the symbol, or pass --renumber "
            "if this mod has not been published yet."
        )
    next_index = max(manifest.values(), default=FIRST_INDEX - 1) + 1
    for key in expected_keys:
        if key not in manifest:
            manifest[key] = next_index
            next_index += 1
    indices = sorted(manifest.values())
    if indices != list(range(FIRST_INDEX, FIRST_INDEX + len(indices))):
        sys.exit(f"{MANIFEST_PATH.name} does not hold one unbroken index range starting at {FIRST_INDEX}: the picker stops at the first gap.")
    return manifest


def compose(plate, ink, coverage):
    counter = plate.astype(np.float64)
    blend = coverage[:, :, None]
    counter[:, :, :3] = counter[:, :, :3] * (1 - blend) + ink * blend
    return np.clip(np.rint(counter), 0, 255).astype(np.uint8)


def render_symbol(symbol, size):
    pen = Pen(size)
    symbol.draw(pen)
    return pen.coverage()


def remove_stale_files(written):
    removed = 0
    for size in SIZES:
        for path in (COUNTERS_DIR / size.folder).glob(f"{FILE_PREFIX}.*.dds"):
            if path not in written:
                path.unlink()
                removed += 1
    return removed


def write_gfx(manifest):
    ordered = sorted(manifest.items(), key=lambda item: item[1])
    lines = ["spriteTypes = {", ""]
    for size in SIZES:
        for key, index in ordered:
            symbol_key, echelon, colour = key.split(".")
            texture = f"gfx/interface/counters/{size.folder}/{counter_file_name(symbol_key, echelon, colour, size)}"
            lines.append(f'\tspriteType = {{ name = "GFX_div_templ_{index}_{size.name}" textureFile = "{texture}" }}')
        lines.append("")
    lines.append("}")
    GFX_PATH.parent.mkdir(parents=True, exist_ok=True)
    GFX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\r\n")


def write_manifest(manifest):
    ordered = dict(sorted(manifest.items(), key=lambda item: item[1]))
    MANIFEST_PATH.write_text(json.dumps({"counters": ordered}, indent=4) + "\n", encoding="utf-8", newline="\r\n")


def write_preview(counters):
    cell_width = LARGE.width * PREVIEW_SCALE + 6
    cell_height = LARGE.height * PREVIEW_SCALE + 6
    columns = len(COLOURS) + len(ECHELONS)
    sheet = Image.new("RGBA", (PREVIEW_LABEL_WIDTH + columns * cell_width, len(SYMBOLS) * cell_height), PREVIEW_BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    for row, symbol in enumerate(SYMBOLS):
        draw.text((6, row * cell_height + cell_height // 2 - 6), symbol.name, fill=(255, 255, 255, 255))
        cells = [counters[(symbol.key, "div", colour, LARGE.name)] for colour in COLOURS]
        cells += [counters[(symbol.key, echelon, "white", SMALL.name)] for echelon in ECHELONS]
        for column, pixels in enumerate(cells):
            image = Image.fromarray(pixels, "RGBA")
            image = image.resize((image.width * PREVIEW_SCALE, image.height * PREVIEW_SCALE), Image.NEAREST)
            sheet.alpha_composite(image, (PREVIEW_LABEL_WIDTH + column * cell_width + 3, row * cell_height + 3))
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(PREVIEW_PATH)


def main():
    parser = argparse.ArgumentParser(description="Render every counter, the sprite definitions and a preview sheet.")
    parser.add_argument("--renumber", action="store_true", help="Discard the saved icon indices. Only safe before the mod is published.")
    parser.add_argument("--rbm-dir", type=Path, help="Folder of the installed RBM's GFX Overhaul mod.")
    parser.add_argument("--game-dir", type=Path, help="Folder of the installed game, for the check that no icon index is already declared.")
    arguments = parser.parse_args()

    symbol_keys = [symbol.key for symbol in SYMBOLS]
    if len(set(symbol_keys)) != len(symbol_keys):
        sys.exit("Two symbols share a key in symbols.py.")
    if not PALETTE_PATH.exists():
        sys.exit("Plates are missing. Run tools/extract_plates.py first.")

    rbm_dir = arguments.rbm_dir or rbm.find_rbm_install()
    reference_rows = check_against_rbm(rbm_dir)

    palette = json.loads(PALETTE_PATH.read_text(encoding="utf-8"))
    manifest = assign_indices(load_manifest(arguments.renumber))
    game_dir = arguments.game_dir or rbm.find_game_install()
    index_problems, unverified = reference.check_indices(manifest, rbm_dir, game_dir)
    if index_problems:
        sys.exit("Nothing was written.\n" + "\n".join(index_problems))
    for label in unverified:
        print(f"WARNING: {label} was not found, so the icon indices were NOT checked against its sprite declarations.")

    counters = {}
    written = set()
    for size in SIZES:
        plates = {(echelon, colour): np.asarray(Image.open(plate_path(size, colour, echelon)).convert("RGBA"))
                  for echelon, colour in SHIPPED_VARIANTS}
        for symbol in SYMBOLS:
            coverage = render_symbol(symbol, size)
            for echelon, colour in SHIPPED_VARIANTS:
                ink = np.array(palette[colour]["ink"], dtype=np.float64)
                pixels = compose(plates[(echelon, colour)], ink, coverage)
                target = COUNTERS_DIR / size.folder / counter_file_name(symbol.key, echelon, colour, size)
                dds.write_rgba(target, pixels)
                written.add(target)
                counters[(symbol.key, echelon, colour, size.name)] = pixels

    removed = remove_stale_files(written)
    write_gfx(manifest)
    write_manifest(manifest)
    write_preview(counters)

    indices = sorted(manifest.values())
    print(f"Symbols: {len(SYMBOLS)}   counters: {len(manifest)}   icon indices: {indices[0]}-{indices[-1]}")
    print(f"Wrote {len(written)} DDS files, removed {removed} stale files")
    print(f"Sprites: {GFX_PATH.relative_to(REPO_ROOT)}")
    print(f"Preview: {PREVIEW_PATH.relative_to(REPO_ROOT)}")
    if reference_rows is not None:
        write_comparison(rbm_dir, reference_rows, counters)
        scores = [score for _symbol, score, _name, _closest in reference_rows if score is not None]
        unreferenced = len(reference_rows) - len(scores)
        lowest = f"{min(scores):.2f}" if scores else "n/a"
        print(f"RBM check: passed, lowest match {lowest}, {unreferenced} symbols without a reference")
        print(f"Comparison: {COMPARISON_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
