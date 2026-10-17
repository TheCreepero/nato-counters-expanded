import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from counters import rbm, reference
from counters.layout import ECHELONS, LARGE, PALETTE_PATH, REPO_ROOT, SMALL, plate_path
from counters.proposals import PROPOSALS
from counters.symbols import SYMBOLS
from generate_counters import PREVIEW_BACKGROUND, PREVIEW_SCALE, compose, render_symbol

DESIGN_SHEET_PATH = REPO_ROOT / "artifacts" / "design_sheet.png"
SHEET_COLOURS = ("white", "black", "forest", "mountain", "marine", "airborne")
LABEL_WIDTH = 300
GAP = 24


def counter(symbol, size, palette, echelon="div", colour="white"):
    plate = np.asarray(Image.open(plate_path(size, colour, echelon)).convert("RGBA"))
    return compose(plate, np.array(palette[colour]["ink"], dtype=np.float64), render_symbol(symbol, size))


def main():
    parser = argparse.ArgumentParser(description="Render the proposed symbols that are not in SYMBOLS yet, for the owner's approval.")
    parser.add_argument("--rbm-dir", type=Path, help="Folder of the installed RBM's GFX Overhaul mod.")
    arguments = parser.parse_args()

    rbm_dir = arguments.rbm_dir or rbm.find_rbm_install()
    if rbm_dir is None or not rbm_dir.is_dir():
        sys.exit("RBM's GFX Overhaul was not found. Pass --rbm-dir <folder>.")
    palette = json.loads(PALETTE_PATH.read_text(encoding="utf-8"))
    shipped = {symbol.key: symbol for symbol in SYMBOLS}
    existing = {name: reference.coverage_from_counter(rbm.template_counter(rbm_dir, name, SMALL)) for name in rbm.RBM_TEMPLATE_SYMBOLS}

    cell_width = LARGE.width * PREVIEW_SCALE + 6
    cell_height = LARGE.height * PREVIEW_SCALE + 6
    columns = 2 + len(SHEET_COLOURS) + len(ECHELONS)
    sheet = Image.new("RGBA", (LABEL_WIDTH + columns * cell_width + 2 * GAP, (len(PROPOSALS) + 1) * cell_height), PREVIEW_BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    headings = ["RBM beside", "this mod's base"] + list(SHEET_COLOURS) + [f"{echelon} (map)" for echelon in ECHELONS]

    def left_of(column):
        return LABEL_WIDTH + column * cell_width + (GAP if column >= 1 else 0) + (GAP if column >= 2 else 0)

    for column, heading in enumerate(headings):
        draw.text((left_of(column) + 3, cell_height // 2), heading, fill=(255, 255, 255, 255))

    problems = []
    for row, proposal in enumerate(PROPOSALS, start=1):
        symbol = proposal.symbol
        closest_name, closest_score = max(((name, reference.match_score(reference.symbol_coverage(symbol), coverage))
                                           for name, coverage in existing.items()), key=lambda item: item[1])
        if closest_score >= reference.DUPLICATE_THRESHOLD:
            problems.append(f"{symbol.key}: duplicates RBM's own '{closest_name}' counter (match {closest_score:.2f}).")
        label = f"{symbol.name}\nno RBM reference\nclosest RBM counter: {closest_name} ({closest_score:.2f})"
        draw.multiline_text((6, row * cell_height + 8), label, fill=(255, 255, 255, 255))

        cells = [rbm.template_counter(rbm_dir, proposal.beside, LARGE), counter(shipped[proposal.base_key], LARGE, palette)]
        cells += [counter(symbol, LARGE, palette, colour=colour) for colour in SHEET_COLOURS]
        cells += [counter(symbol, SMALL, palette, echelon=echelon) for echelon in ECHELONS]
        for column, pixels in enumerate(cells):
            image = Image.fromarray(pixels, "RGBA")
            image = image.resize((image.width * PREVIEW_SCALE, image.height * PREVIEW_SCALE), Image.NEAREST)
            sheet.alpha_composite(image, (left_of(column) + 3, row * cell_height + 3))

    DESIGN_SHEET_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(DESIGN_SHEET_PATH)
    print(f"Proposals: {len(PROPOSALS)}")
    print(f"Design sheet: {DESIGN_SHEET_PATH.relative_to(REPO_ROOT)}")
    if problems:
        print("\n".join(problems))


if __name__ == "__main__":
    main()
