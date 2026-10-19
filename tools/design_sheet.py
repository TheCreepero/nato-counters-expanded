import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from counters import rbm, reference
from counters.canvas import CX, CY, GLYPHS, W, H
from counters.layout import ECHELONS, LARGE, PALETTE_PATH, REPO_ROOT, SMALL, plate_path
from counters.proposals import PROPOSALS
from counters.symbols import SYMBOLS, Symbol
from generate_counters import PREVIEW_BACKGROUND, PREVIEW_SCALE, compose, render_symbol

DESIGN_SHEET_PATH = REPO_ROOT / "artifacts" / "design_sheet.png"
TEXT_SHEET_PATH = REPO_ROOT / "artifacts" / "text_sheet.png"
TEXT_SHEET_COLUMNS = 13
RBM_MP_OFFSET = (0.5, 0.75)
SHEET_COLOURS = ("white", "black", "forest", "mountain", "marine", "airborne")
LABEL_WIDTH = 300
GAP = 24


def counter(symbol, size, palette, echelon="div", colour="white"):
    plate = np.asarray(Image.open(plate_path(size, colour, echelon)).convert("RGBA"))
    return compose(plate, np.array(palette[colour]["ink"], dtype=np.float64), render_symbol(symbol, size))


def text_symbol(text, offset=(0.0, 0.0)):
    return Symbol(f"text_{text}", text, None, lambda pen: pen.text(text, CX + offset[0], CY + offset[1]))


def militia_mark(pen):
    for start_x, start_y, end_x, end_y in ((0, 0, 14.0, 7.2), (W, 0, W - 14.0, 7.2), (0, H, 14.0, H - 7.2), (W, H, W - 14.0, H - 7.2)):
        pen.line([(start_x, start_y), (end_x, end_y)])
    pen.text("M", CX, CY + RBM_MP_OFFSET[1])


def write_text_sheet(rbm_dir, palette):
    """Every glyph of the text primitive at both sizes, after RBM's own letters and this mod's copies of them."""
    rows = [("RBM: Military Police, Militia; this mod: MP, Militia",
             [(rbm.template_counter(rbm_dir, "Military Police", LARGE)), rbm.template_counter(rbm_dir, "Militia", LARGE),
              counter(text_symbol("MP", RBM_MP_OFFSET), LARGE, palette), counter(Symbol("militia", "M", None, militia_mark), LARGE, palette),
              rbm.template_counter(rbm_dir, "Military Police", SMALL), rbm.template_counter(rbm_dir, "Militia", SMALL),
              counter(text_symbol("MP", RBM_MP_OFFSET), SMALL, palette), counter(Symbol("militia", "M", None, militia_mark), SMALL, palette)])]
    characters = [character for character in GLYPHS if character != " "]
    for first in range(0, len(characters), TEXT_SHEET_COLUMNS):
        group = characters[first:first + TEXT_SHEET_COLUMNS]
        for size, size_name in ((LARGE, "designer"), (SMALL, "map")):
            rows.append((f"{group[0]} to {group[-1]} ({size_name})", [counter(text_symbol(character), size, palette) for character in group]))
    rows.append(("pairs (designer)", [counter(text_symbol(pair), LARGE, palette) for pair in ("HQ", "MP", "AA", "AT", "88", "CB")]))
    rows.append(("pairs (map)", [counter(text_symbol(pair), SMALL, palette) for pair in ("HQ", "MP", "AA", "AT", "88", "CB")]))

    cell_width = LARGE.width * PREVIEW_SCALE + 6
    cell_height = LARGE.height * PREVIEW_SCALE + 6
    sheet = Image.new("RGBA", (LABEL_WIDTH + TEXT_SHEET_COLUMNS * cell_width, len(rows) * cell_height), PREVIEW_BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    for row, (label, cells) in enumerate(rows):
        draw.multiline_text((6, row * cell_height + 8), label.replace("; ", ";\n"), fill=(255, 255, 255, 255))
        for column, pixels in enumerate(cells):
            image = Image.fromarray(pixels, "RGBA")
            image = image.resize((image.width * PREVIEW_SCALE, image.height * PREVIEW_SCALE), Image.NEAREST)
            sheet.alpha_composite(image, (LABEL_WIDTH + column * cell_width + 3, row * cell_height + 3))
    TEXT_SHEET_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(TEXT_SHEET_PATH)
    print(f"Glyphs: {len(characters)}")
    print(f"Text sheet: {TEXT_SHEET_PATH.relative_to(REPO_ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="Render the proposed symbols that are not in SYMBOLS yet, for the owner's approval.")
    parser.add_argument("--rbm-dir", type=Path, help="Folder of the installed RBM's GFX Overhaul mod.")
    parser.add_argument("--text", action="store_true", help="Render every glyph of the text primitive instead, to artifacts/text_sheet.png.")
    arguments = parser.parse_args()

    rbm_dir = arguments.rbm_dir or rbm.find_rbm_install()
    if rbm_dir is None or not rbm_dir.is_dir():
        sys.exit("RBM's GFX Overhaul was not found. Pass --rbm-dir <folder>.")
    palette = json.loads(PALETTE_PATH.read_text(encoding="utf-8"))
    if arguments.text:
        write_text_sheet(rbm_dir, palette)
        return
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
